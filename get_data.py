import csv
import re
import datetime
import convert_date


# This script will:
#   * Create the initial py_data object
#   * Populate it with default values from the config file
#   * Create the areas and depts lists
#   * Create the research active staff list

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
        "phd_persons": {},
        "phd_staff": {}
    }

    staff = {}

    # Take the data line by line:
    for d in data:

        # Flag to determine whether or not to include a staff member:
        process = True

        # Identify duplicate entries:
        if d["ResID"] in staff:
        
            # If we have a duplicate staff entry, only process the data if
            # the "Main position" value is other than 0:
            if d["main_position"] == "0":
                process = False
                #print(f"Skipping {d['ResID']} - not main position.")
            
        # No visiting profs etc.:
        if d["POSITION"].startswith("Visiting") or d["DEPT_NAME"].startswith("Visting"):
            process = False
            #print(f"Skipping {d['ResID']} - visiting role.")
        
        # Email is required
        # In past, we've had single-space 'empty' email data, so also check for that.
        if not d["EMAIL"] or d["EMAIL"].strip() == "":
            process = False
            #print(f"Skipping {d['ResID']} - no email address.")

        if process:
            
            # Add area code, if new:
            if d["AREA CODE"] not in py_data["areas"]:
                py_data["areas"][d["AREA CODE"]] = {
                    "name": d["AREA NAME"],
                    "parent": config.uon_id,
                    "type": "faculty",
                    "start_date": config.start_date
                }
            
            # Add dept, if new:
            if d["DEPARTMENT"] not in py_data["depts"]:
                py_data["depts"][d["DEPARTMENT"]] = {
                    "name": d["DEPT_NAME"],
                    "parent": d["AREA CODE"],
                    "type": "department",
                    "start_date": config.start_date
                }
            
            # Convert date, using first ten chars (omit time):
            uni_start_date = convert_date.convert(d['START_DATE'][0:10], config.start_date)
            uni_end_date = convert_date.convert(d['END_DATE'][0:10], config.end_date)
            div_start_date = convert_date.convert(d['POSITION_DATE_FROM'][0:10], config.start_date)
            div_end_date = convert_date.convert(d['POSITION_DATE_TO'][0:10], config.end_date)

            # FTE in HR data uses many decimal places, here we trim it to two.
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
                "uni_end_date": uni_end_date,
                "div_start_date": div_start_date,
                "div_end_date": div_end_date,
                "area_code": d["AREA CODE"].strip(),
                "area": d["AREA NAME"].strip(),
                "dept_code": d["DEPARTMENT"].strip(),
                "dept": d["DEPT_NAME"].strip(),
                "fte": d["FTE"][0:4]
            }
    
    # With staff data in place, we can process students:
    with open(config.phd_source, "r") as f:
        reader = csv.DictReader(f)
        # Skip headers:
        #next(reader, None)
        phd_data = list(reader)

    # A list of our various complaints:
    problems = []

    for d in phd_data:
        # Grab resid and remove leading zeros:
        resid = d["RESID"].strip()
        resid = re.sub(r"^0*","",resid)

        # Catch non-numeric IDs:
        if not resid.isdigit():
            problems.append({
                    "ResId": resid,
                    "studentid": d["STUDENT_ID"],
                    "forenames": d["FORENAMES"],
                    "surname": d["SURNAME"],
                    "email": d["EMAIL"],
                    "problem": "Unusable name-based resid - excluded."
                })
            continue

        # Catch records with no start date included:
        if not d["START_DATE"]:
           problems.append({
                "ResId": resid,
                "studentid": d["STUDENT_ID"],
                "forenames": d["FORENAMES"],
                "surname": d["SURNAME"],
                "email": d["EMAIL"],
                "problem": "No start date provided."
           })
           # Skip to next record:
           continue
        
        # Pad out the resid to 8 digits (for PhDs with staff IDs):
        padded_id = resid.rjust(8, "0")

        # Staff ids will be under 8 digits and have a leading 0 in the padded version:
        if len(resid) < 8 and padded_id[0] == "0":
            # Check if already added during staff phase:
            if resid in py_data["persons"]:
                problems.append({
                    "ResId": resid,
                    "studentid": d["STUDENT_ID"],
                    "forenames": d["FORENAMES"],
                    "surname": d["SURNAME"],
                    "email": d["EMAIL"],
                    "problem": "Staff ResId already found in staff data. Record excluded."
                })
                # Add the PhD data we need to phd_staff list:
                # First, flip the start date to Pure format:
                startdate_obj = datetime.datetime.strptime(d["START_DATE"], "%d/%m/%Y")
                startdate = startdate_obj.strftime("%Y-%m-%d")
                py_data["phd_staff"][resid] = {
                    "email": d["EMAIL"].strip(),
                    "description": d["COURSE_DES"].strip(),
                    "code": d["COURSE_CODE"].strip().upper(),
                    "startdate": startdate
                }
                # Skip to next record:
                continue

            # If not already added as staff, it's OK to add as PhD.
            else:
                # We'll still log:
                problems.append({
                    "ResId": resid,
                    "studentid": d["STUDENT_ID"],
                    "forenames": d["FORENAMES"],
                    "surname": d["SURNAME"],
                    "email": d["EMAIL"],
                    "problem": "Staff ResId, but not found in staff import data. Included, but may need checking."
                })

        # If we get this far, we've probably got a student.
        # Flip the start date to Pure format:
        startdate_obj = datetime.datetime.strptime(d["START_DATE"], "%d/%m/%Y")
        startdate = startdate_obj.strftime("%Y-%m-%d")

        # Build the person record
        # Stripping all fields just in case, based on previous data:
        #py_data["phd_persons"][d["ResId"].strip()] = {
        py_data["phd_persons"][resid] = {
            "title": d["INITCAP(A.TITLE)"].strip(),
            "first_name": d["FORENAMES"].strip(),
            "surname": d["SURNAME"].strip(),
            "email": d["EMAIL"].strip(),
            "description": d["COURSE_DES"].strip(),
            "code": d["COURSE_CODE"].strip().upper(),
            "startdate": startdate
        }

        # CSV export of problems:
        with open(f"{config.output_folder}/{config.phd_problem_file}", 'w', newline='') as csvfile:
            fieldnames = problems[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            for row in problems:
                writer.writerow(row)

    return py_data
