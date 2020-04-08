# source files for staff and phd data:
staff_raw_source = "data/data-raw.csv"
staff_source = "data/data.csv"
phd_source = "data/phd-data.csv"

# master output folder:
output_folder = "out"

# output filenames:
persons_xml = "persons.xml"
users_xml = "users.xml"
org_xml = "org.xml"

# Filename for PhD problems CSV:
phd_problem_file = "phd_problems.csv"

# Notes from data import:
data_notes_file = "data_notes.txt"

# Reference master data file:
master_json = "master_data.json"

#org_namespaces = {
    #"xmlns": "v1.organisation-sync.pure.atira.dk",
    #"xmlns:v3": "v3.commons.pure.atira.dk" 
#}

#persons_namespaces = {
    #"xmlns": "v1.unified-person-sync.pure.atira.dk",
    #"xmlns:v3": "v3.commons.pure.atira.dk"
#}

#users_namespaces = {
    #"xmlns": "v1.user-sync.pure.atira.dk",
    #"xmlns:v3": "v3.commons.pure.atira.dk"
#}

# Default dates
start_date = "2005-09-01"
end_date = "2099-12-31"

uon_id = "UON"

# Add PhDs to Grad School rather than use individual course codes
phd_org = "GRA"

uon_data = {
    "UON": {
        "name": "University of Northampton",
        "type": "university",
        "start_date": "1927-01-01"
    },
    "GRA": {
        "name": "Graduate School",
        "parent": "UON",
        "type": "department",
        "start_date": "2005-09-01"
    }
}

# Blacklist of unwanted depts to avoid duplicates

dept_blacklist = {
    "LLS",
    "LTE",
    "FHS",
    "FEH"
}