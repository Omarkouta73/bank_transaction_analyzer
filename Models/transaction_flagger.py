import pandas as pd
import numpy as np
from typing import Optional, Dict, Tuple


class TransactionFlagger:
    
    def __init__(self, risk_threshold: float = 50.0):
        self.flagged_data: Optional[pd.DataFrame] = None
        self.risk_threshold = risk_threshold
        self._summary: Dict = {}
        self._is_flagged: bool = False
    
    def flag_transactions(
        self, 
        transactions: pd.DataFrame,
        risk_scores: pd.DataFrame
    ) -> Tuple[bool, str]:
        try:
            self.flagged_data = transactions
            
            score_map = dict(zip(
                risk_scores['nameOrig'], 
                risk_scores['risk_score']
            ))
            band_map = dict(zip(
                risk_scores['nameOrig'], 
                risk_scores['risk_band']
            ))
            anomaly_map = dict(zip(
                risk_scores['nameOrig'], 
                risk_scores['is_anomaly']
            ))
            
            self.flagged_data['risk_score'] = (
                self.flagged_data['nameOrig'].map(score_map).fillna(0)
            )
            self.flagged_data['risk_band'] = (
                self.flagged_data['nameOrig'].map(band_map).fillna('Low')
            )
            self.flagged_data['is_anomaly'] = (
                self.flagged_data['nameOrig'].map(anomaly_map).fillna(0)
            )
            
            self.flagged_data['is_flagged'] = (self.flagged_data['risk_score'] >= self.risk_threshold)
            
            total = len(self.flagged_data)
            flagged_count = int(self.flagged_data['is_flagged'].sum())
            
            self._summary = {
                'total_transactions': total,
                'flagged_transactions': flagged_count,
                'flagged_percentage': round(flagged_count / total * 100, 2) if total > 0 else 0,
                'by_risk_band': {
                    'Critical': int((self.flagged_data['risk_band'] == 'Critical').sum()),
                    'High': int((self.flagged_data['risk_band'] == 'High').sum()),
                    'Medium': int((self.flagged_data['risk_band'] == 'Medium').sum())
                },
                'risk_threshold_used': self.risk_threshold,
                'anomalies': int(self.flagged_data['is_anomaly'].sum())
            }
            
            self._is_flagged = True
            
            percentage = flagged_count / total * 100 if total > 0 else 0
            return True, f"Flagged {flagged_count:,} of {total:,} transactions ({percentage:.1f}%)"
            
        except Exception as e:
            self._is_flagged = False
            return False, f"Error: {str(e)}"
    
    def is_flagged(self) -> bool:
        return self._is_flagged
    
    def get_flagged_transactions(self, max_rows: int = 10000) -> Optional[pd.DataFrame]:
        if self.flagged_data is None:
            return None
        
        flagged = self.flagged_data[self.flagged_data['is_flagged'] == 1]
        
        if len(flagged) > max_rows:
            return flagged.head(max_rows)
        
        return flagged
    
    def get_flagged_count(self) -> int:
        if self.flagged_data is None:
            return 0
        return int(self.flagged_data['is_flagged'].sum())
    
    def get_flag_summary(self) -> Dict:
        return self._summary
    