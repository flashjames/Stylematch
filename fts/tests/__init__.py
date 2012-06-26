from django.conf import settings

try:
    skiptest = settings.SKIP_FTS_TESTS
except:
    skiptest = False

if not skiptest:
    from tests import *
