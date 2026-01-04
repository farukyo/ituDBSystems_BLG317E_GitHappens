import csv
import re

input_file = (
    r"C:/Users/faruk/Desktop/Code/ituDBSystems_BLG317E_GitHappens/data/principals.csv"
)
output_file = r"C:/Users/faruk/Desktop/Code/ituDBSystems_BLG317E_GitHappens/data/principals_clean.csv"

# Regex pattern to clean brackets and quotes
chars_pattern = re.compile(r'[\[\]"]')

print("Cleaning process starting... This uses RAM and CPU, writes to disk.")

with (
    open(input_file, mode="r", encoding="utf-8", newline="") as infile,
    open(output_file, mode="w", encoding="utf-8", newline="") as outfile,
):
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    # Skip or write header row (you can write it if using IGNORE 1 LINES in MySQL)
    headers = next(reader)
    writer.writerow(headers)

    row_count = 0

    for row in reader:
        # row[4] -> job, row[5] -> characters

        # Job: if '0', set to empty string (MySQL recognizes \N as null) or NULL
        if row[4] == "0":
            row[4] = "\\N"  # NULL expression in MySQL text loading

        # Characters: Cleaning process
        if row[5] == "0":
            row[5] = "\\N"
        else:
            # ["Blacksmith"] -> Blacksmith conversion
            # Remove square brackets and quotes
            row[5] = chars_pattern.sub("", row[5]).strip()

        writer.writerow(row)
        row_count += 1

        if row_count % 500000 == 0:
            print(f"{row_count} rows processed...")

print(f"Process completed! Total {row_count} rows.")
print(f"New file: {output_file}")
