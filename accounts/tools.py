

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
        
        if minutes_remaining != 0:
            output_str += str(minutes_remaining) + " minuter"

    

    return output_str

def generate_list_of_quarters(min_minutes = 0, minutes_max = 60*24, output_format_func = format_minutes_to_hhmm):
    """ 
    Generates a list of tuples with very fifteen minutes occuring between 
    min_minutes and minutes_max and a string generated from output_format_func.
    """    
    time_list = []
    minutes = min_minutes
    while minutes < minutes_max:

        output_str = output_format_func(minutes)
        time_list.append((minutes, output_str))

        minutes += 15
    
    return time_list

