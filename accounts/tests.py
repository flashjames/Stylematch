from django.test import TestCase
from tastypie.serializers import Serializer
from accounts.models import UserProfile, ProfileImage
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

    def test_list_with_time_interval(self):
        self.assertEqual([(0, "00:00"),
                          (30, "00:30"),
                          (60, "01:00"),
                          (90, "01:30")],
                tools.list_with_time_interval(stop=90))
        self.assertEqual([(30, "00:30")], 
                tools.list_with_time_interval(
                    start=30,
                    stop=45,
                    interval=30))
        self.assertEqual([(0, "00:00"),
                          (15, "00:15"),
                          (30, "00:30"),
                          (45, "00:45"),
                          (60, "01:00"),
                          (75, "01:15")],
                tools.list_with_time_interval(
                    stop=75,
                    interval=15))
        self.assertEqual([(30, "30 minuter"),
                          (45, "45 minuter"),
                          (60, "1 timme"),
                          (75, "1 timme 15 minuter"),
                          (90, "1 timme 30 minuter"),
                          (105, "1 timme 45 minuter"),
                          (120, "2 timmar"),
                          (135, "2 timmar 15 minuter")],
                tools.list_with_time_interval(
                    start=30,
                    stop=140,
                    interval=15,
                    format_function=tools.format_minutes_to_pretty_format))


class ProfileResourceTest(TestCase):
    """
    Testcases for ProfileResource

    NOTE:
    Tastypie has a new testing infrastructure since April. Might want
    to use that:
    http://django-tastypie.readthedocs.org/en/latest/testing.html
    """
    fixtures = ['test_userprofiles.json']

    def setUp(self):
        super(ProfileResourceTest, self).setUp()
        self.serializer = Serializer()

    def test_get_profiles(self):
        resp = self.client.get('/api/profile/profiles/', format='json')

        # for now:
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp['Content-Type'].startswith('application/json'))
        self.serializer.from_json(resp.content)
        # when using tastypies new testing infrastructure:
        # self.assertValidJSON(resp)

        val = self.serializer.deserialize(resp.content, format=resp['Content-Type'])
        self.assertEqual(len(val['objects']), 2) # two users in fixture
