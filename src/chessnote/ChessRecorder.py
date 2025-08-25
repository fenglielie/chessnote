import copy
from collections import deque

from .utils import get_rotate_flag, logger
from .utils import Types as T
from .ChessState import ChessState
from .ChessBoardRenderer import ChessBoardRenderer
from .ChessParser import ChessParser
from .ChessChecker import ChessChecker


class ChessNode:
    """
    A node containing a chess state and optional metadata.
    """

    def __init__(
        self,
        state: ChessState,
        trace: T.Arrow | None,
        extra_info: dict[str, str] | None,
    ):
        self.state = state.deepcopy()
        self.trace = trace
        self.extra_info = extra_info or {}

    def __repr__(self):
        trace_msg = f"{self.trace[0]} -> {self.trace[1]}" if self.trace else ""
        desc_msg = (
            f"desc={self.extra_info.get('desc', '')} "
            f"color={self.extra_info.get('color', '')}"
        )

        return f"{trace_msg} {desc_msg}\n{self.state}"


class ChessNodeDeque:
    """
    Queue for storing ChessNode objects.
    """

    def __init__(
        self,
        state: ChessState,
        trace: T.Arrow | None,
        extra_info: dict[str, str] | None,
    ):
        self._queue = deque([ChessNode(state, trace, extra_info)])

    def append(
        self,
        state: ChessState,
        trace: T.Arrow | None,
        extra_info: dict[str, str] | None,
    ):
        self._queue.append(ChessNode(state, trace, extra_info))

    def pop(self):
        """
        Pop the last node (cannot remove the initial state).
        """
        if len(self._queue) > 1:
            return self._queue.pop()
        return None

    def __len__(self):
        return len(self._queue)

    def __iter__(self):
        return iter(self._queue)

    def deepcopy(self) -> "ChessNodeDeque":
        new_history = ChessNodeDeque(self._queue[0].state, None, None)
        new_history._queue = deque(
            ChessNode(node.state, node.trace, node.extra_info) for node in self._queue
        )
        return new_history

    def __repr__(self):
        lines = []
        for i, node in enumerate(self._queue):
            lines.append(f"state {i}: {node.__repr__()}")
        return "\n".join(lines)


