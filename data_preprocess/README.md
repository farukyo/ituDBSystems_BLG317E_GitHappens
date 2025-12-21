# Data Preprocessing Scripts

This folder contains Python scripts for preprocessing IMDb data before importing into the database.

## Scripts Overview

| Script Name | Description |
|-------------|-------------|
| `tsv_to_csv_converter.py` | Converts IMDb TSV files to CSV format with progress indicator. |
| `title_type_splitter.py` | Splits titles into movies and series based on titleType. |
| `genre_table_builder.py` | Creates genre.csv with unique genres and IDs. |
| `genre_foreign_key_mapper.py` | Maps genre names to foreign key IDs. |
| `column_dropper.py` | Removes unnecessary columns from CSV files. |
| `empty_cell_filler.py` | Fills empty cells with '0' for MySQL import. |
| `cleaner.py` | Cleans characters column in principals.csv (removes brackets/quotes). |
| `cleaner2.py` | Converts principals.csv to TSV format with cleaning. |
| `splitter.py` | Splits large principals file into 1M row chunks. |
| `sqlloader.py` | Generates SQL LOAD DATA commands for principals parts. |

## Usage Order

For proper data preprocessing, run the scripts in the following order:

1. `tsv_to_csv_converter.py` - Convert IMDb TSV files to CSV
2. `title_type_splitter.py` - Split titles into movies and series
3. `genre_table_builder.py` - Create genre dimension table
4. `genre_foreign_key_mapper.py` - Replace genre names with foreign keys
5. `column_dropper.py` - Remove unnecessary columns
6. `empty_cell_filler.py` - Fill empty cells (if needed)
7. `cleaner.py` or `cleaner2.py` - Clean principals data
8. `splitter.py` - Split principals into parts
9. `sqlloader.py` - Generate SQL for loading parts
