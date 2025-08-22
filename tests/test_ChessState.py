import unittest
import tempfile
import os
from chessnote import ChessState, ChessStateIO, set_rotate_flag


class TestChessState(unittest.TestCase):
    def setUp(self):
        self.state = ChessState()

    def test_initial_state(self):
        self.assertEqual(self.state[(0, 0)], "R")
        self.assertEqual(self.state[(4, 0)], "K")
        self.assertEqual(self.state[(0, 9)], "r")
        self.assertEqual(len(self.state), 32)

    def test_initial_state_rotate(self):
        set_rotate_flag(False)

        self.state = ChessState()
        self.assertEqual(self.state[(0, 0)], "R")
        self.assertEqual(self.state[(4, 0)], "K")
        self.assertEqual(self.state[(0, 9)], "r")
        self.assertEqual(len(self.state), 32)

        self.state = ChessState(rotate=True)
        self.assertEqual(self.state[(0, 0)], "r")
        self.assertEqual(self.state[(4, 0)], "k")
        self.assertEqual(self.state[(0, 9)], "R")
        self.assertEqual(len(self.state), 32)

        set_rotate_flag(True)

        self.state = ChessState()
        self.assertEqual(self.state[(0, 0)], "r")
        self.assertEqual(self.state[(4, 0)], "k")
        self.assertEqual(self.state[(0, 9)], "R")
        self.assertEqual(len(self.state), 32)

        self.state = ChessState(rotate=False)
        self.assertEqual(self.state[(0, 0)], "R")
        self.assertEqual(self.state[(4, 0)], "K")
        self.assertEqual(self.state[(0, 9)], "r")
        self.assertEqual(len(self.state), 32)

        set_rotate_flag(False)

    def test_set_get_del_item(self):
        self.state[(4, 4)] = "P"
        self.assertEqual(self.state[(4, 4)], "P")
        del self.state[(4, 4)]
        self.assertNotIn((4, 4), self.state)

        with self.assertRaises(KeyError):
            _ = self.state[(10, None)]  # type: ignore
        with self.assertRaises(KeyError):
            _ = self.state[(10, 10)]

        with self.assertRaises(ValueError):
            self.state[(0, 0)] = "X"
        with self.assertRaises(ValueError):
            self.state[(0, 0)] = 10  # type: ignore

    def test_move(self):
        start = (0, 0)
        end = (0, 1)
        piece = self.state[start]
        self.state.move(start, end)
        self.assertEqual(self.state[end], piece)
        self.assertNotIn(start, self.state)

        # not exist
        start = (1, 1)
        end = (2, 1)
        with self.assertRaises(ValueError):
            self.state.move(start, end)

    def test_rotate_pieces(self):
        orig_positions = list(self.state._pieces.keys())
        self.state.rotate_pieces()
        rotated_positions = list(self.state._pieces.keys())
        self.assertEqual(len(orig_positions), len(rotated_positions))
        self.assertEqual(self.state[(8, 9)], "R")

    def test_swap_pieces(self):
        piece_before = self.state[(0, 0)]
        self.state.swap_pieces()
        piece_after = self.state[(0, 0)]
        self.assertEqual(piece_before.swapcase(), piece_after)

    def test_deepcopy(self):
        new_state = self.state.deepcopy()
        self.assertEqual(self.state._pieces, new_state._pieces)
        new_state[(0, 0)] = "P"
        self.assertNotEqual(self.state[(0, 0)], new_state[(0, 0)])

    def test_io_dict_and_json(self):
        d = ChessStateIO.save_to_dict(self.state)
        loaded_state = ChessStateIO.load_from_dict(d)
        self.assertEqual(self.state._pieces, loaded_state._pieces)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "state.json")
            ChessStateIO.save_to_json_file(self.state, filepath)
            loaded_json_state = ChessStateIO.load_from_json_file(filepath)
            self.assertEqual(self.state._pieces, loaded_json_state._pieces)


if __name__ == "__main__":
    unittest.main()
