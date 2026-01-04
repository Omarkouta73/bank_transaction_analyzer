import pandas as pd
from typing import Optional, Dict, List, Tuple
import os


class DataManager:
    # Manages data loading and validation operations.
    
    def __init__(self):
        self.raw_data: Optional[pd.DataFrame] = None
        self.file_path: str = ""


        self.is_loaded: bool = False
        self.required_columns: List[str] = [
            'step', 'type', 'amount', 'nameOrig', 
            'oldbalanceOrg', 'newbalanceOrig', 'nameDest', 
            'oldbalanceDest', 'newbalanceDest', 'isFraud',
            'isFlaggedFraud'
        ]
        self._validation_errors: List[str] = []
    
    def load_data(self, file_path: str) -> Tuple[bool, str]:
        try:
            if not os.path.exists(file_path):
                return False, f"File not found: {file_path}"

            if not file_path.endswith(".csv"):
                return False, "Only CSV files are supported"

            feather_path = file_path.replace(".csv", ".feather")

            if (
                os.path.exists(feather_path)
                and os.path.getmtime(feather_path) >= os.path.getmtime(file_path)
            ):
                self.raw_data = pd.read_feather(feather_path)
                source = "feather File (cached)"
            else:
                self.raw_data = pd.read_csv(file_path, low_memory=False)
                self.raw_data.reset_index(drop=True).to_feather(feather_path)
                source = "CSV File"

            self.file_path = file_path
            self.is_loaded = True

            is_valid, _ = self.validate_data()

            if is_valid:
                return True, (
                    f"Successfully loaded {self.raw_data.shape[0]} records from {source}"
                )
            else:
                return False, (
                    f"Data is not valid!"
                )

        except Exception as e:
            return False, str(e)
    
    def validate_data(self) -> Tuple[bool, List[str]]:
        self._validation_errors = []
        
        if not self.is_loaded or self.raw_data is None:
            self._validation_errors.append("No data loaded")
            return False, self._validation_errors
        
        missing_columns = [col for col in self.required_columns 
                         if col not in self.raw_data.columns]
        
        if missing_columns:
            self._validation_errors.append(
                f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        if len(self.raw_data) == 0:
            self._validation_errors.append("Dataset is empty")
        
        # duplicate_count = self.raw_data.duplicated().sum()
        # if duplicate_count > 0:
        #     self._validation_errors.append(
        #         f"Found {duplicate_count} duplicate rows"
        #     )

        # null_counts = self.raw_data.isna().sum()
        # columns_with_nulls = null_counts[null_counts > 0]

        # for col, count in columns_with_nulls.items():
        #     self._validation_errors.append(
        #         f"Column '{col}' has {count} null values"
        #     )
        
        # numeric_columns = self.raw_data.select_dtypes(include=["number"]).columns

        # for col in numeric_columns:
        #     non_numeric = (
        #         pd.to_numeric(self.raw_data[col], errors="coerce").isna() & self.raw_data[col].notna()
        #     ).sum()

        #     if non_numeric > 0:
        #         self._validation_errors.append(
        #             f"Found {non_numeric} non-numeric values in '{col}' column"
        #         )
        
        is_valid = len(self._validation_errors) == 0
        return is_valid, self._validation_errors
    
    def get_raw_data(self) -> Optional[pd.DataFrame]:
        return self.raw_data.copy() if self.raw_data is not None else None