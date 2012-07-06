import sample_utils
import datetime

from apiclient.errors import HttpError
from oauth2client.client import AccessTokenRefreshError
from urllib2 import urlopen, quote
from simplejson import loads


# should be moved to Django settings
GOOGLE_ANALYTICS_PROFILE_ID = '59146773'

def get_url_visits(service, ga_profile_id, url):
    """
    Get visit counts for specified url, one entry for each date.
    """
    profile_filter = 'ga:pagePath==/%s/' % (url)

    # Show visit counts for today, and the thirty previous days
    datetime_start_date = datetime.datetime.now() + datetime.timedelta(-30)
    start_date = datetime_start_date.strftime("%Y-%m-%d")
    datetime_end_date = datetime.datetime.now()
    end_date = datetime_end_date.strftime("%Y-%m-%d")

    return service.data().ga().get(
        ids='ga:' + ga_profile_id,
        start_date=start_date,
        end_date=end_date,
        metrics='ga:visitors',
        dimensions='ga:date',
        filters=profile_filter,
        start_index='1',
      max_results='32').execute()


def concat_data_points(visit_points):
    """
    Join all data points, three points to one point
    """
    concated_points = []
    sum_points = 0
    for i in range(0, len(visit_points) ,3):
        # need three data points to concentate, break the loop
        # if there's only one or two data points left
        if i + 2 >= len(visit_points):
            break

        # concentate three data points to one new point
        # and save end- and startdate, of the concentated data points
        new_point = {}
        new_point['visits'] = (int(visit_points[i][1]) +
                               int(visit_points[i+1][1]) +
                               int(visit_points[i+2][1])) 
        new_point['start_date'] = visit_points[i][0]
        new_point['end_date'] = visit_points[i+2][0]
        concated_points.append(new_point)
        
    return concated_points


def get_profile_visits(profile_url):
    # Authenticate and construct service.
    service = sample_utils.initialize_service()

    # Try to make a request to the API. Print the results or handle errors.
    try:
        results = get_url_visits(service,
                                     GOOGLE_ANALYTICS_PROFILE_ID,
                                     profile_url)
    # these exceptions should be logged to django/sentry
    except TypeError, error:
        # Handle errors in constructing a query.
        print ('There was an error in constructing your query : %s' % error)

    except HttpError, error:
        # Handle API errors.
        print ('Arg, there was an API error : %s : %s' %
               (error.resp.status, error._get_reason()))

    except AccessTokenRefreshError:
        # Handle Auth errors.
        print ('The credentials have been revoked or expired, please re-run '
               'the application to re-authorize')
    
    visit_points = results['rows']
    concated_data_points = concat_data_points(visit_points)
    return concat_data_points


def get_fb_likes(profile_url):
    try:
        content = loads(urlopen("https://api.facebook.com/method/fql.query?"+ "format=json" + "&query=" + quote("select like_count from link_stat where url='http://www.stylematch.se/carolinebergholm/'")).read())
    except:
        logging.getLogger().critical("Something is wrong with the get facebook likes query")
        return 0

    try:
        result = content[0]['like_count']
    except:
        logging.getLogger().critical("Something is wrong with the get facebook likes query")        
        result = 0
        
    return result


def print_results(results):
    """Prints out the results.

    This prints out the profile name, the column headers, and all the rows of
    data.

    Args:
    results: The response returned from the Core Reporting API.
    """

    print
    print 'Profile Name: %s' % results.get('profileInfo').get('profileName')
    print

    # Print header.
    output = []
    for header in results.get('columnHeaders'):
        output.append('%30s' % header.get('name'))
        print ''.join(output)

    # Print data table.
    if results.get('rows', []):
        for row in results.get('rows'):
            output = []
            for cell in row:
                output.append('%30s' % cell)
            print ''.join(output)

    else:
        print 'No Rows Found'


if __name__ == '__main__':
    print get_fb_likes()
