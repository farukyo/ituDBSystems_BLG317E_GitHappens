# Data Preprocessing Scripts

This folder contains Python scripts for preprocessing IMDb data before importing into the database.

## Scripts Overview

| Script Name | Description |
|-------------|-------------|
| `tsv_to_csv_converter.py` | Converts TSV (Tab-Separated Values) files from IMDb to CSV format. Includes progress indicator for large files and supports batch conversion. |
| `title_type_splitter.py` | Splits `title.basics.csv` into movies and series based on `titleType`. Movies include: movie, short, tvMovie, video. Series include: tvSeries, tvMiniSeries, tvEpisode, tvPilot, tvShort, tvSpecial. |
| `genre_table_builder.py` | Extracts unique genres from `title.basics.csv` and creates a separate `genre.csv` with auto-incremented `genre_id`. Used for database normalization. |
| `genre_foreign_key_mapper.py` | Converts text-based genre values in movies/series CSV files to `genre_id` foreign keys using `genre.csv`. Maps genre strings to IDs for database relationships. |
| `column_dropper.py` | Removes unnecessary columns from movies and series CSV files. Drops `originalTitle` from both, and `endYear` from movies (meaningless for films). |
| `empty_cell_filler.py` | Fills empty cells in CSV files with '0' value. Used when default values are required instead of NULL for MySQL import. Designed for missing data in the names table. |

## Usage Order

For proper data preprocessing, run the scripts in the following order:

1. `tsv_to_csv_converter.py` - Convert IMDb TSV files to CSV
2. `title_type_splitter.py` - Split titles into movies and series
3. `genre_table_builder.py` - Create genre dimension table
4. `genre_foreign_key_mapper.py` - Replace genre names with foreign keys
5. `column_dropper.py` - Remove unnecessary columns
6. `empty_cell_filler.py` - Fill empty cells (if needed)
