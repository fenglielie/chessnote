from .utils import Types as T
from .ChessState import ChessState


class ChessChecker:
    """
    Move legality checker for Chinese Chess (Xiangqi).
    Provides piece-specific rule validation.
    """

    @staticmethod
    def check_move(
        cur_state: ChessState,
        start: T.Pos,
        end: T.Pos,
        rotate_flag: bool,
    ) -> bool:
        """
        Check whether a single move is legal by piece rules only.
        Return None if move is legal, otherwise raises ValueError.
        """

        # --- basic sanity checks ---
        if start not in cur_state:
            raise ValueError(f"No piece at start {start}")
        if start == end:
            raise ValueError("Start and end cannot be the same")

        piece = cur_state[start]

        # --- disallow capturing own piece ---
        if end in cur_state:
            target = cur_state[end]
            if (piece.isupper() and target.isupper()) or (
                piece.islower() and target.islower()
            ):
                raise ValueError(f"Cannot capture own piece at {end}")

        color = "red" if piece.isupper() else "black"
        # determine side
        if (color == "red" and not rotate_flag) or (color == "black" and rotate_flag):
            side = "down"
        else:
            side = "up"

        sx, sy = start
        ex, ey = end
        dx, dy = ex - sx, ey - sy

        if piece in ("R", "r"):  # Rook
            if not (dx == 0 or dy == 0):
                raise ValueError("Rook must move straight")
            if ChessChecker._count_between(cur_state, start, end) != 0:
                raise ValueError("Rook path blocked")

        elif piece in ("H", "h"):  # Knight
            if not ((abs(dx), abs(dy)) in [(1, 2), (2, 1)]):
                raise ValueError("Knight must move in 日-shape")
            block = (sx + dx // 2, sy) if abs(dx) == 2 else (sx, sy + dy // 2)
            if block in cur_state:
                raise ValueError("Knight's leg blocked")

        elif piece in ("E", "e"):  # Elephant
            if not (abs(dx), abs(dy)) == (2, 2):
                raise ValueError("Elephant must move 2 diagonally")
            eye = (sx + dx // 2, sy + dy // 2)
            if eye in cur_state:
                raise ValueError("Elephant's eye blocked")
            if not ChessChecker._check_in_side(end, color, rotate_flag):
                raise ValueError("Elephant cannot cross the river")

        elif piece in ("A", "a"):  # Advisor
            if not (abs(dx), abs(dy)) == (1, 1):
                raise ValueError("Advisor must move 1 diagonally")
            if not ChessChecker._check_in_palace(end, color, rotate_flag):
                raise ValueError("Advisor must stay inside palace")

        elif piece in ("K", "k"):  # King
            if not (abs(dx), abs(dy)) in ((1, 0), (0, 1)):
                raise ValueError("King must move 1 step orthogonally")
            if not ChessChecker._check_in_palace(end, color, rotate_flag):
                raise ValueError("King must stay inside palace")

        elif piece in ("C", "c"):  # Cannon
            if not (dx == 0 or dy == 0):
                raise ValueError("Cannon must move straight")
            cnt_between = ChessChecker._count_between(cur_state, start, end)
            if end in cur_state:
                if cnt_between != 1:
                    raise ValueError(
                        "Cannon must jump exactly one piece when capturing"
                    )
            else:
                if cnt_between != 0:
                    raise ValueError("Cannon path blocked")

        else:  # piece in ("P", "p")  # Pawn
            if not (abs(dx), abs(dy)) in ((1, 0), (0, 1)):
                raise ValueError("Pawn must move 1 step")

            # cannot move backward
            if (side == "up" and dy > 0) or (side == "down" and dy < 0):
                raise ValueError("Pawn cannot move backward")
            # before crossing river, only forward
            if ChessChecker._check_in_side(end, color, rotate_flag):
                if dx != 0:
                    raise ValueError("Pawn cannot move sideways before crossing river")

        return True

    @staticmethod
    def _count_between(cur_state: ChessState, start: T.Pos, end: T.Pos) -> int:
        """
        Count pieces between two points (must be aligned on row/col)
        """
        sx, sy = start
        ex, ey = end
        cnt = 0
        if sx == ex:  # vertical
            step = 1 if ey > sy else -1
            for y in range(sy + step, ey, step):
                if (sx, y) in cur_state:
                    cnt += 1
        elif sy == ey:  # horizontal
            step = 1 if ex > sx else -1
            for x in range(sx + step, ex, step):
                if (x, sy) in cur_state:
                    cnt += 1
        else:
            raise ValueError("Must be aligned on row/col")

        return cnt

    @staticmethod
    def _check_in_palace(pos: T.Pos, color: str, rotate_flag: bool) -> bool:
        """
        Check if position is inside palace (3x3 area)
        """
        if (color == "red" and not rotate_flag) or (color == "black" and rotate_flag):
            return 3 <= pos[0] <= 5 and 0 <= pos[1] <= 2
        else:
            return 3 <= pos[0] <= 5 and 7 <= pos[1] <= 9

    @staticmethod
    def _check_in_side(pos: T.Pos, color: str, rotate_flag: bool) -> bool:
        """
        Check if position is on player's own side of the river
        """
        if (color == "red" and not rotate_flag) or (color == "black" and rotate_flag):
            return pos[1] <= 4
        else:
            return pos[1] >= 5
