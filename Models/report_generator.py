import pandas as pd
import os
from datetime import datetime
from typing import Optional, Dict, Tuple


class ReportGenerator:
    """
    Generates reports
    """
    
    def __init__(self, output_dir: str = "outputs"):
        self.output_dir: str = output_dir
        self.report_paths: Dict[str, str] = {}
    
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def generate_reports(self, flagged_transactions: pd.DataFrame, risk_scores: pd.DataFrame, flag_summary: Dict, risk_summary: Dict) -> Tuple[bool, str]:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._generate_flagged_csv(flagged_transactions, timestamp)
            self._generate_risk_csv(risk_scores, timestamp)
            self._generate_text_report(flag_summary, risk_summary, timestamp)
            
            return True, f"Reports saved to '{self.output_dir}/' folder"
            
        except Exception as e:
            return False, f"Error generating reports: {str(e)}"
    
    def _generate_flagged_csv(self, flagged_transactions: pd.DataFrame, timestamp: str) -> None:
        filename = f"flagged_transactions.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        columns_to_export = [
            'nameOrig', 'nameDest', 'type', 'amount',
            'oldbalanceOrg', 'newbalanceOrig',
            'risk_score', 'risk_band', 'flag_reasons'
        ]
        
        available = [c for c in columns_to_export if c in flagged_transactions.columns]
        
        flagged_transactions[available].to_csv(filepath, index=False)
        self.report_paths['flagged_csv'] = filepath
    
    def _generate_risk_csv(self, risk_scores: pd.DataFrame, timestamp: str) -> None:
        filename = f"customer_risk_summary.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        sorted_scores = risk_scores.sort_values('risk_score', ascending=False)
        
        sorted_scores.to_csv(filepath, index=False)
        self.report_paths['risk_csv'] = filepath
    
    def _generate_text_report(self, flag_summary: Dict, risk_summary: Dict, timestamp: str) -> None:
        filename = f"report.txt"
        filepath = os.path.join(self.output_dir, filename)
        
        report_lines = []
        
        report_lines.append("=" * 60)
        report_lines.append("BANK TRANSACTION ANALYSIS REPORT")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("=" * 60)
        report_lines.append("")
        
        report_lines.append("-" * 40)
        report_lines.append("TRANSACTION FLAGGING SUMMARY")
        report_lines.append("-" * 40)
        report_lines.append(f"Total Transactions: {flag_summary.get('total_transactions', 0):,}")
        report_lines.append(f"Flagged Transactions: {flag_summary.get('flagged_transactions', 0):,}")
        report_lines.append(f"Flagged Percentage: {flag_summary.get('flagged_percentage', 0):.2f}%")
        report_lines.append(f"Risk Threshold Used: {flag_summary.get('risk_threshold_used', 'N/A')}")
        report_lines.append("")
        
        report_lines.append("Flagged by Risk Band:")
        by_band = flag_summary.get('by_risk_band', {})
        for band in ['Critical', 'High', 'Medium']:
            count = by_band.get(band, 0)
            report_lines.append(f"  - {band}: {count:,}")
        report_lines.append("")
        
        # Customer Risk Summary
        report_lines.append("-" * 40)
        report_lines.append("CUSTOMER RISK SUMMARY")
        report_lines.append("-" * 40)
        report_lines.append(f"Total Customers Scored: {risk_summary.get('total_customers', 0):,}")
        report_lines.append(f"Anomalies Detected: {risk_summary.get('anomalies', 0):,}")
        report_lines.append("")
        
        # Risk Band Distribution
        report_lines.append("Risk Band Distribution:")
        for band in ['Low', 'Medium', 'High', 'Critical']:
            band_data = risk_summary.get(band, {})
            count = band_data.get('count', 0)
            percent = band_data.get('percent', 0)
            report_lines.append(f"  - {band}: {count:,} ({percent:.2f}%)")
        report_lines.append("")
        
        # Recommendations
        report_lines.append("-" * 40)
        report_lines.append("RECOMMENDATIONS")
        report_lines.append("-" * 40)
        
        critical_count = by_band.get('Critical', 0)
        high_count = by_band.get('High', 0)
        
        if critical_count > 0:
            report_lines.append(f"1. URGENT: Review {critical_count:,} critical risk transactions immediately")
        
        if high_count > 0:
            report_lines.append(f"2. HIGH PRIORITY: Investigate {high_count:,} high risk transactions")
        
        anomalies = risk_summary.get('anomalies', 0)
        if anomalies > 0:
            report_lines.append(f"3. Review {anomalies:,} anomaly customers for unusual patterns")
        
        report_lines.append("")
        
        # Footer
        report_lines.append("=" * 60)
        report_lines.append("END OF REPORT")
        report_lines.append("=" * 60)
        
        # Write to file
        with open(filepath, 'w') as f:
            f.write('\n'.join(report_lines))
        
        self.report_paths['text_report'] = filepath
    
    
    def get_report_paths(self) -> Dict[str, str]:
        """Get paths to generated reports."""
        return self.report_paths.copy()
    
    def get_report_content(self) -> Optional[str]:
        """Read and return text report content."""
        if 'text_report' not in self.report_paths:
            return None
        
        filepath = self.report_paths['text_report']
        
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'r') as f:
            return f.read()