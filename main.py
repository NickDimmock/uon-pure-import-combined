import create_orgs
import create_persons
import create_users
import get_data
import os
import config

# Check for output and archive folders:
try:
    # Create target Directory
    os.mkdir(config.output_folder)
    print("Output folder created ") 
except FileExistsError:
    print("Output folder already exists")
try:
    # Create target Directory
    os.mkdir(config.archive_folder)
    print("Archive folder created ") 
except FileExistsError:
    print("Archive folder already exists")

# Parse the staff CSV data:
data = get_data.get(config=config)

# Combine uni, faculty and dept data to send to org creation function:
org_data = {**data["areas"], **data["depts"]}

# Create org data:
create_orgs.create(config=config, data=org_data)

# Create person data:
create_persons.create(config=config, data=data)

# Create user data:
create_users.create(config=config, data=data)
