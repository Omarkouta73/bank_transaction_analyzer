from Models.data_manager import DataManager
from Models.transaction_cleaner import TransactionCleaner
from Models.feature_builder import FeatureBuilder
from Models.risk_scorer import RiskScorer
from Models.transaction_flagger import TransactionFlagger
from Models.report_generator import ReportGenerator


class MainController:
    
    def __init__(self, view):
        self.view = view
        
        self.data_manager = DataManager()
        self.transaction_cleaner = TransactionCleaner()
        self.feature_builder = FeatureBuilder()
        self.risk_scorer = RiskScorer()
        self.transaction_flagger = TransactionFlagger()
        self.report_generator = ReportGenerator()
        
        self.state = {
            'data_loaded': False,
            'data_cleaned': False,
            'features_built': False,
            'customers_scored': False,
            'transactions_flagged': False
        }
    
    def load_dataset(self, file_path: str) -> None:
        self.view.show_status("Loading...")
        
        success, message = self.data_manager.load_data(file_path)
        
        if not success:
            self.view.show_error(message)
            return
        
        self.state['data_loaded'] = True
        self._reset_downstream('data_loaded')
        
        data = self.data_manager.get_raw_data()
        self.view.show_data(data)
        self.view.show_status(message)
        self.view.show_info("Success", message)
    
    def clean_data(self) -> None:
        """Clean data."""
        if not self.state['data_loaded']:
            self.view.show_error("Load data first")
            return
        
        self.view.show_status("Cleaning...")
        
        data = self.data_manager.get_raw_data()
        success, message = self.transaction_cleaner.clean_data(data)
        
        if not success:
            self.view.show_error(message)
            return
        
        self.state['data_cleaned'] = True
        self._reset_downstream('data_cleaned')
        
        self.view.show_data(self.transaction_cleaner.get_cleaned_data())
        self.view.show_status(message)
        self.view.show_info("Success", message)
    
    def build_features(self) -> None:
        """Build features."""
        if not self.state['data_cleaned']:
            self.view.show_error("Clean data first")
            return
        
        self.view.show_status("Building features...")
        
        data = self.transaction_cleaner.get_cleaned_data()
        success, message = self.feature_builder.build_features(data)
        
        if not success:
            self.view.show_error(message)
            return
        
        self.state['features_built'] = True
        self._reset_downstream('features_built')
        
        self.view.show_data(self.feature_builder.get_features())
        self.view.show_status(message)
        self.view.show_info("Success", message)
    
    def score_customers(self) -> None:
        if not self.state['features_built']:
            self.view.show_error("Build features first")
            return
        
        self.view.show_status("Scoring customers...")
        
        features = self.feature_builder.get_features()
        success, message = self.risk_scorer.compute_risk_scores(features)
        
        if not success:
            self.view.show_error(message)
            return
        
        self.state['customers_scored'] = True
        self._reset_downstream('customers_scored')
        
        self.view.show_data(self.risk_scorer.get_risk_scores())
        self.view.show_status(message)
        self.view.show_info("Success", message)
    
    def flag_transactions(self) -> None:
        if not self.state['customers_scored']:
            self.view.show_error("Score customers first")
            return
        
        self.view.show_status("Flagging transactions...")
        
        features = self.feature_builder.get_features()
        scores = self.risk_scorer.get_risk_scores()
        
        success, message = self.transaction_flagger.flag_transactions(features, scores)
        
        if not success:
            self.view.show_error(message)
            return
        
        self.state['transactions_flagged'] = True
        
        try:
            flagged = self.transaction_flagger.get_flagged_transactions(max_rows=100)
            if flagged is not None and len(flagged) > 0:
                self.view.show_data(flagged)
            else:
                self.view.show_status("No transactions flagged")
        except Exception as e:
            print(f"Display error: {e}")
        
        self.view.show_status(message)
        self.view.show_info("Success", message)
    
    def export_reports(self) -> None:
        if not self.state['transactions_flagged']:
            self.view.show_error("Flag transactions first")
            return
        
        if not self.transaction_flagger.is_flagged():
            self.view.show_error("Flagging not completed. Try again.")
            return
        
        self.view.show_status("Exporting reports...")
        
        flagged = self.transaction_flagger.get_flagged_transactions(max_rows=50000)
        scores = self.risk_scorer.get_risk_scores()
        flag_summary = self.transaction_flagger.get_flag_summary()
        risk_summary = self.risk_scorer.get_risk_summary()
        
        success, message = self.report_generator.generate_reports(
            flagged_transactions=flagged,
            risk_scores=scores,
            flag_summary=flag_summary,
            risk_summary=risk_summary
        )
        
        if not success:
            self.view.show_error(message)
            return
        
        self.view.show_report(self.report_generator.get_report_content())
        self.view.show_status(message)
        self.view.show_info("Success", message)
    
    def display_summary(self) -> None:
        """Display summary."""
        lines = ["=" * 40, "SUMMARY", "=" * 40, ""]
        
        lines.append(f"Data Loaded: {'Yes' if self.state['data_loaded'] else 'No'}")
        lines.append(f"Data Cleaned: {'Yes' if self.state['data_cleaned'] else 'No'}")
        lines.append(f"Features Built: {'Yes' if self.state['features_built'] else 'No'}")
        lines.append(f"Customers Scored: {'Yes' if self.state['customers_scored'] else 'No'}")
        lines.append(f"Transactions Flagged: {'Yes' if self.state['transactions_flagged'] else 'No'}")
        lines.append("")
        
        if self.state['customers_scored']:
            summary = self.risk_scorer.get_risk_summary()
            lines.append("RISK DISTRIBUTION")
            lines.append("-" * 30)
            for band in ['Low', 'Medium', 'High', 'Critical']:
                data = summary.get(band, {})
                lines.append(f"  {band}: {data.get('count', 0):,}")
            lines.append("")
        
        if self.state['transactions_flagged']:
            summary = self.transaction_flagger.get_flag_summary()
            lines.append("FLAG SUMMARY")
            lines.append("-" * 30)
            lines.append(f"  Total: {summary.get('total_transactions', 0):,}")
            lines.append(f"  Flagged: {summary.get('flagged_transactions', 0):,}")
            lines.append(f"  Percentage: {summary.get('flagged_percentage', 0):.2f}%")
        
        lines.append("")
        lines.append("=" * 40)
        
        self.view.show_summary("\n".join(lines))
        self.view.show_status("Summary displayed")
    
    def _reset_downstream(self, from_state: str) -> None:
        order = [
            'data_loaded',
            'data_cleaned', 
            'features_built',
            'customers_scored',
            'transactions_flagged'
        ]
        
        try:
            pos = order.index(from_state)
            for state in order[pos + 1:]:
                self.state[state] = False
        except ValueError:
            pass