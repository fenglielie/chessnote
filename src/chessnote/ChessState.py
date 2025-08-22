import copy
import json
import ast
from collections.abc import MutableMapping

from .utils import get_rotate_flag
from .utils import Types as T


class ChessState(MutableMapping):
    """
    Store Xiangqi (Chinese Chess) board state using first-quadrant coordinates:
    bottom-left (0,0), x-axis to the right, y-axis upward.
    Exposes a dictionary-like interface, but keys (positions) and values (pieces) are validated.
    Internal representation uses uppercase/lowercase letters; no Chinese characters.
    """

    _ROWS_NUM, _COLS_NUM = 10, 9
    _VALID_PIECES = "RrHhEeAaCcPpKk"

    _DEFALUT_STATE = {
        # red
        (0, 0): "R",
        (1, 0): "H",
        (2, 0): "E",
        (3, 0): "A",
        (4, 0): "K",
        (5, 0): "A",
        (6, 0): "E",
        (7, 0): "H",
        (8, 0): "R",
        (1, 2): "C",
        (7, 2): "C",
        (0, 3): "P",
        (2, 3): "P",
        (4, 3): "P",
        (6, 3): "P",
        (8, 3): "P",
        # black
        (0, 6): "p",
        (2, 6): "p",
        (4, 6): "p",
        (6, 6): "p",
        (8, 6): "p",
        (1, 7): "c",
        (7, 7): "c",
        (0, 9): "r",
        (1, 9): "h",
        (2, 9): "e",
        (3, 9): "a",
        (4, 9): "k",
        (5, 9): "a",
        (6, 9): "e",
        (7, 9): "h",
        (8, 9): "r",
    }

    def __init__(self, empty: bool = False, rotate: bool | None = None):
        self._pieces: dict[T.Pos, str] = {}
        if not empty:
            self._pieces = copy.deepcopy(ChessState._DEFALUT_STATE)

        if rotate is None:
            if get_rotate_flag():
                self = self.rotate_pieces()
        else:
            if rotate:
                self = self.rotate_pieces()

    def _check_key(self, key: T.Pos) -> None:
        if not (
            isinstance(key, tuple)
            and len(key) == 2
            and isinstance(key[0], int)
            and isinstance(key[1], int)
        ):
            raise KeyError(f"Invalid key: {key=} must be (x,y) tuple of ints")

        x, y = key
        if not (0 <= x < ChessState._COLS_NUM and 0 <= y < ChessState._ROWS_NUM):
            raise KeyError(f"Invalid key: {key=}, out of board range")

    def _check_piece(self, piece: str) -> None:
        if not isinstance(piece, str):
            raise ValueError(
                f"Piece value must be a string, but type is {type(piece).__name__}"
            )

        if piece not in ChessState._VALID_PIECES:
            raise ValueError(
                f"Invalid piece: {piece=!r} must be in {ChessState._VALID_PIECES}"
            )

    def __getitem__(self, key: T.Pos) -> str:
        self._check_key(key)
        return self._pieces[key]

    def __setitem__(self, key: T.Pos, value: str) -> None:
        self._check_key(key)
        self._check_piece(value)
        self._pieces[key] = value

    def __delitem__(self, key: T.Pos) -> None:
        self._check_key(key)
        del self._pieces[key]

    def __iter__(self):
        return iter(self._pieces)

    def __len__(self):
        return len(self._pieces)

    def __str__(self) -> str:
        """
        ASCII board display
        """
        lines = []
        lines.append(" +-------------------+")
        for y in reversed(range(self._ROWS_NUM)):
            row_str = ""
            for x in range(self._COLS_NUM):
                piece = self._pieces.get((x, y), None)
                row_str += (piece if piece else ".") + " "
            lines.append(f"{y}| {row_str}|")
        lines.append(" +-------------------+")
        lines.append("   " + " ".join(str(c) for c in range(self._COLS_NUM)))
        return "\n".join(lines)

    def move(self, start: T.Pos, end: T.Pos) -> "ChessState":
        """
        Move a piece from start to end
        """
        if start not in self._pieces:
            raise ValueError(f"No piece at {start=}")
        self[end] = self[start]
        del self[start]
        return self

    def rotate_pieces(self) -> "ChessState":
        """
        Toggle the rotation flag.
        """
        new_pieces = {}
        for (x, y), piece in self._pieces.items():
            new_x, new_y = 8 - x, 9 - y
            new_pieces[(new_x, new_y)] = piece
        self._pieces = new_pieces
        return self

    def swap_pieces(self) -> "ChessState":
        """
        Swap piece colors
        """
        self._pieces = {pos: piece.swapcase() for pos, piece in self._pieces.items()}
        return self

    def deepcopy(self) -> "ChessState":
        new_state = ChessState(empty=True)
        new_state._pieces = copy.deepcopy(self._pieces)
        return new_state


class ChessStateIO:
    """
    Helper for saving/loading ChessState
    """

    @staticmethod
    def save_to_dict(state: "ChessState") -> dict[str, str]:
        """
        Convert to dict, serialize position keys as '(x,y)'
        """
        return {str(pos): piece for pos, piece in state._pieces.items()}

    @staticmethod
    def load_from_dict(data: dict[str, str]) -> "ChessState":
        """
        Load ChessState from dict
        """
        state = ChessState(empty=True)
        for key, piece in data.items():
            pos = ast.literal_eval(key)  # str "(0,1)" -> tuple (0,1)
            state[pos] = piece
        return state

    @staticmethod
    def save_to_json_file(state: "ChessState", filepath: str) -> None:
        """
        Save ChessState to JSON file
        """
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(ChessStateIO.save_to_dict(state), f, indent=2, ensure_ascii=False)

    @staticmethod
    def load_from_json_file(filepath: str) -> "ChessState":
        """
        Load ChessState from JSON file
        """
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return ChessStateIO.load_from_dict(data)
