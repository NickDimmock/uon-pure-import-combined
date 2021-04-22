import config

def create(data):
    org_data = {
        "organisations": {
            "@xmlns": "v1.organisation-sync.pure.atira.dk",
            "@xmlns:v3": "v3.commons.pure.atira.dk",
            "organisation": [],
        }
    }
    orgs = []
    for id, obj in data.items():
        org = {
                "organisationId": id,
                "type": obj["type"],
                "name": {"v3:text": obj["name"]},
                "startDate": obj["start_date"],
                "endDate": "2050-01-01",
                "visibility": "Public"
            }
        if "parent" in obj:
            org["parentOrganisationId"] = obj["parent"]
        orgs.append(org)

    org_data["organisations"]["organisation"] = orgs

    return org_data
