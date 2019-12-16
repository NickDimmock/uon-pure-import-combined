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
        orgs.append(
            {
                "organisationId": id,
                "type": obj["type"],
                "name": {"v3:text": obj["name"]},
                "startDate": obj["start_date"],
            }
        )

    org_data["organisations"]["organisation"] = orgs

    return org_data
