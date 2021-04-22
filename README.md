# uon-pure-imports-combined

This version of the code uses the xmltodict library.

## Setup for PhD person & user records

Some of these settings may already be active as part of the existing staff sync.

### In user sync job (Pure admin panel)

Set FIRST_NAME and LAST_NAME to sync

### In person sync job (Pure admin panel)

PERSON_DATA:
    USER_ID: Sync
PERSON_ORG_RELATION:
    PRIMARY_ASSOCIATION: sync
    STUDENT_ORG_RELATION:
        EMPLOYMENT_TYPE: sync
        PROGRAMME: sync
    STUDENT_ORG_RELATION.ORG_RELATION_EMAILS: Enable sync
PERSON_IDS: Enable sync

## On Pure

Graduate School must exist with importedOrganisation ID "GRA".
As this doesn't currently exist in the staff data, in has been manually added to the structure in config.py, just after the creation of the UoN element. An org import with GRA included must be run before the initial import of PhD data to support this (this should align with the current configuration and not require any additional steps).

## Usage

1. Copy source data csv files to 'data' folder, matching filename in config.json
2. Run main.py using Python 3
3. Output files will be created in 'out' folder

## Files created

### In output folder

- org.xml - organisations import file
- persons.xml  - persons import file
- users.xml  - users import file
- phd_problems.csv - CSV export of excluded phd records for Pure team
- master_data.json - JSON export of data structure
