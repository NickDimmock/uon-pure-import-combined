import os
import json
import config
import xmltodict
import get_data
import build_csv
import create_org_data
import create_person_data
import create_user_data

# Check for output and archive folders:
try:
    # Create target Directory
    os.mkdir(config.output_folder)
    print(f"Output folder ({config.output_folder}) created.") 
except FileExistsError:
    print(f"Output folder ({config.output_folder}) already exists.")

# Add headers to raw CSV;
build_csv.build(config)

# Get the combined data:
py_data = get_data.get(config)

# Create org data using combination of areas and depts:
org_data = create_org_data.create({**py_data["areas"], **py_data["depts"]})
with open(f"{config.output_folder}/{config.org_xml}", "w", newline="") as orgfile:
    orgfile.write(xmltodict.unparse(org_data, pretty=True))

# Create person data:
person_data = create_person_data.create(py_data)
with open(f"{config.output_folder}/{config.persons_xml}", "w", newline="", encoding="utf-8") as orgfile:
    orgfile.write(xmltodict.unparse(person_data, pretty=True))

# Create user data:
user_data = create_user_data.create(py_data)
with open(f"{config.output_folder}/{config.users_xml}", "w", newline="", encoding="utf-8") as orgfile:
    orgfile.write(xmltodict.unparse(user_data, pretty=True))

# Write the main data structure to disk, for reference
with open(f"{config.output_folder}/{config.master_json}", "w") as f:
    f.write(json.dumps(py_data, indent=4))

# Log grand totals to console:
print("\n-= Data processed! =-")
print(f"Areas: {len(py_data['areas'])}")
print(f"Depts: {len(py_data['depts'])}")
print(f"Staff: {len(py_data['persons'])}")
print(f"PhDs: {len(py_data['phd_persons'])}")
print(f"PhD staff: {len(py_data['phd_staff'])}")
