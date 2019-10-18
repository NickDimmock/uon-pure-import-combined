import csv
import json
import get_phd_data
from time import strptime
import datetime

def get(config):

    # Read in the staff and org CSV data:
    with open(config.staff_source, "r") as f:
        reader = csv.DictReader(f)
        data = list(reader)

    # Create starting data, including root UON info from config and phd data:
    py_data = {
        "areas": config.uon_data,
        "depts": {},
        "persons": {},
        "phd_persons": {}
    }

    # List of added staff resid values, to be compared against PhD records later.
    added_staff = []

    # Take the data line by line:
    for d in data:

        # Flag to determine whether or not to include a staff member:
        process_staff = True

        # Identify duplicate entries:
        if d["ResID"] in py_data["persons"]:

            # If we have a duplicate staff entry, only process the data if
            # the "Main position" value is other than 0:
            if d["main_position"] == "0":
                process_staff = False

            # Log the duplicate in the alerts section of the data output:
            print(f"Skipping {d['ResID']} - duplicate entry.")

        # No visiting profs etc.:
        if d["POSITION"].startswith("Visiting") or d["DEPT_NAME"].startswith("Visting"):
            process_staff = False
            print(f"Skipping {d['ResID']} - visiting role.")

        # Email is required
        # In past, we've had single-space 'empty' email data, so also check for that.
        if not d["EMAIL"] or d["EMAIL"].strip() == "":
            process_staff = False
            print(f"Skipping {d['ResID']} - no email address.")

        # Only process if data is wanted:
        if process_staff:
            
            # Append ResID to our list of added records:
            added_staff.append(d['ResID'])

            # If we get here, we want to add the dept and area codes:
            if d["AREA CODE"] not in py_data["areas"]:
                py_data["areas"][d["AREA CODE"]] = {
                    "name": d["AREA NAME"],
                    "parent": config.uon_id,
                    "type": "faculty",
                    "start_date": config.start_date
                }

            if d["DEPARTMENT"] not in py_data["depts"]:
                py_data["depts"][d["DEPARTMENT"]] = {
                    "name": d["DEPT_NAME"],
                    "parent": d["AREA CODE"],
                    "type": "department",
                    "start_date": config.start_date
                }

            # Convert date, using first ten chars (omit time):
            uni_start_date = convert_date(d['START_DATE'][0:10], config.start_date)
            div_start_date = convert_date(d['POSITION_DATE_FROM'][0:10], config.start_date)

            # Note: FTE in HR data uses many decimal places, here we trim it to two.
            # But it's a string! So we just have to truncate to four characters...
            # Also, some name values have trailing spaces, so best to strip the lot.

            py_data["persons"][d["ResID"]] = {
                "first_name": d["FORENAMES"].strip(),
                "surname": d["SURNAME"].strip(),
                "known_as_first": d["FAMILIAR_NAME"].strip(),
                "known_as_last": d["SURNAME"].strip(),
                "title": d["TITLE"].strip(),
                "email": d["EMAIL"].lower().strip(),
                "role": d["POSITION"].strip(),
                "uni_start_date": uni_start_date,
                "div_start_date": div_start_date,
                "area_code": d["AREA CODE"].strip(),
                "area": d["AREA NAME"].strip(),
                "dept_code": d["DEPARTMENT"].strip(),
                "dept": d["DEPT_NAME"].strip(),
                "fte": d["FTE"][0:4]
            }

    # Get the PhD data add to data object:
    phd_data = get_phd_data.get(config, added_staff)
    py_data["phd_persons"] = phd_data["phd_persons"]

    # Grab the date:
    today = datetime.datetime.today().strftime('%Y-%m-%d')

    # Write JSON output of data for verification / checking
    with open(f"{config.archive_folder}/{config.master_json}_{today}.json", "w") as f:
        f.write(json.dumps(py_data, indent=4))

    dept_total = len(py_data["areas"])
    area_total = len(py_data["depts"])
    staff_total = len(py_data["persons"])
    phd_total = len(py_data["phd_persons"])

    print(  f"\nCreated:\n  * {staff_total} staff records\n"
            f"  * {phd_total} phd records\n"
            f"  * {dept_total} departments\n"
            f"  * {area_total} areas\n")

    # Return data as Python object:
    return py_data

def convert_date(date, default):
    # Convert UON format (31/01/2018) to Pure format (2018-01-31):
    date_parts = date.split("/")
    date_parts.reverse()
    new_date = "-".join(date_parts)
    # Also clamp any dates earlier than the default start date:
    if strptime(new_date, "%Y-%m-%d") < strptime(default, "%Y-%m-%d"):
        return default
    else:
        return new_date