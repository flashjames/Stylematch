import sample_utils
import datetime

from apiclient.errors import HttpError
from oauth2client.client import AccessTokenRefreshError

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
    Join data points, three points to one point
    """
    concated_points = []
    at_point = -1
    sum_points = 0
    print len(visit_points)
    for i in range(0,len(visit_points),3):
        if i * 3  > len(visit_points):
            break
        
        new_point = {}
        new_point['visits'] = int(visit_points[i][1]) + int(visit_points[i+1][1]) + int(visit_points[i+2][1])
        new_point['end_date'] = visit_points[i][0]
        new_point['start_date'] = visit_points[i][0]
        concated_points.append(new_point)
        
    return concated_points


def get_profile_visits(profile_url="caroline"):
    
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
    return concat_data_points(visit_points)


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
    data = [[u'20120604', u'6'], [u'20120605', u'4'], [u'20120606', u'2'], [u'20120607', u'9'], [u'20120608', u'6'], [u'20120609', u'2'], [u'20120610', u'7'], [u'20120611', u'0'], [u'20120612', u'4'], [u'20120613', u'10'], [u'20120614', u'0'], [u'20120615', u'0'], [u'20120616', u'0'], [u'20120617', u'0'], [u'20120618', u'5'], [u'20120619', u'4'], [u'20120620', u'3'], [u'20120621', u'1'], [u'20120622', u'1'], [u'20120623', u'1'], [u'20120624', u'2'], [u'20120625', u'0'], [u'20120626', u'7'], [u'20120627', u'4'], [u'20120628', u'0'], [u'20120629', u'3'], [u'20120630', u'1'], [u'20120701', u'1'], [u'20120702', u'6'], [u'20120703', u'2'], [u'20120704', u'2']]
    print concat_data_points(data)
    #get_profile_visits()
