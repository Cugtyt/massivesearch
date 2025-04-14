"""Data loader."""  # noqa: INP001

import pandas as pd


def load_data() -> pd.DataFrame:
    """Load book data from a CSV file."""
    file_path: str = "examples/book/books.csv"
    return pd.read_csv(file_path)
