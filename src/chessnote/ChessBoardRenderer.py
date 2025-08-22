from io import BytesIO
from PIL import Image
from IPython.display import display, Image as IPImage
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle
from matplotlib.lines import Line2D
import copy

from .utils import get_rotate_flag, logger
from .utils import Types as T
from .ChessState import ChessState


class ChessBoardRenderer:
    _DEFAULT_PIECE_CHINESE = {
        "R": "车",
        "H": "马",
        "E": "相",
        "A": "仕",
        "K": "帅",
        "C": "炮",
        "P": "兵",
        "r": "車",
        "h": "馬",
        "e": "象",
        "a": "士",
        "k": "将",
        "c": "砲",
        "p": "卒",
    }

    _DEFAULT_STYLE = {
        "board": {"grid_color": "brown", "grid_lw": 1.0, "palace_color": "brown"},
        "piece": {
            "facecolor": "lightyellow",
            "radius": 0.4,
            "font_size": 16,
            "circle_lw": 1.0,
        },
        "highlight": {"color": "red", "lw": 2},
        "arrow": {"color": "green", "lw": 2, "mutation_scale": 10},
        "figsize": (4, 5),
    }

    _BLACK_LABELS = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
    _RED_LABELS = ["一", "二", "三", "四", "五", "六", "七", "八", "九"]
    _MID_LABELS = ["楚 河", "汉 界"]

    def __init__(
        self,
        style: dict | None = None,
        piece_config: dict[str, str] | None = None,
        rotate_flag: bool | None = None,
    ):
        self._style = {k: copy.deepcopy(v) for k, v in self._DEFAULT_STYLE.items()}

        # update style
        if isinstance(style, dict):
            for layer, opts in style.items():
                if layer in self._style:
                    self._style[layer].update(opts)

        self._piece_config = copy.deepcopy(self._DEFAULT_PIECE_CHINESE)

        # update piece_config
        if piece_config is not None:
            self._piece_config.update(piece_config)

        self._rotate_flag = rotate_flag or get_rotate_flag()

    def rotate(self) -> "ChessBoardRenderer":
        """
        Toggle the rotation flag.
        """
        self._rotate_flag = not self._rotate_flag
        return self

    def draw(
        self,
        state: ChessState,
        highlight_pieces: T.SeqPos | None = None,
        arrows: T.SeqArrow | None = None,
        filename: str | None = None,
        return_fig: bool = False,
    ):
        """
        Draw a static chessboard with pieces, highlights, and arrows
        """

        fig, ax = plt.subplots(figsize=self._style.get("figsize", (6, 7)))
        ax.set_xlim(-0.5, 8.5)
        ax.set_ylim(-1, 10)
        ax.set_aspect("equal")
        ax.axis("off")

        self._draw_grid(ax)
        self._draw_labels(ax)
        self._draw_pieces(ax, state)

        if highlight_pieces is not None:
            self._draw_highlight(ax, highlight_pieces)

        if arrows is not None:
            self._draw_arrows(ax, arrows)

        if filename is not None:
            fig.savefig(filename)
            logger.info(f"Saved to {filename}")

        return (fig, ax) if return_fig else None

    def animate(
        self,
        states: list[ChessState],
        *,
        duration: int,
        highlight_pieces_seq: T.SeqSeqPos | None = None,
        arrows_seq: T.SeqSeqArrow | None = None,
        filename: str | None = None,
    ):
        """
        Animate a sequence of chessboard states
        """

        frames = []

        for i, state in enumerate(states):
            highlight_pieces = highlight_pieces_seq[i] if highlight_pieces_seq else None
            arrows = arrows_seq[i] if arrows_seq else None

            fig, _ = self.draw(
                state, highlight_pieces=highlight_pieces, arrows=arrows, return_fig=True
            )
            buf = BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight", pad_inches=0.2)
            buf.seek(0)
            img = Image.open(buf)
            frames.append(img.copy())
            plt.close(fig)

        if not frames:
            return

        if filename is not None:
            frames[0].save(
                filename,
                save_all=True,
                append_images=frames[1:],
                duration=duration,
                loop=0,
            )
            logger.info(f"Saved to {filename}")

        gif_buf = BytesIO()
        frames[0].save(
            gif_buf,
            format="GIF",
            save_all=True,
            append_images=frames[1:],
            duration=duration,
            loop=0,
        )
        gif_buf.seek(0)
        display(IPImage(data=gif_buf.getvalue()))

    def _draw_grid(self, ax):
        grid_style = {
            "color": self._style["board"]["grid_color"],
            "lw": self._style["board"]["grid_lw"],
            "zorder": 1,
        }
        bg = {
            "edgecolor": self._style["board"]["grid_color"],
            "lw": self._style["board"]["grid_lw"],
            "zorder": 0,
            "fill": False,
        }

        halfwidth = 0.1
        rect = Rectangle(
            (-halfwidth, -halfwidth), 8 + 2 * halfwidth, 9 + 2 * halfwidth, **bg
        )
        ax.add_patch(rect)

        ax.plot([0, 0], [0, 9], **grid_style)
        ax.plot([8, 8], [0, 9], **grid_style)
        for x in range(1, 8):
            ax.plot([x, x], [0, 4], **grid_style)
            ax.plot([x, x], [5, 9], **grid_style)
        for y in range(10):
            ax.plot([0, 8], [y, y], **grid_style)

        palace_coords = [
            [(3, 0), (5, 2)],
            [(5, 0), (3, 2)],
            [(3, 7), (5, 9)],
            [(5, 7), (3, 9)],
        ]
        for (x0, y0), (x1, y1) in palace_coords:
            ax.plot([x0, x1], [y0, y1], **grid_style)

    def _draw_pieces(self, ax, state):
        circle_style = {
            "facecolor": self._style["piece"]["facecolor"],
            "edgecolor": "black",
            "lw": self._style["piece"]["circle_lw"],
            "zorder": 2,
        }

        text_style = {
            "fontsize": self._style["piece"]["font_size"],
            "ha": "center",
            "va": "center",
            "weight": "bold",
            "zorder": 3,
        }

        for (x, y), piece in state.items():
            circle = Circle((x, y), self._style["piece"]["radius"], **circle_style)
            ax.add_patch(circle)

            name = self._piece_config.get(piece, "?")
            color = "red" if piece.isupper() else "black"
            ax.text(x, y, name, color=color, **text_style)

    def _draw_labels(self, ax):
        style = {"fontsize": self._style["piece"]["font_size"], "ha": "center"}

        if not self._rotate_flag:
            down_labels = ChessBoardRenderer._RED_LABELS[::-1]
            up_labels = ChessBoardRenderer._BLACK_LABELS
            mid_labels = ChessBoardRenderer._MID_LABELS
        else:
            down_labels = ChessBoardRenderer._BLACK_LABELS[::-1]
            up_labels = ChessBoardRenderer._RED_LABELS
            mid_labels = ChessBoardRenderer._MID_LABELS[::-1]

        for i, label in enumerate(down_labels):
            ax.text(i, -0.6, label, va="top", **style)
        for i, label in enumerate(up_labels):
            ax.text(i, 9.6, label, va="bottom", **style)

        ax.text(2, 4.5, mid_labels[0], va="center", **style)
        ax.text(6, 4.5, mid_labels[1], va="center", **style)

    def _draw_highlight(self, ax, highlight_pieces):
        r = 1.2 * self._style["piece"]["radius"]
        width = r * 0.3

        hl_style = {
            "color": self._style["highlight"]["color"],
            "lw": self._style["highlight"]["lw"],
            "zorder": 4,
        }

        for x, y in highlight_pieces:
            left, right = x - r, x + r
            down, top = y - r, y + r
            # left down
            ax.add_line(Line2D([left, left + width], [down, down], **hl_style))
            ax.add_line(Line2D([left, left], [down, down + width], **hl_style))
            # right down
            ax.add_line(Line2D([right - width, right], [down, down], **hl_style))
            ax.add_line(Line2D([right, right], [down, down + width], **hl_style))
            # left up
            ax.add_line(Line2D([left, left + width], [top, top], **hl_style))
            ax.add_line(Line2D([left, left], [top - width, top], **hl_style))
            # right up
            ax.add_line(Line2D([right - width, right], [top, top], **hl_style))
            ax.add_line(Line2D([right, right], [top - width, top], **hl_style))

    def _draw_arrows(self, ax, arrows):
        arrows_style = {
            "arrowstyle": "->",
            "color": self._style["arrow"]["color"],
            "mutation_scale": self._style["arrow"]["mutation_scale"],
            "linewidth": self._style["arrow"]["lw"],
            "zorder": 5,
        }

        arrows_text_style = {
            "color": "white",
            "fontsize": 8,
            "ha": "center",
            "va": "center",
            "zorder": 6,
            "bbox": {
                "boxstyle": "circle,pad=0.2",
                "facecolor": self._style["arrow"]["color"],
                "edgecolor": "none",
            },
        }

        n = len(arrows)
        for idx, ((x1, y1), (x2, y2)) in enumerate(arrows, start=1):
            arrow = FancyArrowPatch((x1, y1), (x2, y2), **arrows_style)
            ax.add_patch(arrow)
            if n == 1:
                continue

            text_x = x1 + 0.5 * (x2 - x1)
            text_y = y1 + 0.5 * (y2 - y1)
            ax.text(text_x, text_y, str(idx), **arrows_text_style)
