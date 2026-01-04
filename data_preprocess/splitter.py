import csv
import os

# --- SETTINGS ---
# Path to cleaned file (e.g., principals_clean.csv)
input_file = r"C:/Users/faruk/Desktop/Code/ituDBSystems_BLG317E_GitHappens/data/principals_clean.tsv"

# Folder where parts will be saved
output_folder = r"C:/Users/faruk/Desktop/Code/ituDBSystems_BLG317E_GitHappens/data/principals_parts/"

# How many rows per file? (1 Million is ideal)
CHUNK_SIZE = 1000000

# Create folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

print(f"Splitting process starting: {input_file}")


def write_chunk(part_num, header, rows):
    filename = os.path.join(output_folder, f"principals_part_{part_num}.tsv")
    with open(filename, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)  # Add header to each file
        writer.writerows(rows)
    print(f"--> {filename} created ({len(rows)} rows).")


with open(input_file, mode="r", encoding="utf-8", newline="") as infile:
    reader = csv.reader(infile)

    try:
        header = next(reader)  # Get first row (header)
    except StopIteration:
        print("File is empty!")
        exit()

    current_chunk = []
    part_counter = 1

    for row in reader:
        current_chunk.append(row)

        # When list is full, write to file and clear memory
        if len(current_chunk) == CHUNK_SIZE:
            write_chunk(part_counter, header, current_chunk)
            current_chunk = []
            part_counter += 1

    # After loop ends, write remaining rows
    if current_chunk:
        write_chunk(part_counter, header, current_chunk)

print("\nDone! Files are ready in the folder.")
