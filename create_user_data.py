import config

# Users
# Now using user_id (from MAIN_RESID value) to create account, to ensure
# academic staff who've been assigned new RESID values can still use SSO.
def create(data):
    users = []
    for id, obj in data["persons"].items():
        user_id = obj["user_id"]
        user = {
            "@id": f"user-{user_id}",
            "userName": user_id.rjust(8,"0"),
            "email": obj["email"],
            "name": {
                "v3:firstname": obj["first_name"],
                "v3:lastname": obj["surname"]
            }
        }
        users.append(user)
    
    for id, obj in data["phd_persons"].items():
        user = {
            "@id": f"user-{id}",
            "userName": id.rjust(8,"0"),
            "email": obj["email"],
            "name": {
                "v3:firstname": obj["first_name"],
                "v3:lastname": obj["surname"]
            }
        }
        users.append(user)

    return {
        "users": {
            "@xmlns": "v1.user-sync.pure.atira.dk",
            "@xmlns:v3": "v3.commons.pure.atira.dk",
            "user": users
        }
    }
