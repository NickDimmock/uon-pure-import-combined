import config

# Persons
def create(person_data):
    persons = []
    for id, obj in person_data["persons"].items():
        new_person = {
            "@id": id,
            "name": {
                "v3:firstname": obj["first_name"],
                "v3:lastname": obj["surname"]
            },
            "names": {
                "classifiedName": {
                    "@id": f"knownas-{id}",
                    "name": {
                        "v3:firstname": obj["known_as_first"],
                        "v3:lastname": obj["known_as_last"]
                    },
                    "typeClassification": "knownas"
                }
            },
            "titles": {
                "title": {
                    "@id": f"title-{id}",
                    "typeClassification": "designation",
                    "value": {
                        "v3:text": {
                            "@lang": "en",
                            "@country": "GB",
                            "#text": obj["title"]
                        }
                    }
                }
            },
            "gender": "unknown",
            "employeeStartDate": obj["uni_start_date"],
            "systemLeavingDate": obj["uni_end_date"],
            "organisationAssociations": {
                "staffOrganisationAssociation": {
                    "@id": f"{id}-{obj['dept_code']}-{obj['div_start_date']}",
                    "emails": {
                        "v3:classifiedEmail": {
                            "@id": f"{id}-{obj['dept_code']}-{obj['email']}",
                            "v3:classification": "email",
                            "v3:value": obj['email']
                        }
                    },
                    "primaryAssociation": "true",
                    "organisation": {
                        "v3:source_id": obj["dept_code"]
                    },
                    "period": {
                        "v3:startDate": obj["div_start_date"],
                        "v3:endDate": obj["div_end_date"]
                    },
                    "staffType": "academic",
                    "jobDescription": {
                        "v3:text": obj["role"]
                    },
                    "fte": obj["fte"]
                }
            },
            "user": {
                "@id": f"user-{id}"
            },
            "personIds": {
                "v3:id": {
                    "@id": id,
                    "@type": "employee",
                    "#text": f"employee-{id}"
                }
            }
        }
        # Now add phd_staff data where required:
        if id in person_data["phd_staff"].keys():
            # A match here means the current person is also in the PHD data set.
            # So we can just add this as an org association on their staff record,
            # rather than creating a separate PHD person record.
            phd_org = config.phd_org
            phd_start = person_data["phd_staff"][id]["startdate"]
            phd_prog = person_data["phd_staff"][id]["description"]
            new_person["organisationAssociations"]["studentOrganisationAssociation"] = {
                "@id": f"{id}-{phd_org}-{phd_start}",
                "employmentType": "phd",
                "organisation": {
                    "v3:source_id": phd_org
                },
                "period": {
                    "v3:startDate": phd_start
                },
                "programme": phd_prog
            }
        # Add the new person to the list of persons:
        persons.append(new_person)

    # Add non-staff PhDs:
    for id, obj in person_data["phd_persons"].items():
        new_phd = {
            "@id": id,
            "name": {
                "v3:firstname": obj["first_name"],
                "v3:lastname": obj["surname"]
            },
            "titles": {
                "title": {
                    "@id": f"title-{id}",
                    "typeClassification": "designation",
                    "value": {
                        "v3:text": {
                            "@lang": "en",
                            "@country": "GB",
                            "#text": obj["title"]
                        }
                    }
                }
            },
            "gender": "unknown",
            "organisationAssociations": {
                "studentOrganisationAssociation": {
                    "@id": f"{id}-{obj['code']}-{obj['startdate']}",
                    "emails": {
                        "v3:classifiedEmail": {
                            "@id": f"{id}-{obj['code']}-{obj['email']}",
                            "v3:classification": "email",
                            "v3:value": obj["email"]
                        }
                    },
                    "employmentType": "phd",
                    "primaryAssociation": "true",
                    "organisation": {
                        "v3:source_id": phd_org
                    },
                    "period": {
                        "v3:startDate": obj['startdate']
                    },
                    "programme": obj['description']
                }
            }
        }
        persons.append(new_phd)

    return {
        "persons": {
            "@xmlns": "v1.unified-person-sync.pure.atira.dk",
            "@xmlns:v3": "v3.commons.pure.atira.dk",
            "person": persons
        }
    }

