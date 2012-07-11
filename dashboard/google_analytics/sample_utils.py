#!/usr/bin/python
#
# Copyright 2012 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Utilities for Analytics API code samples.

Handles various tasks to do with logging, authentication and initialization.
Mostly taken from Sergio :)

Before You Begin:

You must update the client_secrets.json file with a client id, client secret,
and the redirect uri. You get these values by creating a new project
in the Google APIs console and registering for OAuth2.0 for installed
applications: https://code.google.com/apis/console

Also all OAuth2.0 tokens are stored for resue in the file specified
as TOKEN_FILE_NAME. You can modify this file name if you wish.
"""

__author__ = ('sergio.gomes@google.com (Sergio Gomes)'
              'api.nickm@gmail.com (Nick Mihailovski)')



"""
Test to get 2LO work (it does not currently)
"""
import copy
import httplib2
import logging
import oauth2 as oauth
import urllib
import urlparse

from oauth2client.anyjson import simplejson
from oauth2client.client import Credentials
from oauth2client.client import Flow
from oauth2client.client import Storage
try:
  from urlparse import parse_qsl
except ImportError:
  from cgi import parse_qsl

class Error(Exception):
  """Base error for this module."""
  pass


class RequestError(Error):
  """Error occurred during request."""
  pass


class MissingParameter(Error):
  pass


class CredentialsInvalidError(Error):
  pass

class TwoLeggedOAuthCredentials(Credentials):
  """Two Legged Credentials object for OAuth 1.0a.

  The Two Legged object is created directly, not from a flow.  Once you
  authorize and httplib2.Http instance you can change the requestor and that
  change will propogate to the authorized httplib2.Http instance. For example:

    http = httplib2.Http()
    http = credentials.authorize(http)

    credentials.requestor = 'foo@example.info'
    http.request(...)
    credentials.requestor = 'bar@example.info'
    http.request(...)
  """

  def __init__(self, consumer_key, consumer_secret, user_agent):
    """
    Args:
      consumer_key: string, An OAuth 1.0 consumer key
      consumer_secret: string, An OAuth 1.0 consumer secret
      user_agent: string, The HTTP User-Agent to provide for this application.
    """
    self.consumer = oauth.Consumer(consumer_key, consumer_secret)
    self.user_agent = user_agent
    self.store = None

    # email address of the user to act on the behalf of.
    self._requestor = "jenso1988@gmail.com"

  @property
  def invalid(self):
    """True if the credentials are invalid, such as being revoked.

    Always returns False for Two Legged Credentials.
    """
    return False

  def getrequestor(self):
    return self._requestor

  def setrequestor(self, email):
    self._requestor = email

  requestor = property(getrequestor, setrequestor, None,
      'The email address of the user to act on behalf of')

  def set_store(self, store):
    """Set the storage for the credential.

    Args:
      store: callable, a callable that when passed a Credential
        will store the credential back to where it came from.
        This is needed to store the latest access_token if it
        has been revoked.
    """
    self.store = store

  def __getstate__(self):
    """Trim the state down to something that can be pickled."""
    d = copy.copy(self.__dict__)
    del d['store']
    return d

  def __setstate__(self, state):
    """Reconstitute the state of the object from being pickled."""
    self.__dict__.update(state)
    self.store = None

  def authorize(self, http):
    """Authorize an httplib2.Http instance with these Credentials

    Args:
       http - An instance of httplib2.Http
           or something that acts like it.

    Returns:
       A modified instance of http that was passed in.

    Example:

      h = httplib2.Http()
      h = credentials.authorize(h)

    You can't create a new OAuth
    subclass of httplib2.Authenication because
    it never gets passed the absolute URI, which is
    needed for signing. So instead we have to overload
    'request' with a closure that adds in the
    Authorization header and then calls the original version
    of 'request()'.
    """
    request_orig = http.request
    signer = oauth.SignatureMethod_HMAC_SHA1()

    # The closure that will replace 'httplib2.Http.request'.
    def new_request(uri, method='GET', body=None, headers=None,
                    redirections=httplib2.DEFAULT_MAX_REDIRECTS,
                    connection_type=None):
      """Modify the request headers to add the appropriate
      Authorization header."""
      response_code = 302
      http.follow_redirects = False
      while response_code in [301, 302]:
        # add in xoauth_requestor_id=self._requestor to the uri
        if self._requestor is None:
          raise MissingParameter(
              'Requestor must be set before using TwoLeggedOAuthCredentials')
        parsed = list(urlparse.urlparse(uri))
        q = parse_qsl(parsed[4])
        q.append(('xoauth_requestor_id', self._requestor))
        parsed[4] = urllib.urlencode(q)
        uri = urlparse.urlunparse(parsed)

        req = oauth.Request.from_consumer_and_token(
            self.consumer, None, http_method=method, http_url=uri)
        req.sign_request(signer, self.consumer, None)
        if headers is None:
          headers = {}
        headers.update(req.to_header())
        if 'user-agent' in headers:
          headers['user-agent'] = self.user_agent + ' ' + headers['user-agent']
        else:
          headers['user-agent'] = self.user_agent
        resp, content = request_orig(uri, method, body, headers,
                            redirections, connection_type)
        response_code = resp.status
        if response_code in [301, 302]:
          uri = resp['location']

      if response_code == 401:
        print content
        logging.info('Access token no longer valid: %s' % content)
        # Do not store the invalid state of the Credentials because
        # being 2LO they could be reinstated in the future.
        raise CredentialsInvalidError("Credentials are invalid.")

      return resp, content

    http.request = new_request
    return http


#credentials = TwoLeggedOAuthCredentials("stylematch.se", "xXZorjXlIz2Vm9Glyhgx9jzG", 'stylematchs')
# test to get it to work with Simple API key
#return build('analytics', 'v3', http=http, developerKey="AIzaSyDA3wWYlEqxN178D42MBkL2wcZwZCCtqwk")


# END 2LO


import logging
import os
import sys
from apiclient.discovery import build
import gflags
import httplib2
import oauth2 as oauth
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run
from oauth2client.client import Credentials

FLAGS = gflags.FLAGS

# CLIENT_SECRETS, name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret. You get these values by
# creating a new project in the Google APIs console and registering for
# OAuth2.0 for installed applications: <https://code.google.com/apis/console>
CLIENT_SECRETS = 'client_secrets.json'


# Helpful message to display in the browser if the CLIENT_SECRETS file
# is missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the APIs Console <https://code.google.com/apis/console>.

""" % os.path.join(os.path.dirname(__file__), CLIENT_SECRETS)
asd = os.path.join(os.path.dirname(__file__), CLIENT_SECRETS)
# Set up a Flow object to be used if we need to authenticate.
FLOW = flow_from_clientsecrets(asd,
    scope='https://www.googleapis.com/auth/analytics.readonly',
    message=MISSING_CLIENT_SECRETS_MESSAGE)

