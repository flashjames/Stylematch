from django.conf import settings  
  
import gdata.analytics.client  
from gdata.sample_util import CLIENT_LOGIN, SettingsUtil
import os

# Set the DJANGO_SETTINGS_MODULE environment variable.
#os.environ['DJANGO_SETTINGS_MODULE'] = "settings"

"""
Always set in your environment:
export DJANGO_SETTINGS_MODULE=yoursite.settings
http://www.b-list.org/weblog/2007/sep/22/standalone-django-scripts/
"""

  
gdata_client = gdata.analytics.client.AnalyticsClient(  
    source=settings.GOOGLE_ANALYTICS_APP_NAME  
    )  
  
def _login():  
      
    settings_util = SettingsUtil(prefs={  
        "email": settings.GOOGLE_ANALYTICS_USER_EMAIL,  
        "password": settings.GOOGLE_ANALYTICS_USER_PASS,  
    })  
    settings_util.authorize_client(  
        gdata_client,  
        service=gdata_client.auth_service,  
        auth_type=CLIENT_LOGIN,  
        source=settings.GOOGLE_ANALYTICS_APP_NAME,   
        scopes=['https://www.google.com/analytics/feeds/']  
        )  
          
def get_views(year, week):  
      
    _login()          
    data_query = gdata.analytics.client.DataFeedQuery({  
        'ids': settings.GOOGLE_ANALYTICS_TABLE_ID,  
        'start-date': '2010-10-01',  
        'end-date': '2100-01-01',  
        'dimensions': 'ga:customVarValue3,ga:customVarValue4,ga:week',  
        'metrics': 'ga:pageviews',  
        'filters': 'ga:customVarValue4==Job,ga:customVarValue4==Profile;ga:week==%s;ga:year==%s' % (week, year),  
        'max-results': "10000"  
        })  
          
    return gdata_client.GetDataFeed(data_query)  

print get_views(2012, 5)