class ChessRecorder:
    """
    Recorder for managing chess state history.
    """

    def __init__(
        self,
        state: ChessState | None = None,
        rotate_flag: bool | None = None,
    ):
        if state is None:
            state = ChessState(rotate=rotate_flag)

        self._history = ChessNodeDeque(state, None, None)
        self._rotate_flag = rotate_flag or get_rotate_flag()
        self._checkpoints: dict[str, int] = {}

    def rotate(self) -> "ChessRecorder":
        """
        Toggle the rotation flag.
        """
        self._rotate_flag = not self._rotate_flag
        return self

    def move(
        self, start: T.Pos, end: T.Pos, desc: str | None = None
    ) -> "ChessRecorder":
        """
        Move a piece by start and end coordinates.
        """
        try:
            ChessChecker.check_move(
                self._history._queue[-1].state,
                start,
                end,
                rotate_flag=self._rotate_flag,
            )
        except Exception as e:
            state_snapshot = self._history._queue[-1].state
            piece = state_snapshot.get(start, None)
            extra_msg = (
                f"Invalid move detected: piece={piece}, start={start}, end={end}, "
                f"rotate_flag={self._rotate_flag}, desc={desc}\n"
                f"Current state: \n{state_snapshot}"
            )
            raise ValueError(extra_msg) from e

        # check color
        color = "red" if self._history._queue[-1].state[start].isupper() else "black"
        pre_color = self._history._queue[-1].extra_info.get("color", "")
        if pre_color == color:
            raise ValueError(
                "The color of the current player is the same as the previous player."
            )

        new_state = self._history._queue[-1].state.deepcopy()
        new_state.move(start, end)

        logger.debug(f"[{len(self._history) - 1}] trace: {start} -> {end} {desc=}")

        extra_info = {"color": color}
        if desc:
            extra_info["desc"] = desc

        self._history.append(new_state, (start, end), extra_info=extra_info)
        return self

    def exec(
        self, cmds: str | list[str] | tuple[str], strict_flag: bool = False
    ) -> "ChessRecorder":
        """
        Update state using Chinese chess notation.
        """
        if isinstance(cmds, str):
            cmds = ChessParser.normalize_cmds(cmds)
        elif isinstance(cmds, list) or isinstance(cmds, tuple):
            cmds = list(cmds)
        else:
            raise TypeError(f"Unsupported cmds type: {type(cmds).__name__}")

        for cmd in filter(None, cmds):
            try:
                start, end = ChessParser.parse_cmd(
                    self._history._queue[-1].state,
                    cmd,
                    rotate_flag=self._rotate_flag,
                    strict_flag=strict_flag,
                )
            except ValueError as e:
                state_snapshot = self._history._queue[-1].state
                extra_msg = (
                    f"Invalid cmd detected: {cmd=} ({strict_flag=})\n"
                    f"Current state: \n{state_snapshot}"
                )
                raise ValueError(extra_msg) from e

            self.move(start, end, desc=cmd)
        return self

    def set_checkpoint(self, name: str) -> None:
        """Save a checkpoint with a name."""
        self._checkpoints[name] = len(self._history)

    def rollback_to_checkpoint(self, name: str) -> None:
        """Rollback history to a checkpoint."""
        if name not in self._checkpoints:
            raise KeyError(f"Checkpoint '{name}' not found")
        target_len = self._checkpoints[name]
        while len(self._history) > target_len:
            self._history.pop()

    def rollback(self, steps: int) -> None:
        """Rollback a given number of steps."""
        if steps < 0:
            raise ValueError(f"Steps must be non-negative, but got {steps}")
        for _ in range(steps):
            self._history.pop()

    def draw(
        self,
        renderer: ChessBoardRenderer | None = None,
        highlight_last_move: bool = True,
        **kwargs,
    ) -> None:
        """
        Render the current board state.
        """
        renderer = renderer or ChessBoardRenderer(rotate_flag=self._rotate_flag)
        highlight_pieces = None
        if highlight_last_move:
            last_move = self._history._queue[-1].trace
            if last_move:
                highlight_pieces = [last_move[0], last_move[1]]

        return renderer.draw(
            self._history._queue[-1].state.deepcopy(),
            highlight_pieces=highlight_pieces,
            **kwargs,
        )

    def animate(
        self,
        renderer: ChessBoardRenderer | None = None,
        duration: int | None = None,
        highlight_moves: bool = True,
        **kwargs,
    ) -> None:
        """
        Animate the sequence of moves.
        """
        renderer = renderer or ChessBoardRenderer(rotate_flag=self._rotate_flag)
        states = [node.state.deepcopy() for node in self._history]
        movements = [node.trace for node in self._history if node.trace]

        if duration is None:
            if highlight_moves:
                duration = 500
            else:
                duration = 1000

        if not highlight_moves:
            return renderer.animate(states, duration=duration, **kwargs)

        highlight_pieces_seq = []
        for move in movements:
            highlight_pieces_seq.append([move[0]])
            highlight_pieces_seq.append([move[0], move[1]])

        active_states = []
        for i in range(1, len(states)):
            active_states.append(states[i - 1])
            active_states.append(states[i])

        return renderer.animate(
            active_states,
            highlight_pieces_seq=highlight_pieces_seq,
            duration=duration,
            **kwargs,
        )

    def deepcopy(self) -> "ChessRecorder":
        """
        Return a deep copy of the recorder.
        """
        new_rec = ChessRecorder(
            state=self._history._queue[0].state,
            rotate_flag=self._rotate_flag,
        )
        new_rec._history = self._history.deepcopy()
        new_rec._checkpoints = copy.deepcopy(self._checkpoints)
        return new_rec

    def __repr__(self):
        return (
            f"ChessRecorder: {len(self._history)} states, rotate_flag={self._rotate_flag}\n"
            + self._history.__repr__()
        )

    def last(self) -> ChessState:
        return self._history._queue[-1].state.deepcopy()

    def derive(self) -> "ChessRecorder":
        return ChessRecorder(self.last(), self._rotate_flag)

    def dryrun(
        self,
        cmds: list[str],
        *,
        rotate_flag: bool | None = None,
        strict_flag: bool = False,
    ) -> None:
        arrows = []
        for cmd in cmds:
            arrows.append(
                ChessParser.parse_cmd(
                    self.last(), cmd, rotate_flag=rotate_flag, strict_flag=strict_flag
                )
            )

        return self.draw(arrows=arrows, highlight_last_move=False)
