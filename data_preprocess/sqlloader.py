import os
import re

# --- SETTINGS ---
# Folder containing split files
input_folder = r'C:/Users/faruk/Desktop/Code/ituDBSystems_BLG317E_GitHappens/data/principals_parts'

# Output SQL file location
output_sql_file = r'C:/Users/faruk/Desktop/Code/ituDBSystems_BLG317E_GitHappens/data/load_all_parts.sql'

# Check if folder exists
if not os.path.exists(input_folder):
    print(f"ERROR: '{input_folder}' folder not found!")
    exit(1)

# List files
files = [f for f in os.listdir(input_folder) if f.endswith('.tsv') and f.startswith('principals_part_')]

if len(files) == 0:
    print(f"ERROR: No principals_part_*.tsv files found in '{input_folder}'!")
    exit(1)

# Sort files by number (Important: part_1, part_2... part_10 in order)
# Otherwise it sorts as part_1, part_10, part_11... part_2
files.sort(key=lambda f: int(re.search(r'\d+', f).group()))

print(f"Found {len(files)} files. Generating SQL...")

# Ensure output folder exists
os.makedirs(os.path.dirname(output_sql_file), exist_ok=True)

with open(output_sql_file, 'w', encoding='utf-8') as f:
    # 1. Initial Settings (Speed optimization)
    f.write("-- Speed and Security Settings\n")
    f.write("TRUNCATE TABLE principals;\n")
    f.write("ALTER TABLE principals DISABLE KEYS;\n")
    f.write("SET autocommit = 0;\n")
    f.write("SET unique_checks = 0;\n")
    f.write("SET foreign_key_checks = 0;\n")
    f.write("SET sql_log_bin = 0;\n\n")

    # 2. Loop to write LOAD DATA commands
    for filename in files:
        # Fix backslashes for Windows path
        full_path = os.path.join(input_folder, filename).replace('\\', '/')

        sql_command = f"""LOAD DATA LOCAL INFILE '{full_path}' 
INTO TABLE principals 
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"' 
LINES TERMINATED BY '\\n' 
IGNORE 1 LINES;

"""
        f.write(f"-- Loading {filename}\n")
        f.write(sql_command)

    # 3. Final Settings (Restore and Commit)
    f.write("\n-- Complete the process\n")
    f.write("COMMIT;\n")
    f.write("ALTER TABLE principals ENABLE KEYS;\n")
    f.write("SET unique_checks = 1;\n")
    f.write("SET foreign_key_checks = 1;\n")
    f.write("SET sql_log_bin = 1;\n")
    f.write("SET autocommit = 1;\n")

print(f"Done! '{output_sql_file}' file created.")
print("Open this file in MySQL Workbench via File -> Open SQL Script and run it.")