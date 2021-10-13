# Basic check on data files
# Will output 1 if no errors are found
# If errors are found, will output 0 followed by report

import os.path, time

hesa_file = "data/puredatahesa.csv"

phd_file = "data/phd-data.csv"

staff_file = "data/phd-staff.tsv"

errors = []

# Basic existential crisis check - are the files there?

if not os.path.isfile(hesa_file):
    errors.append("puredatahesa.csv: File not found.")

if not os.path.isfile(phd_file):
    errors.append("phd-data.csv: File not found.")

if not os.path.isfile(staff_file):
    errors.append("phd-staff.tsv: File not found.")

# Only run the rest of the tests if all files are present:

if(len(errors) == 0):

    # puredatahesa.csv and phd-staff.tsv should not be more than two days old:

    now = time.time()
    hesa_file_age = now - os.path.getmtime(hesa_file)
    staff_file_age = now - os.path.getmtime(staff_file)
    if(hesa_file_age > 172800):
        errors.append(f"{hesa_file} may not have been updated.")
    if(staff_file_age > 172800):
        errors.append(f"{staff_file} may not have been updated.")

    # Length of file - ensures file is longer than the required length:

    req_len = 100

    with open(hesa_file) as f:
        for i, l in enumerate(f):
            pass
        if (i < req_len):
            errors.append(f"puredatahesa.csv: File is under {req_len} lines.")

    with open(phd_file) as f:
        for i, l in enumerate(f):
            pass
        if (i < req_len):
            errors.append(f"phd-data.csv: File is under {req_len} lines.")

    with open(staff_file) as f:
        for i, l in enumerate(f):
            pass
        if (i < req_len):
            errors.append(f"phd-staff.tsv: File is under {req_len} lines.")

    # CSV data should be quoted. Checks will bail out as soon as one non-quoted line is found.
    # (We just check the first character here.)

    with open(hesa_file) as f:
        for i, l in enumerate(f):
            if(l[0] != '"'):
                errors.append(f"puredatahesa.csv: Data may not be quoted (line {i+1} is first occurence).")
                break

    with open(phd_file) as f:
        for i, l in enumerate(f):
            if(l[0] != '"'):
                errors.append(f"phd-data.csv: Data may not be quoted (line {i+1} is first occurence).")
                break

    # Check headers are as expected:

    # puredatahesa is not expected to have a header row:
    with open(hesa_file) as f:
        first_line = f.readline()
        if first_line[0:9] == "DIM_VALUE" or first_line[0:11] == '"DIM_VALUE"':
            errors.append("puredatahesa.csv: Headers have been included, but are not expected in this file.")

    #phd-data should have a header row:
    with open(phd_file) as f:
        first_line = f.readline()
        if first_line[0:11] != '"RES_VALUE"':
            errors.append("phd-data.csv: Headers not found, but are expected (first line should begin with \"RES_VALUE\").")

    #phd-staff should also have a header row:
    with open(staff_file) as f:
        first_line = f.readline()
        if first_line[0:8] != "Staff ID":
            errors.append("phd-staff.tsv: Headers not found, but are expected (first line should begin with Staff ID).")

# Output results:

if(len(errors) > 0):
    print("0")
    for error in errors:
        print(error)
else:
    print("1")
