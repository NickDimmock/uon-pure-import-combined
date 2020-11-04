import csv
import re
import datetime
import convert_date
import create_id_lookup

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

    # Note logging:
    notes = open(f"{config.output_folder}/{config.data_notes_file}", "w")

    # Create our staff login to employee ID lookup table:
    login_to_id = create_id_lookup.create()

    # Create starting data, including root UON info from config and phd data:
    py_data = {
        "areas": config.uon_data,
        "depts": {},
        "persons": {},
        "phd_persons": {},
        "phd_staff": {}
    }

    staff = {}

    # Keep track of already filtered areas:
    filtered_areas = []

    # Take the data line by line:
    for d in data:

        # Flag to determine whether or not to include a staff member:
        process = True
        
        

        if d["AREA_CODE"] in config.dept_blacklist:
            if d["AREA_CODE"] not in filtered_areas:
                notes.write(f"Blacklisted area code: {d['AREA_CODE']}.\n")
                filtered_areas.append(d["AREA_CODE"])
            process = False

        # Use MAIN_RESID column for resid value, to ensure staff given newer RESID
        # values can still log in:

        staff_resid = d["MAIN_RESID"]

        # Identify duplicate staff entries:
        if staff_resid in py_data["persons"]:
            # If we have a duplicate staff entry, only process the data if
            # the "Main position" value is other than 0:
            if d["MAIN_POSITION"] == "0":
                process = False
                notes.write(f"Skipping {staff_resid} - not main position ({d['EMAIL']}).\n")
            # Otherwise we have duplicate main positions and are overwriting the
            # previous one. This may fix default date of birth rows - proceed,
            # but log it:
            else:
                notes.write(f"Duplicate main position found for {staff_resid} ({d['EMAIL']}).\n")

        # No visiting profs etc.:
        if d["POSITION"].startswith("Visiting") or d["DEPARTMENT_NAME"].startswith("Visting"):
            process = False
            #print(f"Skipping {staff_resid} - visiting role.")
        
        # Email is required
        # In past, we've had single-space 'empty' email data, so also check for that.
        if not d["EMAIL"] or d["EMAIL"].strip() == "":
            process = False
            notes.write(f"Skipping {staff_resid} - no email address ({d['FORENAMES']} {d['SURNAME']}).\n")

        if process:
            # Add area code, if new:
            if d["AREA_CODE"] not in py_data["areas"]:
                py_data["areas"][d["AREA_CODE"]] = {
                    "name": d["AREA_NAME"],
                    "parent": config.uon_id,
                    "type": "faculty",
                    "start_date": config.start_date
                }
            
            # Add dept, if new:
            if d["DEPARTMENT"] not in py_data["depts"]:
                py_data["depts"][d["DEPARTMENT"]] = {
                    "name": d["DEPARTMENT_NAME"],
                    "parent": d["AREA_CODE"],
                    "type": "department",
                    "start_date": config.start_date
                }
            
            # Convert date, using first ten chars (omit time):
            uni_start_date = convert_date.convert(d['START_DATE'][0:10], config.start_date)
            uni_end_date = convert_date.convert(d['END_DATE'][0:10], config.end_date)
            div_start_date = convert_date.convert(d['POSITION_DATE_FROM'][0:10], config.start_date)
            div_end_date = convert_date.convert(d['POSITION_DATE_TO'][0:10], config.end_date)

            # HESA ID should be 13 chars, but data may strip leading zeroes.
            # Pad them back in if necessary:
            hesa_id = d['HESA_ID'].strip().rjust(13, "0")

            # Make sure date of birth is sensible.
            # Pure specifies dd-mm-yyyy,  our data uses dd/mm/yyyy
            # DoB will be blank unless it's included in the CSV data and
            # matches the format dd/mm/yyyy.
            date_of_birth = ""
            if len(d["DATE_OF_BIRTH"]):
                if re.match("^\d{2}/\d{2}/\d{4}", d["DATE_OF_BIRTH"]):
                    date_of_birth = d["DATE_OF_BIRTH"].replace("/","-")
                else:
                    notes.write(f"DoB format mismatch: {d['DATE_OF_BIRTH']} for {staff_resid} ({d['EMAIL']}).\n")
                if date_of_birth[0:10] == "01/01/1900":
                    notes.write(f"Default DoB found for {staff_resid} ({d['EMAIL']}).\n")

            # FTE in HR data may use many decimal places, here we trim it to two.
            # But it's a string! So we just have to truncate to four characters...
            # Also, some name values have trailing spaces, so best to strip the lot.

            py_data["persons"][staff_resid] = {
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
                "area_code": d["AREA_CODE"].strip(),
                "area": d["AREA_NAME"].strip(),
                "dept_code": d["DEPARTMENT"].strip(),
                "dept": d["DEPARTMENT_NAME"].strip(),
                "fte": d["FTE"][0:4],
                "hesa_id": hesa_id,
                "date_of_birth": date_of_birth
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
        # Grab resid and remove leading zeros. Note we only have a RESID column here (no MAIN_RESID):
        phd_resid = d["RESID"].strip()
        phd_resid = re.sub(r"^0*", "", phd_resid)

        # Catch non-numeric IDs:
        if not phd_resid.isdigit():
            if phd_resid.lower() in login_to_id:
                # If we can match the non-numeric ID in the PhD lopkup table,
                # patch in the associated resid for use later.
                print(f"Found a missing PhD login for {phd_resid}!")
                phd_resid = login_to_id[phd_resid.lower()]
            else:
                # Otherwise, we can't really do much - just log the mismatch and skip this record:
                print(f"Didn't find a missing PhD login for {phd_resid} :(")
                problems.append({
                        "ResId": phd_resid,
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
                "ResId": phd_resid,
                "studentid": d["STUDENT_ID"],
                "forenames": d["FORENAMES"],
                "surname": d["SURNAME"],
                "email": d["EMAIL"],
                "problem": "No start date provided."
           })
           # Skip to next record:
           continue
        
        # Pad out the resid to 8 digits (for PhDs with staff IDs):
        padded_id = phd_resid.rjust(8, "0")

        # Staff ids will be under 8 digits and have a leading 0 in the padded version:
        if len(phd_resid) < 8 and padded_id[0] == "0":
            # Check if already added during staff phase:
            if phd_resid in py_data["persons"]:
                problems.append({
                    "ResId": phd_resid,
                    "studentid": d["STUDENT_ID"],
                    "forenames": d["FORENAMES"],
                    "surname": d["SURNAME"],
                    "email": d["EMAIL"],
                    "problem": "Staff ResId found - adding PhD details to existing staff record."
                })
                # Add the PhD data we need to phd_staff list:
                # First, flip the start date to Pure format:
                startdate_obj = datetime.datetime.strptime(d["START_DATE"], "%d/%m/%Y")
                startdate = startdate_obj.strftime("%Y-%m-%d")
                py_data["phd_staff"][phd_resid] = {
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
                    "ResId": phd_resid,
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
        py_data["phd_persons"][padded_id] = {
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

    notes.close()

    return py_data
