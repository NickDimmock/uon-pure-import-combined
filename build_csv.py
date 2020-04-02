import config
import shutil

def build(config):
    # Add headers to raw CSV file

    filenames = ["staff_headers.csv", config.staff_raw_source]

    with open(config.staff_source,"w") as outfile:
        for f in filenames:
            with open(f,'r') as infile:
                shutil.copyfileobj(infile, outfile)