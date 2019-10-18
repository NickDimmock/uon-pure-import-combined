import csv
import json
import re
import datetime
from time import strptime

# Pass get the config, and also a list of imported staff IDs

def get(config, added_staff):

    # Set headers for CSV data:
    csv_fieldnames=[
        'rel_value',
        'student_id',
        'ResId',
        'title',
        'forenames',
        'surname',
        'email',
        'start_date',
        'division_code',
        'division_name',
        'course_code',
        'course_desc',
        'ft_pt',
        'mystery_flag'
    ]

    # Read in the CSV data:
    with open(config.phd_source, "r") as f:
        reader = csv.DictReader(f, fieldnames = csv_fieldnames)
        # Skip headers:
        next(reader, None)
        data = list(reader)

    # Create starting data, including root UON info from config:
    py_data = {
        "phd_persons": {}
    }

    # A list of our various complaints:
    problems = []

    # Take the data line by line:
    for d in data:
        resid = d["ResId"].strip()

        # Filter out name-based staff logins:
        if not resid.isdigit():
            problems.append({
                    "ResId": d['ResId'],
                    "studentid": d["student_id"],
                    "forenames": d["forenames"],
                    "surname": d["surname"],
                    "email": d["email"],
                    "problem": "Unusable name-based resid - excluded."
                })
            continue

        # Pad out the resid to 8 digits (for PhDs with staff IDs):
        padded_id = resid.rjust(8, "0")

        # Staff ids will be under 8 digits and have a leading 0 in the padded version:
        if len(resid) < 8 and padded_id[0] == "0":
            # Check if already added during staff phase:
            if resid in added_staff:
                problems.append({
                    "ResId": d['ResId'],
                    "studentid": d["student_id"],
                    "forenames": d["forenames"],
                    "surname": d["surname"],
                    "email": d["email"],
                    "problem": "Staff ResId already found in staff data. Record excluded."
                })
                # Skip to next record:
                continue
            # If not already added, just note that a staff ID has been used:
            else:
                problems.append({
                    "ResId": d['ResId'],
                    "studentid": d["student_id"],
                    "forenames": d["forenames"],
                    "surname": d["surname"],
                    "email": d["email"],
                    "problem": "Staff ResId, but not found in staff import data. Included, but may need checking."
                })

        # Catch records with no start date included:
        if not d["start_date"]:
           problems.append({
                "ResId": d['ResId'],
                "studentid": d["student_id"],
                "forenames": d["forenames"],
                "surname": d["surname"],
                "email": d["email"],
                "problem": "No start date provided."
           })
           # Skip to next record:
           continue

        # If we get this far, we've probably got a student.
        # Flip the start date to Pure format:
        startdate_obj = datetime.datetime.strptime(d["start_date"], "%d/%m/%Y")
        startdate = startdate_obj.strftime("%Y-%m-%d")

        # Build the person record
        # Stripping all fields just in case, based on previous data:
        py_data["phd_persons"][d["ResId"].strip()] = {
            "title": d["title"].strip(),
            "first_name": d["forenames"].strip(),
            "surname": d["surname"].strip(),
            "email": d["email"].strip(),
            "description": d["course_desc"].strip(),
            "startdate": startdate
        }
    
    # Get today's date:
    today = datetime.datetime.today().strftime('%Y-%m-%d')

    # CSV export of problems:
    with open(f"{config.output_folder}/{config.phd_problem_file}.csv", 'w', newline='') as csvfile:
        fieldnames = problems[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in problems:
            writer.writerow(row)
    
    # Dated CSV export of problems:
    with open(f"{config.archive_folder}/{config.phd_problem_file}_{today}.csv", 'w', newline='') as csvfile:
        fieldnames = problems[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in problems:
            writer.writerow(row)

    # Send back the data:
    return py_data