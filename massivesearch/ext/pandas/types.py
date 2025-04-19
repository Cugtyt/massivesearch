"""Types for pandas search engine."""

import pandas as pd
from pydantic import BaseModel


class PandasBaseSearchEngineMixin(BaseModel):
    """Pandas base search engine."""

    file_path: str
    column_name: str

    def load_df(self) -> pd.DataFrame:
        """Load data for the search engine."""
        return pd.read_csv(self.file_path)
