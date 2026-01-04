# ==============================================================================
# genre_foreign_key_mapper.py - Genre Foreign Key Converter
# ==============================================================================
# This script converts text-based genre values in movies and series CSV files
# to genre_id (foreign key) values from genre.csv.
# Maps genre strings to IDs for database relationships.
# ==============================================================================

import os
import pandas as pd


def _load_paths(
    movies_path: str | None,
    series_path: str | None,
    genre_path: str | None,
):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if movies_path is None:
        movies_path = os.path.join(base_dir, "..", "data", "movies.basics.csv")
    if series_path is None:
        series_path = os.path.join(base_dir, "..", "data", "series.basics.csv")
    if genre_path is None:
        genre_path = os.path.join(base_dir, "..", "data", "genre.csv")
    return movies_path, series_path, genre_path


def apply_genre_fk(
    movies_path: str | None = None,
    series_path: str | None = None,
    genre_path: str | None = None,
    movies_output_path: str | None = None,
    series_output_path: str | None = None,
):
    """Replace the textual genres in movies/series basics files with genre_id FK.

    This expects:
    - movies_path: CSV similar to title.basics.csv (contains 'tconst' and 'genres')
    - series_path: same structure for series
    - genre_path: CSV with columns [genre_id, genre]

    It will:
    - explode comma-separated genres per title
    - map each genre string to genre_id via genre.csv
    - aggregate back to a comma-separated list of genre_id values per title
    - overwrite the `genres` column in the basics CSVs with these id lists.
    """

    movies_path, series_path, genre_path = _load_paths(
        movies_path, series_path, genre_path
    )

    base_dir = os.path.dirname(os.path.abspath(__file__))
    if movies_output_path is None:
        movies_output_path = movies_path  # overwrite by default
    if series_output_path is None:
        series_output_path = series_path  # overwrite by default

    # Load basics
    movies_df = pd.read_csv(movies_path)
    series_df = pd.read_csv(series_path)

    # Load genre dimension
    genre_df = pd.read_csv(genre_path, usecols=["genre_id", "genre"])
    genre_df["genre"] = genre_df["genre"].astype("string").str.strip()
    genre_map = dict(zip(genre_df["genre"], genre_df["genre_id"]))

    def replace_genres_with_ids(df: pd.DataFrame) -> pd.DataFrame:
        # Work on a copy to avoid mutating original in place unexpectedly
        df = df.copy()

        base = df[["tconst", "genres"]].copy()
        base["genres"] = base["genres"].astype("string")
        base = base.dropna(subset=["genres"])

        exploded = base.assign(genre_str=base["genres"].str.split(",")).explode(
            "genre_str"
        )
        exploded["genre_str"] = exploded["genre_str"].astype("string").str.strip()

        mask_valid = (exploded["genre_str"] != "") & (exploded["genre_str"] != "\\N")
        exploded = exploded[mask_valid]

        exploded["genre_id"] = exploded["genre_str"].map(genre_map)
        exploded = exploded.dropna(subset=["genre_id"])

        # Group back by tconst, collect genre_ids as comma-separated string
        grouped = (
            exploded.groupby("tconst")["genre_id"]
            .apply(lambda ids: ",".join(str(int(i)) for i in sorted(set(ids))))
            .reset_index()
        )

        # Merge back into original df: titles without genres stay as they are (NaN or \N)
        df = df.drop(columns=["genres"])
        df = df.merge(grouped, on="tconst", how="left")

        # If some titles had no mapped genres, keep original markers (optional: set to NaN)
        df["genre_id"] = df["genre_id"].astype("string")

        # For compatibility with your requirement, rename back to 'genres'
        df = df.rename(columns={"genre_id": "genres"})

        return df

    movies_df_converted = replace_genres_with_ids(movies_df)
    series_df_converted = replace_genres_with_ids(series_df)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(movies_output_path), exist_ok=True)
    os.makedirs(os.path.dirname(series_output_path), exist_ok=True)

    movies_df_converted.to_csv(movies_output_path, index=False)
    series_df_converted.to_csv(series_output_path, index=False)

    return {
        "movies_rows": len(movies_df_converted),
        "series_rows": len(series_df_converted),
    }


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    movies_path = os.path.join(base_dir, "..", "data", "movies.basics.csv")
    series_path = os.path.join(base_dir, "..", "data", "series.basics.csv")
    genre_path = os.path.join(base_dir, "..", "data", "genre.csv")

    result = apply_genre_fk(movies_path, series_path, genre_path)

    print("Genre FK applied in basics files:")
    print(f"  Movies rows : {result['movies_rows']:,} -> {movies_path}")
    print(f"  Series rows : {result['series_rows']:,} -> {series_path}")
