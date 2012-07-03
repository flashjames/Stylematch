import sample_utils
import datetime

from apiclient.errors import HttpError
from oauth2client.client import AccessTokenRefreshError

# should be moved to Django settings
GOOGLE_ANALYTICS_PROFILE_ID = '59146773'


def get_profile_visits(profile_url="caroline"):
    # Authenticate and construct service.
    service = sample_utils.initialize_service()

    # Try to make a request to the API. Print the results or handle errors.
    try:
        results = get_url_visits(service,
                                     GOOGLE_ANALYTICS_PROFILE_ID,
                                     profile_url)
        print_results(results)
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

    return results['rows']


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
    get_profile_visits()
