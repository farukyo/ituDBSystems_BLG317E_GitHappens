import csv
import os
from pathlib import Path

# Increase the field size limit to handle large fields
csv.field_size_limit(10**7)

def convert_tsv_to_csv(tsv_file_path, csv_file_path):
    """
    Convert a TSV file to CSV format.

    Args:
        tsv_file_path (str): Path to the input TSV file
        csv_file_path (str): Path to the output CSV file
    """
    try:
        print(f"Converting {os.path.basename(tsv_file_path)}...")

        with open(tsv_file_path, 'r', encoding='utf-8') as tsv_file:
            with open(csv_file_path, 'w', encoding='utf-8', newline='') as csv_file:
                # Read TSV with tab delimiter
                tsv_reader = csv.reader(tsv_file, delimiter='\t')
                # Write CSV with comma delimiter
                csv_writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)

                # Copy all rows from TSV to CSV
                row_count = 0
                for row in tsv_reader:
                    csv_writer.writerow(row)
                    row_count += 1

                    # Progress indicator for large files
                    if row_count % 100000 == 0:
                        print(f"  Processed {row_count:,} rows...")

                print(f"  ✓ Completed: {row_count:,} rows written to {os.path.basename(csv_file_path)}")
                return True

    except Exception as e:
        print(f"  ✗ Error converting {os.path.basename(tsv_file_path)}: {str(e)}")
        return False


def convert_all_tsv_in_folder(data_folder, output_folder=None):
    """
    Convert all TSV files in a folder to CSV format.

    Args:
        data_folder (str): Path to the folder containing TSV files
        output_folder (str): Path to the output folder (default: same as data_folder)
    """
    # Use the same folder if output folder is not specified
    if output_folder is None:
        output_folder = data_folder

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Get all TSV files in the data folder
    data_path = Path(data_folder)
    tsv_files = list(data_path.glob('*.tsv'))

    if not tsv_files:
        print(f"No TSV files found in {data_folder}")
        return

    print(f"Found {len(tsv_files)} TSV file(s) to convert\n")
    print("=" * 60)

    successful = 0
    failed = 0

    for tsv_file in tsv_files:
        # Create output CSV filename
        csv_filename = tsv_file.stem + '.csv'
        csv_file_path = os.path.join(output_folder, csv_filename)

        # Convert the file
        if convert_tsv_to_csv(str(tsv_file), csv_file_path):
            successful += 1
        else:
            failed += 1

        print("-" * 60)

    print("\n" + "=" * 60)
    print(f"Conversion Summary:")
    print(f"  ✓ Successful: {successful}")
    print(f"  ✗ Failed: {failed}")
    print(f"  Total: {len(tsv_files)}")
    print("=" * 60)


if __name__ == "__main__":
    # Get the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the data folder path (one level up from script directory)
    data_folder = os.path.join(os.path.dirname(script_dir), 'data')

    # You can optionally specify a different output folder
    # output_folder = os.path.join(os.path.dirname(script_dir), 'data_csv')
    output_folder = data_folder  # Save CSV files in the same folder

    print("TSV to CSV Converter")
    print("=" * 60)
    print(f"Input folder: {data_folder}")
    print(f"Output folder: {output_folder}")
    print("=" * 60 + "\n")

    # Convert all TSV files
    convert_all_tsv_in_folder(data_folder, output_folder)

