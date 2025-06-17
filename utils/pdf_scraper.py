# pdf_scraper.py

import pdfplumber
import json

# PDF scraper for tables in the Tasmanian Plant Quarantine Manual

pages = list(range(83, 87))  # adjust page numbers as needed, only extracts the table data

all_tables = []
with pdfplumber.open('../docs/tas_pqm.pdf') as pdf:
    for p in pages:
        tbl = pdf.pages[p].extract_table()
        if tbl:
            # Include page number for reference
            all_tables.append({"page": p+1, "rows": tbl})

# Save raw output 
# Ensure the file name matches the table name in the data folder
with open('../mnt/data/new-table.json', 'w') as f: 
    json.dump(all_tables, f, indent=2)

print("Raw table extracts saved to mnt/data/")
