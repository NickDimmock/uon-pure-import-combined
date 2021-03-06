import config

# Persons
def create(person_data):
    persons = []
    for id, obj in person_data["persons"].items():
        new_person = {
            "@id": id,
            "name": {
                "v3:firstname": obj["first_name"],
                "v3.lastname": obj["surname"]
            },
            "names": {
                "classifiedName": {
                    "@id": f"knownas-{id}",
                    "name": {
                        "v3:firstname": obj["known_as_first"],
                        "v3.lastname": obj["known_as_last"]
                    },
                    "typeClassification": "knownas"
                }
            },
            "titles": {
                "title": {
                    "@id": f"title={id}",
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
            "organisationAssociations": {
                "staffOrganisationAssociation": {
                    "@id": f"{id}-{obj['dept_code']}-{obj['div_start_date']}",
                    "emails": {
                        "v3:classifiedEmail": {
                            "@id": f"{id}-{obj['dept_code']}-{obj['email']}",
                            "v3:classificaiton": "email"
                        }
                    },
                    "primaryAssociation": "true",
                    "organisation": {
                        "v3:source_id": obj["dept_code"]
                    },
                    "period": {
                        "v3:startDate": obj["div_start_date"]
                    },
                    "staffType": "academic",
                    "jobDescription": {
                        "v3:text": obj["role"]
                    },
                    "fte": obj["fte"]
                }
            },
            "user": {
                "@id": f"user={id}"
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
            # Bingo!
            phd_code = person_data["phd_staff"][id]["code"]
            phd_start = person_data["phd_staff"][id]["startdate"]
            phd_prog = person_data["phd_staff"][id]["description"]
            new_person["organisationAssociations"]["studentOrganisationAssociation"] = {
                "@id": f"{id}-{phd_code}-{phd_start}",
                "employmentType": "phd",
                "organisation": {
                    "v3:source_id": phd_code
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
                "v3.lastname": obj["surname"]
            },
            "titles": {
                "title": {
                    "@id": f"title={id}",
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
                            "v3:classificaiton": "email",
                            "v3:value": obj["email"]
                        }
                    },
                    "employmentType": "phd",
                    "primaryAssociation": "true",
                    "organisation": {
                        "v3:source_id": obj['code']
                    },
                    "period": {
                        "v3:startDate": obj['startdate']
                    },
                    "programme": obj['description']
                }
            },
            "employmentType": "phd",
            "organisation": {
                "v3:source_id": obj['code']
            },
            "period": {
                "v3:startDate": obj['startdate']
            },
            "programme": obj['description']
        }
        persons.append(new_phd)

    return {
        "persons": {
            "@xmlns": "v1.unified-person-sync.pure.atira.dk",
            "@xmlns:v3": "v3.commons.pure.atira.dk",
            "person": persons
        }
    }

