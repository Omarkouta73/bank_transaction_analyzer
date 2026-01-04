"""
FeatureBuilder: Builds transaction-level features.
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple


class FeatureBuilder:
    def __init__(self):
        self.features: Optional[pd.DataFrame] = None

    def build_features(self, cleaned_data: pd.DataFrame) -> Tuple[bool, str]:
        try:
            self.features = cleaned_data

            self._add_transaction_features()
            self._add_customer_features()
            self._add_velocity_features()
            self._add_rolling_features()

            return True, f"Built features for {len(self.features):,} records"

        except Exception as e:
            return False, f"Error: {str(e)}"


    def _add_transaction_features(self) -> None:
        df = self.features

        df['balance_ratio_orig'] = np.where(
            df['oldbalanceOrg'] > 0,
            df['amount'] / df['oldbalanceOrg'],
            0
        )

        df['is_full_drain'] = (
            (df['oldbalanceOrg'] > 0) &
            (df['newbalanceOrig'] == 0)
        )

        df['hour_of_day'] = (df['step'] % 24)


    def _add_customer_features(self) -> None:
        df = self.features

        customer_grp = df.groupby('nameOrig')['amount']

        df['trns_count_customer'] = customer_grp.transform('count')
        df['trns_total_customer'] = customer_grp.transform('sum')
        df['trns_avg_customer'] = customer_grp.transform('mean')
        df['trns_max_customer'] = customer_grp.transform('max')


    def _add_velocity_features(self) -> None:
        df = self.features

        df['day'] = (df['step'] // 24)

        daily_count = (
            df.groupby(['nameOrig', 'day'])['amount']
            .transform('count')
        )

        df['daily_trns_velocity'] = daily_count


    def _add_rolling_features(self) -> None:
        df = self.features

        df.sort_values(['nameOrig', 'step'], inplace=True)

        rolling_window = 5

        df['rolling_mean_amount'] = (
            df.groupby('nameOrig')['amount']
            .rolling(rolling_window, min_periods=1)
            .mean()
            .reset_index(level=0, drop=True)
        )

        df['rolling_max_amount'] = (
            df.groupby('nameOrig')['amount']
            .rolling(rolling_window, min_periods=1)
            .max()
            .reset_index(level=0, drop=True)
        )

    def get_features(self) -> Optional[pd.DataFrame]:
        return self.features
