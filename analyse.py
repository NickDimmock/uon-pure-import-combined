import json

# Analyse master_data.json for stats

sits_staff_keys=[]
pre_sits_staff_keys=[]
sits_phd_keys=[]
pre_sits_phd_keys=[]

with open("out/master_data.json") as json_file:
    json_data = json.load(json_file)
    print(
        f"SITS PhD Staff: {len(json_data['phd_staff'])}"
    )
    for item in json_data['phd_staff'].keys():
        sits_staff_keys.append(item)
    for item in json_data['phd_persons'].keys():
        sits_phd_keys.append(item)

    
with open("out/backups/pre-sits/master_data.json") as json_file:
    json_data = json.load(json_file)
    print(
        f"Pre-SITS PhD Staff: {len(json_data['phd_staff'])}"
    )
    for item in json_data['phd_staff'].keys():
        pre_sits_staff_keys.append(item)
    for item in json_data['phd_persons'].keys():
        pre_sits_phd_keys.append(item)

# with open(f"out/sits_keys.json", "w") as f:
#     f.write(json.dumps(sits_keys, indent=4))
# with open(f"out/pre_sits_keys.json", "w") as f:
#     f.write(json.dumps(pre_sits_keys, indent=4))

sits_staff_ids_new = []
sits_staff_ids_lost = []
sits_phd_ids_new = []
sits_phd_ids_lost = []

for id in sits_staff_keys:
    if id not in pre_sits_staff_keys:
        sits_staff_ids_new.append(id)
with open(f"out/sits_staff_ids_new.json", "w") as f:
    f.write(json.dumps(sits_staff_ids_new, indent=4))

for id in pre_sits_staff_keys:
    if id not in sits_staff_keys:
        sits_staff_ids_lost.append(id)
with open(f"out/sits_staff_ids_lost.json", "w") as f:
    f.write(json.dumps(sits_staff_ids_lost, indent=4))

for id in sits_phd_keys:
    if id not in pre_sits_phd_keys:
        sits_phd_ids_new.append(id)
with open(f"out/sits_phd_ids_new.json", "w") as f:
    f.write(json.dumps(sits_phd_ids_new, indent=4))

for id in pre_sits_phd_keys:
    if id not in sits_phd_keys:
        sits_phd_ids_lost.append(id)
with open(f"out/sits_phd_ids_lost.json", "w") as f:
    f.write(json.dumps(sits_phd_ids_lost, indent=4))