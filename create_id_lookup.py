# Create a lookup table for login names and employee IDs

import config
import csv
import re

def create():
    login_to_id = {}
    log = []

    with open(config.phd_staff_source, encoding="utf-8-sig") as tsvfile, open(f"{config.output_folder}/{config.id_lookup_log}", "w") as logfile:
        reader = csv.DictReader(tsvfile, dialect='excel-tab')
        for row in reader:
            # Some rows are just NULL, need to ignore those - checking Staff ID will do the job:
            if row['Staff ID'] == "NULL":
                continue
            # Not all entries have a login ID, so check both fields have something:
            if len(row["Staff ID"]) and len(row["Login ID"]):
                # All IDs in the phd_staff file are padded to 5 digits, but we only
                # want the original resid - so remove leading zeroes:
                resid = re.sub("^0*","",row["Staff ID"])
                login_to_id[row["Login ID"].lower()] = resid
            else:
                log.append(f"Skipping {row['Staff ID']} ({row['Forename']} {row['Surname']}) - no login ID value.\n")

        logfile.write(f"Created {len(login_to_id)} login to ID lookups.\n")
        logfile.write(f"Skipped {len(log)} entries.\n")
        for line in log:
            logfile.write(line)
        return login_to_id

if __name__ == "__main__":
    data = create()
    print(f"Created {len(data)} lookups.")
    