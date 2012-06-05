"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
import tools


class TestTools(TestCase):
    def test_format_minutes_to_hhmm(self):
        self.assertEqual("01:00", tools.format_minutes_to_hhmm(60))
        self.assertEqual("00:59", tools.format_minutes_to_hhmm(59))
        self.assertEqual("23:59", tools.format_minutes_to_hhmm(1439))

        # NOTE: Is this what we want?
        self.assertEqual("24:00", tools.format_minutes_to_hhmm(1440))

        # huh?
        self.assertEqual("59:59", tools.format_minutes_to_hhmm(3599))

    def test_format_minutes_to_pretty_format(self):
        self.assertEqual("1 minut",
                    tools.format_minutes_to_pretty_format(1))
        self.assertEqual("2 minuter",
                    tools.format_minutes_to_pretty_format(2))
        self.assertEqual("1 timme",
                    tools.format_minutes_to_pretty_format(60))
        self.assertEqual("1 timme 1 minut",
                    tools.format_minutes_to_pretty_format(61))
        self.assertEqual("2 timmar",
                    tools.format_minutes_to_pretty_format(120))
        self.assertEqual("2 timmar 1 minut",
                    tools.format_minutes_to_pretty_format(121))
        self.assertEqual("2 timmar 2 minuter",
                    tools.format_minutes_to_pretty_format(122))
        self.assertEqual("23 timmar 59 minuter",
                    tools.format_minutes_to_pretty_format(1439))

    def test_generate_list_of_quarters(self):
        self.assertEqual([(0, "00:00"),
                          (15, "00:15"),
                          (30, "00:30"),
                          (45, "00:45"),
                          (60, "01:00"),
                          (75, "01:15")],
                tools.generate_list_of_quarters(
                    minutes_max=75))
        self.assertEqual([(0, ""),
                          (15, "15 minuter"),
                          (30, "30 minuter"),
                          (45, "45 minuter"),
                          (60, "1 timme"),
                          (75, "1 timme 15 minuter"),
                          (90, "1 timme 30 minuter"),
                          (105, "1 timme 45 minuter"),
                          (120, "2 timmar"),
                          (135, "2 timmar 15 minuter")],
                tools.generate_list_of_quarters(
                    minutes_max=135,
                    output_format_func=tools.format_minutes_to_pretty_format))

