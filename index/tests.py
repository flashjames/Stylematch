"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from index.models import BetaEmail, Tip
from index.views import make_pagination_list


class IndexViewsTest(TestCase):
    def test_index(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)

    def test_beta_email(self):
        resp = self.client.get('/get_invite', follow=True)
        self.assertEqual(resp.status_code, 200)

        data = {'email': 'badformat'}
        resp = self.client.post('/get_invite', data, follow=True)
        self.assertEqual(resp.status_code, 200)

        with self.assertRaises(BetaEmail.DoesNotExist):
            BetaEmail.objects.get(email='badformat')

        data = {'email': 'good@email.com'}
        resp = self.client.post('/get_invite', data, follow=True)
        self.assertEqual(resp.status_code, 200)

        #redirected from /get_invite
        self.assertEqual(resp.redirect_chain[0][1], 302)
        try:
            beta = BetaEmail.objects.get(email='good@email.com')
        except:
            self.fail("'good@email.com' should be in the database")

    def test_tip(self):
        return #FIXME: Remove when LoginRequiredMixin is no longer present
        resp = self.client.get('/tip/')
        self.assertEqual(resp.status_code, 200)

        data = {'name': 'Alice',
                'address': 'Big street 123',
                'zip': '12345',
                'city': 'New York',
                'phone': '0731234567'}
        resp = self.client.post('/tip/', data, follow=True)
        self.assertEqual(resp.status_code, 200)

        try:
            # also make sure a hyphen is inserted
            tip = Tip.objects.get(phone='073-1234567')
        except:
            self.fail("Tip with phonenumber '073-1234567' should "
                      "be in the database")

        # try post the same data again
        resp = self.client.post('/tip/', data, follow=True)
        self.assertEqual(resp.status_code, 200)

        tip = Tip.objects.filter(phone='073-1234567')

        # only 1 tip with that phone number can exist
        self.assertEqual(len(tip), 1)


class TestPagination(TestCase):

    def test_make_pagination_list(self):
        list = range(1, 5) # _1_,2,3,4
        self.assertEqual([1,2,3,4], make_pagination_list(list, 1))

        list = range(1, 8) # _1_,2,3 ... 5,6,7
        self.assertEqual([1,2,3,False,5,6,7], make_pagination_list(list, 1))

        list = range(1, 8) # 1,2,_3_,4, 5,6,7
        self.assertEqual([1,2,3,4,5,6,7], make_pagination_list(list, 3))

        list = range(1, 8) # 1,2,3,4, _5_,6,7
        self.assertEqual([1,2,3,4,5,6,7], make_pagination_list(list, 5))

        list = range(1, 18) # _1_,2,3 ... 15,16,17
        self.assertEqual([1,2,3,False,15,16,17], make_pagination_list(list, 1))

        list = range(1, 18) # 1,2,3,4,_5_,6 ... 15,16,17
        self.assertEqual([1,2,3,4,5,6,False,15,16,17], make_pagination_list(list, 5))

        list = range(1, 18) # 1,2,3 ... 5,_6_,7 ... 15,16,17
        self.assertEqual([1,2,3,False,5,6,7,False,15,16,17], make_pagination_list(list, 6))

        list = range(1, 18) # 1,2,3 ... 15,16,_17_
        self.assertEqual([1,2,3,False,15,16,17], make_pagination_list(list, 17))
