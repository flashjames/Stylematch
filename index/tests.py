"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from index.models import BetaEmail


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


