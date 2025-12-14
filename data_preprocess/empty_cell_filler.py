# ==============================================================================
# empty_cell_filler.py - Empty Cell Filler Script
# ==============================================================================
# This script fills empty cells in CSV files with '0' value.
# Used when default values are required instead of NULL values for MySQL import.
# Specifically designed for missing data in the names table.
# ==============================================================================

import csv


input_file = '../data/names_clean.csv'
output_file = '../data/names.csv'

print("Processing started...")

with open(input_file, mode='r', encoding='utf-8', newline='') as f_in, \
        open(output_file, mode='w', encoding='utf-8', newline='') as f_out:
    reader = csv.reader(f_in)
    writer = csv.writer(f_out)

    for row in reader:
        # Using list comprehension to check each cell in the row
        # If cell is empty (''), replace with '0', otherwise keep as is
        new_row = ['0' if cell == '' else cell for cell in row]

        writer.writerow(new_row)

print(f"Completed! '{output_file}' is ready for MySQL import.")