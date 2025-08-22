import unittest
from chessnote import ChessState, ChessRecorder, ChessBoardRenderer


class TestChessRecorder(unittest.TestCase):
    def setUp(self):
        self.rec = ChessRecorder(ChessState(empty=True))
        self.rec._history._queue[0].state[(0, 0)] = "R"
        self.rec._history._queue[0].state[(1, 0)] = "H"
        self.rec._history._queue[0].state[(0, 3)] = "P"
        self.rec._history._queue[0].state[(0, 9)] = "r"
        self.rec._history._queue[0].state[(1, 9)] = "h"
        self.rec._history._queue[0].state[(0, 6)] = "p"

    # ----------------- move -----------------
    def test_move_valid(self):
        self.rec.move((0, 0), (0, 1))
        self.assertIn((0, 1), self.rec._history._queue[-1].state)
        self.assertEqual(self.rec._history._queue[-1].state[(0, 1)], "R")

    def test_move_invalid(self):
        with self.assertRaises(ValueError):
            self.rec.move((0, 0), (1, 1))

    # ----------------- exec -----------------
    def test_exec_cmds(self):
        self.rec._history._queue[0].state[(8, 0)] = "R"
        self.rec.exec(["车一进二"])
        last_state = self.rec._history._queue[-1].state
        self.assertIn((8, 2), last_state)
        self.assertEqual(last_state[(8, 2)], "R")

        self.rec = self.rec.rotate()
        self.rec.exec("车9退1，车一退一")
        last_state = self.rec._history._queue[-1].state
        self.assertIn((0, 1), last_state)
        self.assertEqual(last_state[(0, 1)], "R")

        with self.assertRaises(TypeError):
            self.rec.exec({"车1进2", "车一进三"})  # type: ignore

        with self.assertRaises(ValueError):
            self.rec.exec("马二退三")

        with self.assertRaises(ValueError):
            self.rec.exec("马2退3")

    # ----------------- checkpoints -----------------
    def test_checkpoint_and_rollback(self):
        self.rec.move((0, 0), (0, 1))
        self.rec.move((0, 9), (0, 7))
        self.rec.set_checkpoint("after_first")
        self.rec.move((0, 1), (0, 2))
        self.rec.rollback_to_checkpoint("after_first")
        last_state = self.rec._history._queue[-1].state
        self.assertIn((0, 1), last_state)
        self.assertNotIn((0, 2), last_state)

        with self.assertRaises(KeyError):
            self.rec.rollback_to_checkpoint("xxx")

    def test_rollback_steps(self):
        self.rec.move((0, 0), (0, 1))
        self.rec.move((0, 9), (0, 8))
        self.rec.rollback(1)
        last_state = self.rec._history._queue[-1].state
        self.assertIn((0, 1), last_state)
        self.assertNotIn((0, 2), last_state)

        self.rec.rollback(2)

        with self.assertRaises(ValueError):
            self.rec.rollback(-2)

    # ----------------- deepcopy/derive -----------------
    def test_deepcopy(self):
        self.rec.move((0, 0), (0, 1))
        new_rec = self.rec.deepcopy()
        new_rec.move((0, 9), (0, 8))
        new_rec.move((0, 1), (0, 2))
        self.assertIn((0, 1), self.rec._history._queue[-1].state)
        self.assertNotIn((0, 2), self.rec._history._queue[-1].state)

    def test_derive(self):
        self.rec.move((0, 0), (0, 1))
        self.rec.move((0, 9), (0, 8))

        new_rec = self.rec.derive()
        self.assertEqual(
            self.rec._history._queue[-1].state, new_rec._history._queue[0].state
        )

    # ----------------- draw/animate -----------------
    def test_draw(self):
        self.rec = ChessRecorder(ChessState())

        self.rec.draw(renderer=ChessBoardRenderer())
        self.rec.draw()
        self.rec.draw(highlight_last_move=False)

        self.rec.exec("车九进二,炮2平5，马八进七")
        self.rec.draw()

    def test_animate(self):
        self.rec = ChessRecorder()

        self.rec.animate(
            renderer=ChessBoardRenderer(), highlight_moves=True, duration=100
        )
        self.rec.animate(highlight_moves=False, duration=100)

        self.rec.exec("车九进二,炮2平5，马八进七")
        self.rec.animate(highlight_moves=False)
        self.rec.animate()

    def test_dryrun(self):
        self.rec = ChessRecorder()
        self.rec.dryrun(["炮二平五", "马八进七"])

    # ----------------- repr -----------------
    def test_repr(self):
        print(self.rec)


if __name__ == "__main__":
    unittest.main()
