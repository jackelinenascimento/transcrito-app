import unittest

from src.application.utils.time_formatter import format_duration


class FormatDurationTest(unittest.TestCase):

    def test_formats_duration_without_hours(self):
        self.assertEqual(format_duration(0), "00m 00s")
        self.assertEqual(format_duration(65.8), "01m 05s")

    def test_formats_duration_with_hours(self):
        self.assertEqual(format_duration(3661), "01h 01m 01s")


if __name__ == "__main__":
    unittest.main()
