import xml.etree.ElementTree as ET
import xml.dom.minidom
import json
import datetime

def create(config, data):

    # org_list creates a simple list of created orgs:
    org_list = {}

    orgs = ET.Element("organisations")

    for ns, uri in config.org_namespaces.items():
        orgs.set(ns, uri)

    # Iterate through our organisational data set:
    for id, obj in data.items():

        org_list[id] = obj["name"]

        org = ET.SubElement(orgs, "organisation")

        org_id = ET.SubElement(org, "organisationId")
        org_id.text = id
        
        org_type = ET.SubElement(org, "type")
        org_type.text = obj["type"]
        
        name = ET.SubElement(org, "name")
        name_text = ET.SubElement(name, "v3:text")
        name_text.text = obj["name"]

        start_date = ET.SubElement(org, "startDate")
        start_date.text = obj["start_date"]
        
        visibility = ET.SubElement(org, "visibility")
        visibility.text = "Public"
        
        # UON won't have a parent, so we need to check before creating:
        if "parent" in obj:
            parent = ET.SubElement(org, "parentOrganisationId")
            parent.text = obj["parent"]
            
    # Create XML string, then use minidom to generate a readable version
    xml_string = ET.tostring(orgs, encoding="unicode")
    new_xml = xml.dom.minidom.parseString(xml_string)
    
    # Grab the date:
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    
    # Write the main XML output:
    with open(f"{config.output_folder}/{config.org_xml}.xml", "w", encoding="utf-8") as f:
        f.write(new_xml.toprettyxml())
    
    # Write the dated XML output:
    with open(f"{config.archive_folder}/{config.org_xml}_{today}.xml", "w", encoding="utf-8") as f:
        f.write(new_xml.toprettyxml())

    # Write archived org_list to json:
    with open(f"{config.archive_folder}/{config.org_list_json}_{today}.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(org_list, sort_keys=True, indent=4))