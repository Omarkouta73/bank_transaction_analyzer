import pandas as pd
import numpy as np
from scipy import stats
from typing import Optional, Dict, Tuple

class RiskScorer:
    """
    Computes risk scores for customers using Z-score
    """
    
    def __init__(self, z_score_threshold: float = 2.0):
        self.risk_scores: Optional[pd.DataFrame] = None
        self.z_score_threshold: float = z_score_threshold
        
        self.risk_bands = {
            'Low': (0, 25),
            'Medium': (25, 50),
            'High': (50, 75),
            'Critical': (75, 100)
        }
        
        self._risk_features = [
            'amount',                    
            'balance_ratio_orig',        
            'is_full_drain',             
            'trns_count_customer',       
            'trns_total_customer',       
            'trns_avg_customer',         
            'trns_max_customer',         
            'daily_trns_velocity',       
            'rolling_mean_amount', 
            'rolling_max_amount'   
        ]
    
    def compute_risk_scores(self, features: pd.DataFrame) -> Tuple[bool, str]:
        try:
            # Step 1: Aggregate to customer level
            self.risk_scores = self._aggregate_to_customer(features)
            
            # Step 2: Find available numeric features
            available_features = self._get_available_features()
            if not available_features:
                return False, "No features available for scoring"
            
            # Step 3: Compute Z-scores
            self._compute_z_scores(available_features)
            
            # Step 4: Compute final risk score (0-100)
            self._compute_final_score()
            
            # Step 5: Assign risk bands
            self._assign_risk_bands()
            
            # Step 6: Flag anomalies
            self._flag_anomalies()
            
            high_risk_count = (
                self.risk_scores['risk_band'].isin(['High', 'Critical']).sum()
            )
            
            return True, f"Scored {len(self.risk_scores)} customers. {high_risk_count} high/critical risk."
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False, f"Error: {str(e)}"
    
    def _aggregate_to_customer(self, features: pd.DataFrame) -> pd.DataFrame:
        if 'nameOrig' not in features.columns:
            return features
        
        agg_dict = {}
        numeric_cols = features.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if col in ['is_full_drain', 'trns_count_customer', 'daily_trns_velocity']:
                agg_dict[col] = 'sum'
            else:
                agg_dict[col] = 'mean'
        
        customer_data = features.groupby('nameOrig').agg(agg_dict).reset_index()
        return customer_data
    

    def _get_available_features(self) -> list:
        available = []
        numeric_cols = self.risk_scores.select_dtypes(include=[np.number]).columns
        for feature in self._risk_features:
            if feature in numeric_cols:
                if self.risk_scores[feature].std() > 0:
                    available.append(feature)
        return available
    
    def _compute_z_scores(self, features: list) -> None:
        for feature in features:
            col_data = self.risk_scores[feature].fillna(0)
            z_scores = stats.zscore(col_data, nan_policy='omit')
            # print(z_scores)
            # z_scores = np.nan_to_num(z_scores, nan=0.0)
            self.risk_scores[f'{feature}_zscore'] = z_scores
    
    def _compute_final_score(self) -> None:
        z_cols = [c for c in self.risk_scores.columns if c.endswith('_zscore')]
        if not z_cols:
            self.risk_scores['composite_zscore'] = 0
            self.risk_scores['risk_score'] = 0
            return
        
        self.risk_scores['composite_zscore'] = (
            self.risk_scores[z_cols].abs().mean(axis=1)
        )
        
        min_val = self.risk_scores['composite_zscore'].min()
        max_val = self.risk_scores['composite_zscore'].max()
        if max_val > min_val:
            self.risk_scores['risk_score'] = (
                (self.risk_scores['composite_zscore'] - min_val) /
                (max_val - min_val) * 100
            )
        else:
            self.risk_scores['risk_score'] = 50.0
    
    def _assign_risk_bands(self) -> None:
        def get_band(score):
            for band, (low, high) in self.risk_bands.items():
                if low <= score < high:
                    return band
            return 'Critical'
        self.risk_scores['risk_band'] = self.risk_scores['risk_score'].apply(get_band)
    
    def _flag_anomalies(self) -> None:
        self.risk_scores['is_anomaly'] = (
            self.risk_scores['composite_zscore'] > self.z_score_threshold
        ).astype(int)
    
    def get_risk_scores(self) -> Optional[pd.DataFrame]:
        if self.risk_scores is None:
            return None
        columns = ['nameOrig', 'composite_zscore', 'risk_score', 'risk_band', 'is_anomaly']
        available = [c for c in columns if c in self.risk_scores.columns]
        return self.risk_scores[available].copy()
    
    def get_full_data(self) -> Optional[pd.DataFrame]:
        return self.risk_scores.copy() if self.risk_scores is not None else None
    
    def get_high_risk_customers(self) -> pd.DataFrame:
        if self.risk_scores is None:
            return pd.DataFrame()
        mask = self.risk_scores['risk_band'].isin(['High', 'Critical'])
        return self.risk_scores[mask].sort_values('risk_score', ascending=False)
    
    def get_risk_summary(self) -> Dict:
        if self.risk_scores is None:
            return {}
        total = len(self.risk_scores)
        band_counts = self.risk_scores['risk_band'].value_counts()
        summary = {
            'total_customers': total,
            'anomalies': int(self.risk_scores['is_anomaly'].sum()),
        }
        for band in ['Low', 'Medium', 'High', 'Critical']:
            count = band_counts.get(band, 0)
            summary[band] = {
                'count': int(count),
                'percent': round(count / total * 100, 2) if total > 0 else 0
            }
        return summary