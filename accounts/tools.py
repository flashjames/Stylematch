def generate_list_of_quarters():
    time_list = []
    
    # Calculate minutes past for every quarter of an hour
    # and generate a good looking output.
    minutes = 0
    while minutes < 60*24:

        output_str = format_minutes_to_hhmm(minutes)

        time_list.append((minutes, output_str))

        minutes += 15
    
    return time_list


def format_minutes_to_hhmm(minutes):
    """
    Formats minutes passed in a day ('dygn') into HH:MM format
    where H is hour and M is minute.
    """

    hours = minutes / 60
    minutes_remaining = minutes - (hours * 60)

    output_str = str(hours).zfill(2) + ":" + str(minutes_remaining).zfill(2) 

    return output_str
