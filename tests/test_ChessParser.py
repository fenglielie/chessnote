import unittest
from chessnote import ChessState, ChessParser


class TestChessParser(unittest.TestCase):
    def setUp(self):
        self.state = ChessState(empty=True)
        self.state[(0, 0)] = "R"
        self.state[(1, 0)] = "H"
        self.state[(4, 2)] = "E"
        self.state[(3, 0)] = "A"
        self.state[(4, 0)] = "K"
        self.state[(1, 2)] = "C"
        self.state[(1, 3)] = "C"
        self.state[(0, 3)] = "P"
        self.state[(0, 5)] = "P"
        self.state[(0, 6)] = "P"

        self.state[(4, 5)] = "H"
        self.state[(8, 4)] = "R"

        self.state[(1, 7)] = "c"
        self.state[(1, 9)] = "h"
        self.state[(1, 8)] = "h"

    # ----------------- detect_color -----------------
    def test_detect_color(self):
        self.assertEqual(ChessParser.detect_color("马二进三"), "red")
        self.assertEqual(ChessParser.detect_color("马2进3"), "black")
        with self.assertRaises(ValueError):
            ChessParser.detect_color("未知命令")

    # ----------------- detect_side -----------------
    def test_detect_side(self):
        self.assertEqual(ChessParser.detect_side("red", rotate_flag=False), "down")
        self.assertEqual(ChessParser.detect_side("red", rotate_flag=True), "up")
        self.assertEqual(ChessParser.detect_side("black", rotate_flag=False), "up")
        self.assertEqual(ChessParser.detect_side("black", rotate_flag=True), "down")

    # ----------------- normalize_cmds -----------------
    def test_normalize_cmds(self):
        self.assertEqual(
            ChessParser.normalize_cmds("炮二平五，马2进3"),
            [
                "炮二平五",
                "马2进3",
            ],
        )

        self.assertEqual(ChessParser.normalize_cmds("1."), [])

        cmds = ChessParser.normalize_cmds("1. 车一平二  马2进3  2. 车二平三")
        self.assertEqual(cmds, ["车一平二", "马2进3", "车二平三"])

        text2 = "车一平二  车二平三"
        with self.assertRaises(ValueError):
            ChessParser.normalize_cmds(text2)

    # ----------------- parse_piece_char -----------------
    def test_parse_piece_char(self):
        self.assertEqual(
            ChessParser.parse_piece_char("车", color="red", strict_flag=True), "R"
        )
        self.assertEqual(
            ChessParser.parse_piece_char("車", color="black", strict_flag=True), "r"
        )

        with self.assertRaises(ValueError):
            ChessParser.parse_piece_char("车", color="black", strict_flag=True)

        # not strict
        self.assertEqual(
            ChessParser.parse_piece_char("车", color="black", strict_flag=False), "r"
        )

        with self.assertRaises(ValueError):
            ChessParser.parse_piece_char("包", color="black", strict_flag=False)

    # ----------------- parse_col_idx -----------------
    def test_parse_col_idx(self):
        self.assertEqual(ChessParser.parse_col_idx("一", color="red", side="up"), 0)
        self.assertEqual(ChessParser.parse_col_idx("1", color="black", side="up"), 0)
        self.assertEqual(ChessParser.parse_col_idx("一", color="red", side="down"), 8)
        with self.assertRaises(ValueError):
            ChessParser.parse_col_idx("十", color="red", side="up")
        with self.assertRaises(ValueError):
            ChessParser.parse_col_idx("a", color="black", side="up")
        with self.assertRaises(ValueError):
            ChessParser.parse_col_idx("10", color="black", side="up")

    # ----------------- parse_row_delta -----------------
    def test_parse_row_delta(self):
        self.assertEqual(ChessParser.parse_row_delta("一", color="red", side="up"), -1)
        self.assertEqual(ChessParser.parse_row_delta("一", color="red", side="down"), 1)

        with self.assertRaises(ValueError):
            ChessParser.parse_row_delta("1", color="red", side="up")

        self.assertEqual(ChessParser.parse_row_delta("1", color="black", side="up"), -1)
        self.assertEqual(
            ChessParser.parse_row_delta("1", color="black", side="down"), 1
        )

        with self.assertRaises(ValueError):
            ChessParser.parse_row_delta("10", color="black", side="up")

        with self.assertRaises(ValueError):
            ChessParser.parse_row_delta("一", color="black", side="up")

    # ----------------- parse_cmd -----------------
    def test_parse_cmd_basic(self):
        start, end = ChessParser.parse_cmd(self.state, "车九平八")
        self.assertEqual((start, end), ((0, 0), (1, 0)))

        start, end = ChessParser.parse_cmd(self.state, "车一退一")
        self.assertEqual((start, end), ((8, 4), (8, 3)))

        start, end = ChessParser.parse_cmd(self.state, "马八进七")
        self.assertEqual((start, end), ((1, 0), (2, 2)))

        start, end = ChessParser.parse_cmd(self.state, "马五退三")
        self.assertEqual((start, end), ((4, 5), (6, 4)))

        start, end = ChessParser.parse_cmd(self.state, "相五进三")
        self.assertEqual((start, end), ((4, 2), (6, 4)))

        start, end = ChessParser.parse_cmd(self.state, "相五退三")
        self.assertEqual((start, end), ((4, 2), (6, 0)))

        start, end = ChessParser.parse_cmd(self.state, "士六进五")
        self.assertEqual((start, end), ((3, 0), (4, 1)))

        start, end = ChessParser.parse_cmd(self.state, "帅五进一")
        self.assertEqual((start, end), ((4, 0), (4, 1)))

    def test_parse_cmd_hard_mode(self):
        start, end = ChessParser.parse_cmd(self.state, "前炮平三")
        self.assertEqual((start, end), ((1, 3), (6, 3)))

        start, end = ChessParser.parse_cmd(self.state, "前马进3")
        self.assertEqual((start, end), ((1, 8), (2, 6)))

        with self.assertRaises(ValueError):
            ChessParser.parse_cmd(self.state, "中炮平一")

        with self.assertRaises(ValueError):
            ChessParser.parse_cmd(self.state, "前马进一")

        with self.assertRaises(ValueError):
            ChessParser.parse_cmd(self.state, "后相进一")

        with self.assertRaises(ValueError):
            ChessParser.parse_cmd(self.state, "后车进一")

        with self.assertRaises(ValueError):
            ChessParser.parse_cmd(self.state, "前炮进1")

        start, end = ChessParser.parse_cmd(self.state, "前兵进一")
        self.assertEqual((start, end), ((0, 6), (0, 7)))
        start, end = ChessParser.parse_cmd(self.state, "中兵平八")
        self.assertEqual((start, end), ((0, 5), (1, 5)))
        start, end = ChessParser.parse_cmd(self.state, "后兵进一")
        self.assertEqual((start, end), ((0, 3), (0, 4)))

    def test_parse_cmd_invalid(self):

        with self.assertRaises(ValueError):
            ChessParser.parse_cmd(self.state, "车九前一")

        with self.assertRaises(ValueError):
            ChessParser.parse_cmd(self.state, "车十平二")

        with self.assertRaises(ValueError):
            ChessParser.parse_cmd(self.state, "未知命令")

        with self.assertRaises(ValueError):
            ChessParser.parse_cmd(self.state, "车九退一")

        with self.assertRaises(ValueError):
            ChessParser.parse_cmd(self.state, "将5进1")

        with self.assertRaises(ValueError):
            ChessParser.parse_cmd(self.state, "相五平三")

        with self.assertRaises(ValueError):
            ChessParser.parse_cmd(self.state, "马八进五")

        with self.assertRaises(ValueError):
            ChessParser.parse_cmd(self.state, "马八平六")

        with self.assertRaises(ValueError):
            ChessParser.parse_cmd(self.state, "马7进6")

        self.state[(7, 5)] = "R"

        with self.assertRaises(ValueError):
            ChessParser.parse_cmd(self.state, "车二进五")

        with self.assertRaises(ValueError):
            ChessParser.parse_cmd(self.state, "车二进七")


if __name__ == "__main__":
    unittest.main()
