import csv
import json
import re
import datetime
from time import strptime

def get(config):

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
        data = list(reader)

    # Create starting data, including root UON info from config:
    py_data = {
        "phd_persons": {}
    }

    # A list of our various complaints:
    problems = []

    # Take the data line by line:
    for d in data:

        # Filter out staff based on alphanumeric ResId values (e.g. jsmith):
        # Strip the ResId, as it sometimes has a leading space...
        staff_pattern=re.compile(r"\D")

        if staff_pattern.search(d["ResId"].strip()):
            problems.append({
                "ResId": d['ResId'],
                "studentid": d["student_id"],
                "forenames": d["forenames"],
                "surname": d["surname"],
                "email": d["email"],
                "problem": "ResId doesn't match ARMS pattern - may be staff."
            })
            # Skip to next record:
            continue
        
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