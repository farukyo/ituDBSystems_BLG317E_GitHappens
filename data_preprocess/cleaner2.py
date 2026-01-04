import csv
import re

input_file = (
    r"C:/Users/faruk/Desktop/Code/ituDBSystems_BLG317E_GitHappens/data/principals.csv"
)
output_file = r"C:/Users/faruk/Desktop/Code/ituDBSystems_BLG317E_GitHappens/data/principals_clean.tsv"  # Extension .tsv

chars_pattern = re.compile(r'[\[\]"]')

print("Conversion starting (CSV -> TSV)...")

with (
    open(input_file, mode="r", encoding="utf-8", newline="") as infile,
    open(output_file, mode="w", encoding="utf-8", newline="") as outfile,
):
    # Reader still reads with comma
    reader = csv.reader(infile)
    # Writer now writes with TAB (\t). This solves "parsing hell" problem 100%.
    writer = csv.writer(outfile, delimiter="\t")

    headers = next(reader)
    writer.writerow(headers)

    row_count = 0
    for row in reader:
        # Job cleaning
        if row[4] == "0":
            row[4] = "\\N"

        # Character cleaning
        if row[5] == "0":
            row[5] = "\\N"
        else:
            row[5] = chars_pattern.sub("", row[5]).strip()

        writer.writerow(row)
        row_count += 1
        if row_count % 1000000 == 0:
            print(f"{row_count}...")

print("Done!")
