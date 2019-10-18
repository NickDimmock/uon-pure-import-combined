import xml.etree.ElementTree as ET
import xml.dom.minidom
import datetime

def create(config, data):
    
    users = ET.Element("users")

    for ns, uri in config.users_namespaces.items():
        users.set(ns, uri)

    # Process staff records:
    for id, obj in data['persons'].items():

        user = ET.SubElement(users, "user")
        user.set("id", f"user-{id}")

        # We need a padded 8-digit version of our ID for the username value
        padded_id = id.rjust(8, "0")

        username = ET.SubElement(user, "userName")
        username.text = padded_id

        email = ET.SubElement(user, "email")
        email.text = obj["email"]

        name = ET.SubElement(user, "name")
        name_first = ET.SubElement(name, "v3:firstname")
        name_first.text = obj["first_name"]
        name_last = ET.SubElement(name, "v3:lastname")
        name_last.text = obj["surname"]
    
    # Almost the same process for PhD persons
    for id, obj in data['phd_persons'].items():
        user = ET.SubElement(users, "user")
        user.set("id", f"user-{id}")
        padded_id = id.rjust(8, "0")
        username = ET.SubElement(user, "userName")
        username.text = padded_id
        email = ET.SubElement(user, "email")
        email.text = obj["email"]
        name = ET.SubElement(user, "name")
        name_first = ET.SubElement(name, "v3:firstname")
        name_first.text = obj["first_name"]
        name_last = ET.SubElement(name, "v3:lastname")
        name_last.text = obj["surname"]
    
    # Create XML string, then use minidom to generate a readable version
    xml_string = ET.tostring(users, encoding="unicode")
    new_xml = xml.dom.minidom.parseString(xml_string)
    
    # Grab the date:
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    
    # Main users file:
    with open(f"{config.output_folder}/{config.users_xml}.xml", "w", encoding="utf-8") as f:
        f.write(new_xml.toprettyxml())
    
    # Dated users file:
    with open(f"{config.archive_folder}/{config.users_xml}_{today}.xml", "w", encoding="utf-8") as f:
        f.write(new_xml.toprettyxml())
    