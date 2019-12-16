
from time import strptime

def convert(date, default):
    # Convert UON format (31/01/2018) to Pure format (2018-01-31):
    date_parts = date.split("/")
    date_parts.reverse()
    new_date = "-".join(date_parts)
    # Also clamp any dates earlier than the default start date:
    if strptime(new_date, "%Y-%m-%d") < strptime(default, "%Y-%m-%d"):
        return default
    else:
        return new_date