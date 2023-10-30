import csv
import re
import datetime
import logging
import convert_date
import create_id_lookup

# This script will:
#   * Create the initial py_data object
#   * Populate it with default values from the config file
#   * Create the areas and depts lists
#   * Create the research active staff list


# Set contract type from HESA_FUNCTION id
def get_contract_type(id):
    contractTypes = {
        "NULL": "non_academic",
        "1": "academic_teaching_and_scholarship",
        "2": "academic_research_only",
        "3": "academic_teaching_and_research",
        "4": "non_academic",
        "9": "academic_other",
    }
    if id in contractTypes.keys():
        return contractTypes[id]
    else:
        return False


# Function to set title classification value.
# Miss/Mr/Mrs/Ms are 'designation'
# All other values are assumed to be 'prenominal'
# (e.g. Dr / Prof / Father)
def get_title_class(title):
    designationTitles = ["Miss", "Mr", "Mrs", "Ms"]
    if title in designationTitles:
        return "designation"
    else:
        return "prenominal"


def get(config):
    # Read in the staff and org CSV data:
    with open(config.staff_source, "r") as f:
        reader = csv.DictReader(f)
        data = list(reader)

    # Create our staff login to employee ID lookup table:
    login_to_id = create_id_lookup.create()

    # Array to caputre RESID and MAIN_RESID values - used during PhD stage
    # to link staff / student accounts:
    used_resids = []

    # Associated dict to map RESID to MAIN_RESID value, where the two differ:
    resid_map = {}

    # Create starting data, including root UON info from config and phd data:
    py_data = {
        "areas": config.uon_data,
        "depts": {},
        "persons": {},
        "phd_persons": {},
        "phd_staff": {},
    }

    # Keep track of already filtered areas:
    filtered_areas = []

    # Take the data line by line:
    for d in data:
        # Flag to determine whether or not to include a staff member:
        process = True

        if d["AREA_CODE"] in config.dept_blacklist:
            if d["AREA_CODE"] not in filtered_areas:
                logging.info(
                    "%s,%s,Skipped - blacklisted area code (%s)",
                    d["RESID"],
                    d["EMAIL"],
                    d["AREA_CODE"],
                )
                filtered_areas.append(d["AREA_CODE"])
            process = False

        # Identify duplicate staff entries:
        if d["RESID"] in py_data["persons"]:
            # If we have a duplicate staff entry, only process the data if
            # the "Main position" value is other than 0:
            if d["MAIN_POSITION"] == "0":
                process = False
                logging.info(
                    "%s,%s,Skipped - not main position", d["RESID"], d["EMAIL"]
                )
            # Otherwise we have duplicate main positions and are overwriting the
            # previous one. This may fix default date of birth rows - proceed, but log it:
            else:
                logging.info(
                    "%s,%s,Skipped - duplicate main position", d["RESID"], d["EMAIL"]
                )

        # No visiting profs etc.:
        if d["POSITION"].startswith("Visiting") or d["DEPARTMENT_NAME"].startswith(
            "Visting"
        ):
            process = False
            logging.info("%s,%s,Skipped - visiting role", d["RESID"], d["EMAIL"])

        # Email is required
        # In past, we've had single-space 'empty' email data, so also check for that.
        if not d["EMAIL"] or d["EMAIL"].strip() == "":
            process = False
            logging.warning(
                "%s,N/A,Skipped - no email address for %s %s",
                d["RESID"],
                d["FORENAMES"],
                d["SURNAME"],
            )

        # Get value for HESA_FUNCTION ID:
        if d["HESA_FUNCTION"]:
            contract_type = get_contract_type(d["HESA_FUNCTION"].strip())
            if not contract_type:
                contract_type = ""
                logging.warning(
                    "%s,%s,Unsupported HESA contract type (%s)",
                    d["RESID"],
                    d["EMAIL"],
                    d["HESA_FUNCTION"],
                )
        else:
            contract_type = ""

        if process:
            # Store RESIDs for later reference:
            used_resids.append(d["RESID"])
            # Also store & map MAIN_RESID if the values differ:
            if d["RESID"] != d["MAIN_RESID"]:
                used_resids.append(d["MAIN_RESID"])
                resid_map[d["MAIN_RESID"]] = d["RESID"]

            # Add area code, if new:
            if d["AREA_CODE"] not in py_data["areas"]:
                py_data["areas"][d["AREA_CODE"]] = {
                    "name": d["AREA_NAME"],
                    "parent": config.uon_id,
                    "type": "faculty",
                    "start_date": config.start_date,
                }

            # Add dept, if new:
            if d["DEPARTMENT"] not in py_data["depts"]:
                py_data["depts"][d["DEPARTMENT"]] = {
                    "name": d["DEPARTMENT_NAME"],
                    "parent": d["AREA_CODE"],
                    "type": "department",
                    "start_date": config.start_date,
                }

            # Convert date, using first ten chars (omit time):
            uni_start_date = convert_date.convert(
                d["START_DATE"][0:10], config.start_date
            )
            uni_end_date = convert_date.convert(d["END_DATE"][0:10], config.start_date)
            div_start_date = convert_date.convert(
                d["POSITION_DATE_FROM"][0:10], config.start_date
            )
            div_end_date = convert_date.convert(
                d["POSITION_DATE_TO"][0:10], config.start_date
            )

            # Staff without HESA IDs will just have a single zero.
            # We want to avoid these.
            # Real HESA ID should be 13 chars, but data may strip leading zeroes,
            # so we need to pad them back to 13 if necessary.
            if d["HESA_ID"] == "0":
                hesa_id = False
            else:
                hesa_id = d["HESA_ID"].strip().rjust(13, "0")

            # Make sure date of birth is sensible.
            # Pure specifies dd-mm-yyyy,  our data uses dd/mm/yyyy
            # DoB will be blank unless it's included in the CSV data and
            # matches the format dd/mm/yyyy.
            date_of_birth = ""
            if len(d["DATE_OF_BIRTH"]):
                if re.match("^\d{2}/\d{2}/\d{4}", d["DATE_OF_BIRTH"]):
                    date_of_birth = d["DATE_OF_BIRTH"].replace("/", "-")
                else:
                    logging.WARNING(
                        "%s,%s,Date of birth formatting error (%s)",
                        d["RESID"],
                        d["EMAIL"],
                        d["DATE_OF_BIRTH"],
                    )
                if date_of_birth[0:10] == "01/01/1900":
                    logging.warning(
                        "%s,%s,Record uses default date of birth (01/01/1900)",
                        d["RESID"],
                        d["EMAIL"],
                    )

            # Establish classification for title:
            title = d["TITLE"].strip()
            titleClass = get_title_class(title)

            # FTE in HR data may use many decimal places, here we trim it to two.
            # But it's a string! So we just have to truncate to four characters...
            # Also, some name values have trailing spaces, so best to strip the lot.
            # Now including MAIN_RESID for use as user account ID, to enable access
            # for academic staff who've been assinged new resid values.
            py_data["persons"][d["RESID"]] = {
                "user_id": d["MAIN_RESID"].strip(),
                "first_name": d["FORENAMES"].strip(),
                "surname": d["SURNAME"].strip(),
                "known_as_first": d["FAMILIAR_NAME"].strip(),
                "known_as_last": d["SURNAME"].strip(),
                "title": title,
                "title_class": titleClass,
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
                "contract_type": contract_type,
                "date_of_birth": date_of_birth,
                "visibility": config.staff_visibility,
            }

    # With staff data in place, we can process students:
    with open(config.phd_source, "r") as f:
        reader = csv.DictReader(f)
        # Skip headers:
        # next(reader, None)
        phd_data = list(reader)

    # A list of our various complaints:
    problems = []

    # Set temporary start date for PhDs to 1 Jan this year.
    # We need to create this as dd/mm/yyyy, as it will be updated to the
    # expected Pure format later, along with all other start dates.
    phd_default_start_date = datetime.date.today().strftime("01/01/%Y")

    # No end date is provided for PhDs, but if someone has left and
    # restarted in some way, Pure will set one - so we need to provide
    # a value to override any dates added by Pure.
    # We can use the Pure date format directly here:
    phd_default_end_date = "2099-12-31"

    for d in phd_data:
        # Grab resid and remove leading zeros:
        resid = d["RESID"].strip()
        resid = re.sub(r"^0*", "", resid)

        # Course decriptions arrive in quotes - remove these:
        d["COURSE_DES"] = re.sub(r"^\"(.*)\"$", r"\1", d["COURSE_DES"])

        # Catch non-numeric IDs:
        if not resid.isdigit():
            if resid.lower() in login_to_id:
                # If we can match the non-numeric ID in the PhD lopkup table,
                # patch in the associated resid for use later.
                resid = login_to_id[resid.lower()]
                logging.info(
                    "%s,%s,Missing PhD login found and added", resid, d["EMAIL"]
                )

            else:
                # Otherwise, we can't really do much - just log the mismatch and skip this record:
                logging.warning(
                    "%s,%s,Skipped - Unusable name-based resid", resid, d["EMAIL"]
                )
                continue

        # Catch records with no start date included and use a temporary date:

        if not d["START_DATE"]:
            logging.info(
                "%s,%s,No PhD start date provided - used %s",
                resid,
                d["EMAIL"],
                phd_default_start_date,
            )
            # Add new date to data:
            d["START_DATE"] = phd_default_start_date

        # Pad out the resid to 8 digits (for PhDs with staff IDs):
        padded_id = resid.rjust(8, "0")

        # Staff ids will be under 8 digits and have a leading 0 in the padded version:
        if len(resid) < 8 and padded_id[0] == "0":
            # Check if already added during staff phase:
            # if resid in py_data["persons"]:
            if resid in used_resids:
                # Need to work out whether the staff member was recorded using
                # RESID or MAIN_RESID, and use this value to record the new info:
                phd_staff_resid = None
                # Easy win if the resis is already a key in the persons data:
                if resid in py_data["persons"]:
                    phd_staff_resid = resid
                # Otherwhise check for a MAIN_RESID alias in the map we created earlier:
                elif resid in resid_map:
                    phd_staff_resid = resid_map[resid]
                # If neither of those worked, something has gone wrong - log and skip:
                if phd_staff_resid is None:
                    logging.warning(
                        "%s,%s,Skipped - staff resid found for PhD, but error matching to staff data",
                        resid,
                        d["EMAIL"],
                    )
                    continue

                # If we get here, we don't really have a problem, but we log the
                # fact we've matched a PhD record to a staff ID:
                logging.info(
                    "%s,%s,Staff resid found - adding PhD details to staff record",
                    resid,
                    d["EMAIL"],
                )
                # Add the PhD data we need to phd_staff list:
                # First, flip the start date to Pure format:
                startdate_obj = datetime.datetime.strptime(d["START_DATE"], "%d/%m/%Y")
                startdate = startdate_obj.strftime("%Y-%m-%d")
                py_data["phd_staff"][phd_staff_resid] = {
                    "email": d["EMAIL"].strip(),
                    "description": d["COURSE_DES"].strip(),
                    "code": d["COURSE_CODE"].strip().upper(),
                    "startdate": startdate,
                    "enddate": phd_default_end_date,
                }
                # Skip to next record:
                continue

            # If not already added as staff, it's OK to add as PhD.
            else:
                # We'll still log:
                logging.warning(
                    "%s,%s,Staff resid for PhD not found in staff data - may need checking",
                    resid,
                    d["EMAIL"],
                )

        # If we get this far, we've probably got a student.
        # Flip the start date to Pure format:
        startdate_obj = datetime.datetime.strptime(d["START_DATE"], "%d/%m/%Y")
        startdate = startdate_obj.strftime("%Y-%m-%d")

        # Establish classification for title:
        title = d["INITCAP(A.TITLE)"].strip()
        titleClass = get_title_class(title)

        # Build the person record
        # Stripping all fields just in case, based on previous data.
        py_data["phd_persons"][padded_id] = {
            "title": title,
            "title_class": titleClass,
            "first_name": d["FORENAMES"].strip(),
            "surname": d["SURNAME"].strip(),
            "email": d["EMAIL"].strip(),
            "description": d["COURSE_DES"].strip(),
            "code": d["COURSE_CODE"].strip().upper(),
            "startdate": startdate,
            "enddate": phd_default_end_date,
            "visibility": config.phd_visibility,
        }

    return py_data
