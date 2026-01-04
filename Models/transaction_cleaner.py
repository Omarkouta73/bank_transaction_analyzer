import pandas as pd
from typing import Optional, Dict, Tuple


class TransactionCleaner:
    def __init__(self):
        self.cleaned_data: Optional[pd.DataFrame] = None
        self.missing_value_count: int = 0
        self.duplicate_count: int = 0
        self.invalid_value_count: int = 0
    
    def clean_data(self, raw_data: pd.DataFrame) -> Tuple[bool, str]:
        try:
            self.cleaned_data = raw_data.copy()
            
            self._handle_missing_values()
            
            self._remove_duplicates()
            
            # self._convert_timestamps()
            
            self._handle_invalid_values()
                        
            total_issues = self.missing_value_count + self.duplicate_count + self.invalid_value_count
            
            message = (f"Cleaning complete. Handled {total_issues} issues: "
                      f"{self.missing_value_count} missing values, "
                      f"{self.duplicate_count} duplicates, "
                      f"{self.invalid_value_count} invalid values")
            
            return True, message
            
        except Exception as e:
            return False, f"Error during cleaning: {str(e)}"
    
    def _handle_missing_values(self) -> None:
        initial_missing = self.cleaned_data.isnull().sum().sum()

        if initial_missing > 0:
            numeric_columns = self.cleaned_data.select_dtypes(include=["number"]).columns
            
            for col in numeric_columns:
                median_amount = self.cleaned_data[col].median()
                self.cleaned_data[col].fillna(median_amount, inplace=True)
            
            categorical_columns = self.cleaned_data.select_dtypes(include=["object", "category"]).columns

            for col in categorical_columns:
                if self.cleaned_data[col].isna().any():
                    mode = self.cleaned_data[col].mode()
                    self.cleaned_data[col] = self.cleaned_data[col].fillna(mode.iloc[0])
            
        final_missing = self.cleaned_data.isnull().sum().sum()
        self.missing_value_count = initial_missing - final_missing
    
    def _remove_duplicates(self) -> None:
        initial_count = len(self.cleaned_data)
        self.cleaned_data.drop_duplicates(inplace=True)    
        self.duplicate_count = initial_count - len(self.cleaned_data)

    
    def _convert_timestamps(self) -> None:
        if self.cleaned_data is None:
            return

        for col in self.cleaned_data.columns:
            if pd.api.types.is_numeric_dtype(self.cleaned_data[col]):
                continue

            try:
                converted = pd.to_datetime(
                    self.cleaned_data[col],
                    errors="coerce",
                    infer_datetime_format=True,
                    utc=True
                )

                if converted.notna().sum() > 0:
                    self.cleaned_data[col] = converted

            except Exception:
                continue

    
    def _handle_invalid_values(self) -> None:      
        if 'amount' in self.cleaned_data.columns:
            negative_mask = self.cleaned_data['amount'] < 0
            negative_count = negative_mask.sum()
            self.invalid_value_count += negative_count
            if negative_count > 0:
                self.cleaned_data.loc[negative_mask, 'amount'] = 0
    
    def get_cleaned_data(self) -> Optional[pd.DataFrame]:
        return self.cleaned_data.copy() if self.cleaned_data is not None else None
    
    def get_cleaning_stats(self) -> Dict:
        stats = {
            'missing_values_handled': self.missing_value_count,
            'duplicates_removed': self.duplicate_count,
            'invalid_value_count': self.invalid_value_count,
            'total_issues_resolved': (
                self.missing_value_count + 
                self.duplicate_count +
                self.invalid_value_count
            ),
            'final_record_count': (
                len(self.cleaned_data) if self.cleaned_data is not None else 0
            )
        }
        return stats
