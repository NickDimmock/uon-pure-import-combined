import config

# Users
def create(data):
    users = []
    for id, obj in data["persons"].items():
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
