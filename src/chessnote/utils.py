import logging
from collections.abc import Sequence

import matplotlib
from matplotlib import pyplot as plt
import matplotlib.font_manager
from matplotlib_inline import backend_inline

# types


class Types:
    Pos = tuple[int, int]
    SeqPos = Sequence[Pos]
    SeqSeqPos = Sequence[SeqPos]

    Arrow = tuple[Pos, Pos]
    SeqArrow = Sequence[Arrow]
    SeqSeqArrow = Sequence[SeqArrow]


# logging

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s]{%(name)s} %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("chessnote")


# rotate flag

_rotate_flag_default = False


def set_rotate_flag(flag: bool):
    """Set the default rotate_flag for newly created objects."""
    global _rotate_flag_default
    _rotate_flag_default = flag


def get_rotate_flag() -> bool:
    """Get the current default rotate_flag."""
    return _rotate_flag_default


# plot setup
_cached_font = None


def _get_kaiti_font():
    """
    Return a Kaiti-style font if available.
    """
    global _cached_font

    if _cached_font is not None:
        return _cached_font
    candidates = ["KaiTi", "STKaiti", "WenQuanYi Zen Hei"]
    for name in candidates:
        try:
            prop = matplotlib.font_manager.FontProperties(family=name)
            if prop.get_name():
                _cached_font = prop
                return prop
        except Exception:
            continue
    _cached_font = matplotlib.font_manager.FontProperties(family="sans-serif")
    return _cached_font


plt.rcParams["font.sans-serif"] = [_get_kaiti_font().get_name()]

backend_inline.set_matplotlib_formats("svg")
