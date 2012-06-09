

def format_minutes_to_hhmm(minutes):
    """
    Formats minutes passed in a day ('dygn') into HH:MM format
    where H is hour and M is minute.
    """
    output_str = ""
    if minutes >= 0:

        hours = minutes / 60
        minutes_remaining = minutes - (hours * 60)

        output_str = str(hours).zfill(2) + ":" + str(minutes_remaining).zfill(2)

    return output_str


def format_minutes_to_pretty_format(minutes):

    """
    Formats minutes into a pretty format:
    Ex:
        1 timme 15 minuter.
        10 timmar 45 minuter.
    """

    output_str = ""
    if minutes >= 0:
        hours = minutes / 60
        minutes_remaining = minutes - (hours * 60)

        if hours >= 1:
            output_str += str(hours) + " "
            if hours == 1:
                output_str += "timme"
            else:
                output_str += "timmar"
            output_str += " "

        if minutes_remaining >= 1:
            output_str += str(minutes_remaining) + " "
            if minutes_remaining == 1:
                output_str += "minut"
            else:
                output_str += "minuter"

    return output_str.strip()


def list_with_time_interval(start=0, stop=60* 24, interval=30,
                            format_function=format_minutes_to_hhmm):
    """
    Generate a list of tuples with minutes occuring between start and
    stop with correct interval and a string generated from
    format_function.
    """
    # basic error checks
    if interval <= 0 or start > stop:
        return []

    times = []
    minutes = start
    while minutes <= stop:

        output = format_function(minutes)
        times.append((minutes, output))

        minutes += interval
    return times

