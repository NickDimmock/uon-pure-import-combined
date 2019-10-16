# source files for staff and phd data:
staff_source = "data/data.csv"
phd_source = "data/phd-data.csv"

# master output folder:
output_folder = "out"

# archive folder:
archive_folder = "out/archived"

# output filenames:
persons_xml = "persons"
users_xml = "users"
org_xml = "org"

# Filename for PhD problems CSV:
phd_problem_file = "phd_problems"

# Only needed to support NECTAR imports:
# email_lookup_json = "out/email_lookup.json"

# Reference org list file:
org_list_json = "org_list"

# Reference master data file:
master_json = "master_data"

org_namespaces = {
    "xmlns": "v1.organisation-sync.pure.atira.dk",
    "xmlns:v3": "v3.commons.pure.atira.dk" 
}

persons_namespaces = {
    "xmlns": "v1.unified-person-sync.pure.atira.dk",
    "xmlns:v3": "v3.commons.pure.atira.dk"
}

users_namespaces = {
    "xmlns": "v1.user-sync.pure.atira.dk",
    "xmlns:v3": "v3.commons.pure.atira.dk"
}

start_date = "2005-09-01"

uon_id = "UON"

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