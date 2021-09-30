# Copy current output files to 'prev' backups to enable comparison

from shutil import copyfile
from pathlib import Path
files = {
    "org.xml": "org-prev.xml",
    "users.xml": "users-prev.xml",
    "persons.xml": "persons-prev.xml",
    "master_data.json": "master_data-prev.json",
}
for src,dest in files.items():
    file = Path(f"./out/{src}")
    if file.is_file():
        copyfile(f"./out/{src}", f"./out/{dest}")
        print(f"out/{src} copied to out/{dest}")
    else:
        print(f"[!] Can't create backup of out/{src} - file not found.")