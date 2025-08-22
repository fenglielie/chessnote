import re

from .utils import get_rotate_flag

from .utils import Types as T
from .ChessState import ChessState


class ChessParser:
    @staticmethod
    def detect_color(cmd: str) -> str:
        """
        Detect move color by cmd string.
        Rules:
            - Red uses Chinese numerals.
            - Black uses Arabic numerals.
        """
        if re.search(r"\d", cmd):
            return "black"
        elif re.search(r"[一二三四五六七八九十]", cmd):
            return "red"
        else:
            raise ValueError(f"Cannot determine color: {cmd!r}")

    @staticmethod
    def detect_side(color: str, *, rotate_flag: bool) -> str:
        """
        Map color + rotate_flag to board side ('up' or 'down')
        """
        if not rotate_flag:
            return "down" if color == "red" else "up"
        return "down" if color == "black" else "up"

    @staticmethod
    def normalize_cmds(text: str) -> list[str]:
        """
        Normalize raw PGN text into cmd list, enforcing red/black alternation.
        """
        text = re.sub(r"\b\d+(\.{1,3}|[、:：])?", " ", text)
        parts = re.split(r"[\s,，、;；]+", text)
        cmds = [p.strip() for p in parts if p.strip()]
        if not cmds:
            return []

        expected_color = ChessParser.detect_color(cmds[0])

        checked: list[str] = []
        for cmd in cmds:
            color = ChessParser.detect_color(cmd)
            if color != expected_color:
                raise ValueError(
                    f"Alternation error: expected {expected_color}, got {color} ({cmd!r})"
                )
            checked.append(cmd)
            expected_color = "red" if expected_color == "black" else "black"

        return checked

    @staticmethod
    def parse_piece_char(piece_ch: str, *, color: str, strict_flag: bool) -> str:
        """
        Map Chinese piece character to internal symbol (R/H/E/A/K/C/P with case)
        """

        RED_PIECES = {
            "车": "R",
            "马": "H",
            "相": "E",
            "仕": "A",
            "帅": "K",
            "炮": "C",
            "兵": "P",
        }
        BLACK_PIECES = {
            "車": "r",
            "馬": "h",
            "象": "e",
            "士": "a",
            "将": "k",
            "砲": "c",
            "卒": "p",
        }

        if strict_flag:
            piece = (
                RED_PIECES.get(piece_ch)
                if color == "red"
                else BLACK_PIECES.get(piece_ch)
            )
            if not piece:
                raise ValueError(f"Invalid piece: {piece_ch} ({color=}) [strict]")
        else:
            piece = RED_PIECES.get(piece_ch, BLACK_PIECES.get(piece_ch))
            if not piece:
                raise ValueError(f"Invalid piece: {piece_ch} ({color=})")
            piece = piece.upper() if color == "red" else piece.lower()

        return piece

    @staticmethod
    def parse_col_idx(col_ch: str, *, color: str, side: str) -> int:
        """
        Parse column index from cmd token
        """
        CHINESE_IDX = {
            "一": 1,
            "二": 2,
            "三": 3,
            "四": 4,
            "五": 5,
            "六": 6,
            "七": 7,
            "八": 8,
            "九": 9,
        }

        if color == "red":
            if col_ch in CHINESE_IDX:
                col = CHINESE_IDX[col_ch] - 1
            else:
                raise ValueError(f"Red column must be Chinese numerals: {col_ch=}")
        else:
            if col_ch.isdigit():
                idx = int(col_ch) - 1
                if 0 <= idx <= 8:
                    col = idx
                else:
                    raise ValueError(f"Black column must be in 1–9: {col_ch=}")
            else:
                raise ValueError(f"Black column must be numeric: {col_ch=}")

        if side == "down":
            col = 8 - col  # Mirror for "down" side

        return col

    @staticmethod
    def parse_row_delta(delta_ch: str, *, color: str, side: str) -> int:
        """
        Parse row delta (forward/backward step size).
        """
        CHINESE_NUM = {
            "一": 1,
            "二": 2,
            "三": 3,
            "四": 4,
            "五": 5,
            "六": 6,
            "七": 7,
            "八": 8,
            "九": 9,
        }
        if color == "red":
            if delta_ch in CHINESE_NUM:
                delta = CHINESE_NUM[delta_ch]
            else:
                raise ValueError(f"Red step must be in Chinese numerals: {delta_ch=}")
        else:
            if delta_ch.isdigit():
                idx = int(delta_ch)
                if 0 <= idx <= 9:
                    delta = idx
                else:
                    raise ValueError(f"Black step must be in 1–9: {delta_ch=}")
            else:
                raise ValueError(f"Invalid black step: {delta_ch=}")

        if side == "up":
            delta = -delta

        return delta

    @staticmethod
    def parse_cmd(
        state: ChessState,
        cmd: str,
        *,
        rotate_flag: bool | None = None,
        strict_flag: bool = False,
    ) -> T.Arrow:
        """
        Parse Chinese cmd string into move coordinates.
        Returns:
            (from_pos, to_pos): both as (col, row).
        """
        HARD_MODE_KEYWORDS = ["前", "中", "后"]

        rotate_flag = rotate_flag or get_rotate_flag()

        # Build reverse map from state
        state_map: dict[str, list[tuple[int, int]]] = {}
        for (i, j), v in state.items():
            state_map.setdefault(v, []).append((i, j))

        # Extract tokens
        if cmd[0] in HARD_MODE_KEYWORDS:
            piece_ch, op_type, op_arg_ch = cmd[1], cmd[2], cmd[3]
        else:
            piece_ch, col_ch, op_type, op_arg_ch = (
                cmd[0],
                cmd[1],
                cmd[2],
                cmd[3],
            )

        color = ChessParser.detect_color(cmd)
        side = ChessParser.detect_side(color, rotate_flag=rotate_flag)

        piece = ChessParser.parse_piece_char(
            piece_ch, color=color, strict_flag=strict_flag
        )

        # Determine starting position
        if cmd[0] not in HARD_MODE_KEYWORDS:
            if piece not in state_map:
                raise ValueError(f"Source piece not found: {piece}")

            start_col = ChessParser.parse_col_idx(col_ch, color=color, side=side)
            start = next(((i, j) for i, j in state_map[piece] if i == start_col), None)

            if start is None:
                raise ValueError(f"Source piece not found: {piece} at {col_ch}")
        else:
            positions = list(state_map[piece])
            cols = {i for i, j in positions}
            if len(cols) > 1:
                raise ValueError(f"{piece} not in same column ({positions=})")

            if side == "down":
                positions.sort(key=lambda x: -x[1])
            else:
                positions.sort(key=lambda x: x[1])

            if cmd[0] == "前":
                if len(positions) < 2:
                    raise ValueError(f"'前' requires >=2 pieces ({cmd=})")
                start = positions[0]
            elif cmd[0] == "后":
                if len(positions) < 2:
                    raise ValueError(f"'后' requires >=2 pieces ({cmd=})")
                start = positions[-1]
            else:  # cmd[0] == "中"
                if len(positions) < 3:
                    raise ValueError(f"'中' requires >=3 pieces ({cmd=})")
                start = positions[1]

        # Determine ending position
        if piece.lower() in ("k", "r", "c", "p"):
            if op_type == "平":
                end = (
                    ChessParser.parse_col_idx(op_arg_ch, color=color, side=side),
                    start[1],
                )
            elif op_type == "进":
                end_row = start[1] + ChessParser.parse_row_delta(
                    op_arg_ch, color=color, side=side
                )
                if not (0 <= end_row <= 9):
                    raise ValueError(f"Row out of range: {end_row=}")
                end = (start[0], end_row)
            elif op_type == "退":
                end_row = start[1] - ChessParser.parse_row_delta(
                    op_arg_ch, color=color, side=side
                )
                if not (0 <= end_row <= 9):
                    raise ValueError(f"Row out of range: {end_row=}")
                end = (start[0], end_row)
            else:
                raise ValueError(f"Invalid operator {op_type} for {piece}")

        elif piece.lower() in ("a", "e"):  # Advisor / Elephant
            end_col = ChessParser.parse_col_idx(op_arg_ch, color=color, side=side)
            if piece.lower() == "a":
                delta_unit = "一" if color == "red" else "1"
            else:  # e
                delta_unit = "二" if color == "red" else "2"
            if op_type == "进":
                end_row = start[1] + ChessParser.parse_row_delta(
                    delta_unit, color=color, side=side
                )
            elif op_type == "退":
                end_row = start[1] - ChessParser.parse_row_delta(
                    delta_unit, color=color, side=side
                )
            else:
                raise ValueError(f"Invalid operator {op_type} for {piece}")
            end = (end_col, end_row)

        else:  # piece.lower() == "h"  # Horse
            end_col = ChessParser.parse_col_idx(op_arg_ch, color=color, side=side)
            if abs(end_col - start[0]) == 1:
                delta_unit = "二" if color == "red" else "2"
            elif abs(end_col - start[0]) == 2:
                delta_unit = "一" if color == "red" else "1"
            else:
                raise ValueError(f"Invalid horse move: {cmd} ({piece=})")

            if op_type == "进":
                end_row = start[1] + ChessParser.parse_row_delta(
                    delta_unit, color=color, side=side
                )
            elif op_type == "退":
                end_row = start[1] - ChessParser.parse_row_delta(
                    delta_unit, color=color, side=side
                )
            else:
                raise ValueError(f"Invalid operator {op_type} for {piece}")
            end = (end_col, end_row)

        return start, end
