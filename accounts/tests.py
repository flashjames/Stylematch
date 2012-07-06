# coding: utf-8
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.handlers.wsgi import WSGIRequest
from accounts.tastypie_test import ResourceTestCase
from tastypie.serializers import Serializer
from accounts.models import UserProfile, ProfileImage
from accounts.register_views import RegisterCustomBackend
from registration.models import RegistrationProfile
from registration.backends.default import DefaultBackend
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


class ProfileResourceTest(ResourceTestCase):
    """
    Testcases for ProfileResource

    Tastypie has a new testing infrastructure since April. We're using
    that:
    http://django-tastypie.readthedocs.org/en/latest/testing.html
    """
    fixtures = ['test_userprofiles.json']

    def setUp(self):
        super(ProfileResourceTest, self).setUp()

        self.api_url = '/api/profile/profiles/'

        self.keys = ['zip_adress',
                     'show_booking_url',
                     'profile_text',
                     'salon_phone_number',
                     'personal_phone_number',
                     'url_online_booking',
                     'profile_image',
                     'salon_name',
                     'salon_city',
                     'salon_adress',
                     'number_on_profile',
                     'salon_url',
                     'id',
                     'profile_url',
                     'first_name',
                     'last_name']

    def test_get_list_json(self):
        resp = self.api_client.get('/api/profile/profiles/', format='json')
        self.assertValidJSONResponse(resp)

        # make sure all values are there
        # fixture has 6 values, where 1 has visible=False
        self.assertEqual(len(self.deserialize(resp)['objects']), 5)

    def test_get_detail_json(self):
        resp = self.api_client.get(self.api_url + "2/", format='json')
        self.assertValidJSONResponse(resp)

        # make sure all keys are there
        self.assertKeys(self.deserialize(resp), self.keys)
        self.assertEqual(self.deserialize(resp)['salon_name'], 'Testsalon2')

    def test_filter_by_city(self):
        resp = self.api_client.get(self.api_url,
                data={'salon_city__iexact': 'linköping', 'format': 'json'})
        self.assertValidJSONResponse(resp)
        # 2 visible profiles are from linköping
        self.assertEqual(len(self.deserialize(resp)['objects']), 2)

        resp = self.api_client.get(self.api_url,
                data={'salon_city__iexact': 'stockholm', 'format': 'json'})
        self.assertValidJSONResponse(resp)
        # 1 visible profile are from Stockholm
        self.assertEqual(len(self.deserialize(resp)['objects']), 2)

#    def test_filter_by_city_startswith(self):
#        resp = self.api_client.get(self.api_url,
#                data={'salon_city__startswith': 'link', 'format': 'json'})
#        self.assertValidJSONResponse(resp)
#        # 2 visible profiles are from linköping
#        self.assertEqual(len(self.deserialize(resp)['objects']), 2)
#
#    def test_filter_by_city_endswith(self):
#        resp = self.api_client.get(self.api_url,
#                data={'salon_city__endswith': 'köping', 'format': 'json'})
#        self.assertValidJSONResponse(resp)
#        # 2 visible profiles are from linköping and one from norrköping
#        self.assertEqual(len(self.deserialize(resp)['objects']), 3)


class _MockRequestClient(Client):
    """
    A ``django.test.Client`` subclass which can return mock
    ``HttpRequest`` objects.
    """

    def request(self, **request):
        """
        Rather than issuing a request and returning the response, this
        simply constructs an ``HttpRequest`` object and returns it.
        """
        environ = {
            'HTTP_COOKIE': self.cookies,
            'PATH_INFO': '/',
            'QUERY_STRING': '',
            'REMOTE_ADDR': '127.0.0.1',
            'REQUEST_METHOD': 'GET',
            'SCRIPT_NAME': '',
            'SERVER_NAME': 'testserver',
            'SERVER_PORT': '80',
            'SERVER_PROTOCOL': 'HTTP/1.1',
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'http',
            'wsgi.errors': self.errors,
            'wsgi.multiprocess': True,
            'wsgi.multithread': False,
            'wsgi.run_once': False,
            'wsgi.input': None,
            }
        environ.update(self.defaults)
        environ.update(request)
        request = WSGIRequest(environ)

        # We have to manually add a session since we'll be bypassing
        # the middleware chain.
        session_middleware = SessionMiddleware()
        session_middleware.process_request(request)
        return request


def _mock_request(first_name, last_name):
    """
    Construct and return a mock ``HttpRequest`` object; this is used
    in testing backend methods which expect an ``HttpRequest`` but
    which are not being called from views.
    """
    request = _MockRequestClient().request()
    request.POST._mutable = True
    request.POST['first_name'] = first_name
    request.POST['last_name'] = last_name
    request.POST._mutable = False
    return request


class TestModels(TestCase):

    user_info = {'password1': 'swordfish',
                 'email': 'alice@example.com'}

    backend = DefaultBackend()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_temporary_profile(self):
        """
        Create a standard profile url at signup step using first name and
        last name. Add number if the url is already taken.

        John Nelson       -> /john-nelson
        John Nelson again -> /john-nelson2

        """
        # alice wonder -> 'alice-wonder'
        request = _mock_request('alice', 'wonder')
        new_user = self.backend.register(request,
                                         username='alice',
                                         **self.user_info)
        self.assertEqual(new_user.userprofile.profile_url, 'alice-wonder')

        # alice wonder land -> 'alice-wonder-land'
        request = _mock_request('alice', 'wonder land')
        new_user = self.backend.register(request,
                                         username='alice1',
                                         **self.user_info)
        self.assertEqual(new_user.userprofile.profile_url, 'alice-wonder-land')

        # alice-yun wonderland -> 'alice-yun-wonderland'
        request = _mock_request('alice-yun', 'wonderland')
        new_user = self.backend.register(request,
                                         username='alice2',
                                         **self.user_info)
        self.assertEqual(new_user.userprofile.profile_url, 'alice-yun-wonderland')
