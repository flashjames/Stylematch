"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from index.models import BetaEmail, Tip


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