# The gflags module makes defining command-line options easy for applications.
# Run this program with the '--help' argument to see all the flags that it
# understands.
gflags.DEFINE_enum('logging_level', 'ERROR',
                   ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                   'Set the level of logging detail.')

#gflags.DEFINE_boolean('auth_local_webserver', False,
#                      ('Run a local web server to handle redirects during '
#                       'OAuth authorization.'))

# Name of file that will store the access and refresh tokens to access
# the API without having to login each time. Make sure this file is in
# a secure place.
# TODO: This filename shouldnt be hardcoded
TOKEN_FILE_NAME = '../analytics.dat'


def process_flags(argv):
    """Uses the command-line flags to set the logging level.

    Args:
      argv: List of command line arguments passed to the python script.
    """
    # Let the gflags module process the command-line arguments.
    try:
        argv = FLAGS(argv)
    except gflags.FlagsError, e:
        print '%s\nUsage: %s ARGS\n%s' % (e, argv[0], FLAGS)
        sys.exit(1)

        # Set the logging according to the command-line flag.
        logging.getLogger().setLevel(getattr(logging, FLAGS.logging_level))


def service_auth():
    """
    Service authentication doesnt work with Google analytics / Core reporting
    api at the moment.
    TODO: Use this when Google analytics api accept service authentication
    """
    from oauth2client.client import SignedJwtAssertionCredentials
    f = file('8e0706de8908522bcf58bd475b9e6cc638294571-privatekey.p12', 'rb')

    key = f.read()
    f.close()
    
    # Create an httplib2.Http object to handle our HTTP requests and authorize it
    # with the Credentials. Note that the first parameter, service_account_name,
    # is the Email address created for the Service account. It must be the email
    # address associated with the key that was created.
    credentials = SignedJwtAssertionCredentials(
        '854546516036-ndecnttg9u84f4t0jf9jdr0054jle8ug.apps.googleusercontent.com',
        key,
        scope='https://www.googleapis.com/auth/analytics.readonly')
    return credentials

def client_auth():
    # Prepare credentials, and authorize HTTP object with them.
    storage = Storage(TOKEN_FILE_NAME)
    credentials = storage.get()
    # remove this? to not get people to try to auth
    if credentials is None or credentials.invalid:
        logging.getLogger().critical("Either we dont have a analytics.dat "
                                     "file or it has expired. The analytics.dat"
                                     "file is used to connect to the Core"
                                     "reporting api.")
        # uncomment the following line, to allow authentication (with the browser)
        #credentials = run(FLOW, storage)
        
    return credentials

def initialize_service():
    """Returns an instance of service from discovery data and does auth.

    This method tries to read any existing OAuth 2.0 credentials from the
    Storage object. If the credentials do not exist, new credentials are
    obtained. The crdentials are used to authorize an http object. The
    http object is used to build the analytics service object.

    Returns:
    An analytics v3 service object.
    """

    # Create an httplib2.Http object to handle our HTTP requests.
    http = httplib2.Http()

    credentials = client_auth()
    http = credentials.authorize(http)
    
    # Retrieve service.
    return build('analytics', 'v3', http=http)
