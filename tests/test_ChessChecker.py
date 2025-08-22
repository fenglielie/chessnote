import unittest
from chessnote import ChessState, ChessChecker


class TestChessChecker(unittest.TestCase):
    def setUp(self):
        self.state = ChessState(empty=True)
        self.rotate_flag = False

    # ----------------- Common -----------------
    def test_common(self):
        with self.assertRaises(ValueError):
            ChessChecker.check_move(self.state, (0, 0), (1, 0), self.rotate_flag)

        self.state[(0, 0)] = "C"
        with self.assertRaises(ValueError):
            ChessChecker.check_move(self.state, (0, 0), (0, 0), self.rotate_flag)

        self.state[(3, 0)] = "C"
        with self.assertRaises(ValueError):
            ChessChecker.check_move(self.state, (0, 0), (3, 0), self.rotate_flag)

    def test__count_between(self):
        self.state[(1, 0)] = "C"
        self.state[(1, 3)] = "C"
        self.state[(1, 7)] = "C"
        self.state[(3, 3)] = "C"
        self.state[(4, 3)] = "C"
        self.state[(5, 3)] = "C"

        self.assertEqual(ChessChecker._count_between(self.state, (1, 0), (1, 7)), 1)
        self.assertEqual(ChessChecker._count_between(self.state, (3, 3), (5, 3)), 1)

        with self.assertRaises(ValueError):
            ChessChecker._count_between(self.state, (1, 0), (5, 3))

    # ----------------- Rook -----------------
    def test_rook(self):
        self.state[(0, 0)] = "R"

        self.assertTrue(
            ChessChecker.check_move(self.state, (0, 0), (0, 5), self.rotate_flag)
        )
        self.state[(0, 3)] = "P"
        with self.assertRaises(ValueError):
            ChessChecker.check_move(self.state, (0, 0), (0, 5), self.rotate_flag)

        self.assertTrue(
            ChessChecker.check_move(self.state, (0, 0), (5, 0), self.rotate_flag)
        )
        self.state[(3, 0)] = "P"
        with self.assertRaises(ValueError):
            ChessChecker.check_move(self.state, (0, 0), (5, 0), self.rotate_flag)

    # ----------------- Knight -----------------
    def test_knight(self):
        self.state[(1, 0)] = "H"
        self.assertTrue(
            ChessChecker.check_move(self.state, (1, 0), (2, 2), self.rotate_flag)
        )
        with self.assertRaises(ValueError):
            ChessChecker.check_move(self.state, (1, 0), (2, 1), self.rotate_flag)

        self.state[(1, 1)] = "P"
        with self.assertRaises(ValueError):
            ChessChecker.check_move(self.state, (1, 0), (2, 2), self.rotate_flag)

    # ----------------- Elephant -----------------
    def test_elephant(self):
        self.state[(2, 4)] = "E"
        self.assertTrue(
            ChessChecker.check_move(self.state, (2, 4), (0, 2), self.rotate_flag)
        )

        with self.assertRaises(ValueError):
            ChessChecker.check_move(self.state, (2, 4), (3, 6), self.rotate_flag)

        with self.assertRaises(ValueError):
            ChessChecker.check_move(self.state, (2, 4), (4, 6), self.rotate_flag)

        self.state[(3, 3)] = "P"
        with self.assertRaises(ValueError):
            ChessChecker.check_move(self.state, (2, 4), (4, 2), self.rotate_flag)

        self.rotate_flag = True
        self.state[(2, 9)] = "E"
        self.assertTrue(
            ChessChecker.check_move(self.state, (2, 9), (4, 7), self.rotate_flag)
        )

    # ----------------- Advisor -----------------
    def test_advisor(self):
        self.state[(3, 0)] = "A"
        self.assertTrue(
            ChessChecker.check_move(self.state, (3, 0), (4, 1), self.rotate_flag)
        )
        with self.assertRaises(ValueError):
            ChessChecker.check_move(self.state, (3, 0), (4, 0), self.rotate_flag)
        with self.assertRaises(ValueError):
            ChessChecker.check_move(self.state, (3, 0), (2, 1), self.rotate_flag)

        self.rotate_flag = True
        self.state[(3, 9)] = "A"
        self.assertTrue(
            ChessChecker.check_move(self.state, (3, 9), (4, 8), self.rotate_flag)
        )

    # ----------------- King -----------------
    def test_king(self):
        self.state[(3, 0)] = "K"
        self.assertTrue(
            ChessChecker.check_move(self.state, (3, 0), (3, 1), self.rotate_flag)
        )
        with self.assertRaises(ValueError):
            ChessChecker.check_move(self.state, (3, 0), (5, 0), self.rotate_flag)
        with self.assertRaises(ValueError):
            ChessChecker.check_move(self.state, (3, 0), (2, 0), self.rotate_flag)

        self.rotate_flag = True
        self.state[(3, 9)] = "K"
        self.assertTrue(
            ChessChecker.check_move(self.state, (3, 9), (3, 8), self.rotate_flag)
        )

    # ----------------- Cannon -----------------
    def test_cannon(self):
        self.state[(1, 2)] = "C"
        self.assertTrue(
            ChessChecker.check_move(self.state, (1, 2), (1, 5), self.rotate_flag)
        )
        with self.assertRaises(ValueError):
            ChessChecker.check_move(self.state, (1, 2), (2, 0), self.rotate_flag)

        self.state[(1, 1)] = "P"
        with self.assertRaises(ValueError):
            ChessChecker.check_move(self.state, (1, 2), (1, 0), self.rotate_flag)

        self.state[(1, 3)] = "P"
        self.state[(1, 4)] = "p"
        self.assertTrue(
            ChessChecker.check_move(self.state, (1, 2), (1, 4), self.rotate_flag)
        )

        self.state = ChessState(empty=True)
        self.state[(1, 2)] = "C"
        self.state[(1, 4)] = "p"
        with self.assertRaises(ValueError):
            ChessChecker.check_move(self.state, (1, 2), (1, 4), self.rotate_flag)

    # ----------------- Pawn -----------------
    def test_pawn(self):
        self.state[(0, 3)] = "P"
        self.assertTrue(
            ChessChecker.check_move(self.state, (0, 3), (0, 4), self.rotate_flag)
        )
        with self.assertRaises(ValueError):
            ChessChecker.check_move(self.state, (0, 3), (0, 5), self.rotate_flag)
        with self.assertRaises(ValueError):
            ChessChecker.check_move(self.state, (0, 3), (0, 2), self.rotate_flag)

        with self.assertRaises(ValueError):
            ChessChecker.check_move(self.state, (0, 3), (1, 3), self.rotate_flag)

        self.state[(0, 5)] = "P"
        self.assertTrue(
            ChessChecker.check_move(self.state, (0, 5), (1, 5), self.rotate_flag)
        )

        self.rotate_flag = True
        self.state[(0, 5)] = "p"
        self.assertTrue(
            ChessChecker.check_move(self.state, (0, 5), (0, 6), self.rotate_flag)
        )
        with self.assertRaises(ValueError):
            ChessChecker.check_move(self.state, (0, 5), (0, 4), self.rotate_flag)


if __name__ == "__main__":
    unittest.main()
