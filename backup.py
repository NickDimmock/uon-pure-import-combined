# Copy current output files to 'prev' backups to enable comparison

from shutil import copyfile
files = {
    "org.xml": "org-prev.xml",
    "users.xml": "users-prev.xml",
    "persons.xml": "persons-prev.xml",
    "master_data.json": "master_data-prev.json",
}
for src,dest in files.items():
    copyfile(f"./out/{src}", f"./out/{dest}")