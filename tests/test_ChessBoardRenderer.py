import os
import unittest
import tempfile
from chessnote import ChessState, ChessBoardRenderer


class TestChessBoardRenderer(unittest.TestCase):
    def setUp(self):
        self.state = ChessState()
        self.renderer = ChessBoardRenderer()

    def test_draw_returns_fig_ax(self):
        fig, ax = self.renderer.draw(self.state, return_fig=True)
        self.assertIsNotNone(fig)
        self.assertIsNotNone(ax)
        fig.clf()

    def test_draw_returns_fig_ax_rotate(self):
        self.renderer.rotate()
        fig, ax = self.renderer.draw(self.state, return_fig=True)
        self.assertIsNotNone(fig)
        self.assertIsNotNone(ax)
        fig.clf()
        self.renderer.rotate()

    def test_draw_saves_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "chess.png")
            self.renderer.draw(self.state, filename=filepath)
            self.assertTrue(os.path.exists(filepath))
            self.assertGreater(os.path.getsize(filepath), 0)

    def test_highlight_and_arrows(self):
        highlights = [(0, 0), (4, 0)]
        arrows = [((0, 0), (0, 1))]
        fig, _ = self.renderer.draw(
            self.state, highlight_pieces=highlights, arrows=arrows, return_fig=True
        )
        self.assertIsNotNone(fig)
        fig.clf()

    def test_more_arrows(self):
        arrows = [((0, 0), (0, 1)), ((2, 0), (4, 1))]
        fig, _ = self.renderer.draw(self.state, arrows=arrows, return_fig=True)
        self.assertIsNotNone(fig)
        fig.clf()

    def test_rotate_flag_effect(self):
        original_flag = self.renderer._rotate_flag
        self.renderer.rotate()
        self.assertNotEqual(self.renderer._rotate_flag, original_flag)
        self.renderer.rotate()
        self.assertEqual(self.renderer._rotate_flag, original_flag)

    def test_animate_generates_frames(self):
        states = [self.state.deepcopy(), self.state.deepcopy()]
        states[1].move((0, 0), (0, 1))
        self.renderer.animate(states, duration=100)
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "chess.gif")
            self.renderer.animate(states, duration=100, filename=filepath)
            self.assertTrue(os.path.exists(filepath))
            self.assertGreater(os.path.getsize(filepath), 0)

    def test_custom_style_and_piece_config(self):
        style = {"board": {"grid_color": "blue"}, "unknonwn": None}
        piece_config = {"K": "King"}
        renderer = ChessBoardRenderer(style=style, piece_config=piece_config)
        fig, _ = renderer.draw(self.state, return_fig=True)
        self.assertEqual(renderer._style["board"]["grid_color"], "blue")
        self.assertEqual(renderer._piece_config["K"], "King")
        fig.clf()


if __name__ == "__main__":
    unittest.main()
