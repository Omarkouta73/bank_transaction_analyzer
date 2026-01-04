"""
MainView: Tkinter GUI for Bank Analyzer application.
Simple and clean implementation.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from typing import Optional, Callable
import pandas as pd


class MainView:
    """
    Main GUI window for the Bank Analyzer application.
    """
    
    def __init__(self):
        """Initialize the main view."""
        self.root = tk.Tk()
        self.root.title("Bank Transaction Analyzer")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Presenter reference (set later)
        self.presenter = None
        
        # Status variable
        self.status_var = tk.StringVar(value="Ready")
        
        # Setup UI components
        self._setup_menu()
        self._setup_main_frame()
        self._setup_status_bar()
    
    def set_presenter(self, presenter) -> None:
        """
        Set the presenter reference.
        
        Args:
            presenter: MainPresenter instance
        """
        self.presenter = presenter
    
    # ==================== UI SETUP ====================
    
    def _setup_menu(self) -> None:
        """Setup the menu bar."""
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # File Menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Dataset", command=self._on_load_dataset)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_exit)
        
        # Process Menu
        process_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Process", menu=process_menu)
        process_menu.add_command(label="Clean and Validate Data", command=self._on_clean_data)
        process_menu.add_command(label="Build Features", command=self._on_build_features)
        process_menu.add_command(label="Score Customers", command=self._on_score_customers)
        process_menu.add_command(label="Flag Suspicious Transactions", command=self._on_flag_transactions)
        
        # Reports Menu
        reports_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Reports", menu=reports_menu)
        reports_menu.add_command(label="Export Reports", command=self._on_export_reports)
        reports_menu.add_command(label="Display Summary", command=self._on_display_summary)
        
        # Help Menu
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._on_about)
    
    def _setup_main_frame(self) -> None:
        """Setup the main content frame."""
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top frame - Buttons
        self._setup_button_frame()
        
        # Middle frame - Notebook with tabs
        self._setup_notebook()
    
    def _setup_button_frame(self) -> None:
        """Setup the button toolbar."""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Buttons
        ttk.Button(
            button_frame, 
            text="1. Load Data", 
            command=self._on_load_dataset
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame, 
            text="2. Clean Data", 
            command=self._on_clean_data
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame, 
            text="3. Build Features", 
            command=self._on_build_features
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame, 
            text="4. Score Customers", 
            command=self._on_score_customers
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame, 
            text="5. Flag Transactions", 
            command=self._on_flag_transactions
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame, 
            text="6. Export Reports", 
            command=self._on_export_reports
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame, 
            text="7. Show Summary", 
            command=self._on_display_summary
        ).pack(side=tk.LEFT, padx=2)
    
    def _setup_notebook(self) -> None:
        """Setup the tabbed notebook."""
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Data View
        self.data_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.data_frame, text="Data View")
        self._setup_data_tab()
        
        # Tab 2: Summary View
        self.summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_frame, text="Summary")
        self._setup_summary_tab()
        
        # Tab 3: Report View
        self.report_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.report_frame, text="Report")
        self._setup_report_tab()
    
    def _setup_data_tab(self) -> None:
        """Setup the data view tab with treeview."""
        # Treeview for data display
        tree_frame = ttk.Frame(self.data_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbars
        y_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        x_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        
        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )
        
        y_scroll.config(command=self.tree.yview)
        x_scroll.config(command=self.tree.xview)
        
        # Pack
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)
    
    def _setup_summary_tab(self) -> None:
        """Setup the summary tab with text display."""
        self.summary_text = scrolledtext.ScrolledText(
            self.summary_frame,
            wrap=tk.WORD,
            font=("Courier", 10)
        )
        self.summary_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _setup_report_tab(self) -> None:
        """Setup the report tab with text display."""
        self.report_text = scrolledtext.ScrolledText(
            self.report_frame,
            wrap=tk.WORD,
            font=("Courier", 10)
        )
        self.report_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _setup_status_bar(self) -> None:
        """Setup the status bar."""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Label(
            status_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2)
        ).pack(fill=tk.X)
    
    # ==================== EVENT HANDLERS ====================
    
    def _on_load_dataset(self) -> None:
        """Handle load dataset action."""
        if not self.presenter:
            self.show_error("Presenter not set")
            return
        
        file_path = filedialog.askopenfilename(
            title="Select Dataset",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            self.presenter.load_dataset(file_path)
    
    def _on_clean_data(self) -> None:
        """Handle clean data action."""
        if self.presenter:
            self.presenter.clean_data()
    
    def _on_build_features(self) -> None:
        """Handle build features action."""
        if self.presenter:
            self.presenter.build_features()
    
    def _on_score_customers(self) -> None:
        """Handle score customers action."""
        if self.presenter:
            self.presenter.score_customers()
    
    def _on_flag_transactions(self) -> None:
        """Handle flag transactions action."""
        if self.presenter:
            self.presenter.flag_transactions()
    
    def _on_export_reports(self) -> None:
        """Handle export reports action."""
        if self.presenter:
            self.presenter.export_reports()
    
    def _on_display_summary(self) -> None:
        """Handle display summary action."""
        if self.presenter:
            self.presenter.display_summary()
    
    def _on_exit(self) -> None:
        """Handle exit action."""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.quit()
    
    def _on_about(self) -> None:
        """Handle about action."""
        messagebox.showinfo(
            "About",
            "Bank Transaction Analyzer\n\n"
            "A tool for analyzing and flagging\n"
            "suspicious bank transactions.\n\n"
            "Version 1.0"
        )
    
    # ==================== DISPLAY METHODS ====================
    
    def show_status(self, message: str) -> None:
        """
        Update status bar message.
        
        Args:
            message: Status message to display
        """
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def show_info(self, title: str, message: str) -> None:
        """
        Show info message box.
        
        Args:
            title: Message box title
            message: Message to display
        """
        messagebox.showinfo(title, message)
    
    def show_error(self, message: str) -> None:
        """
        Show error message box.
        
        Args:
            message: Error message to display
        """
        messagebox.showerror("Error", message)
    
    def show_data(self, data: pd.DataFrame, max_rows: int = 1000) -> None:
        """
        Display DataFrame in the treeview.
        
        Args:
            data: DataFrame to display
            max_rows: Maximum rows to show
        """
        # Clear existing data
        self.tree.delete(*self.tree.get_children())
        
        # Setup columns
        columns = list(data.columns)
        self.tree["columns"] = columns
        self.tree["show"] = "headings"
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, minwidth=50)
        
        # Insert rows (limit for performance)
        display_data = data.head(max_rows)
        for _, row in display_data.iterrows():
            values = [str(v) for v in row.values]
            self.tree.insert("", tk.END, values=values)
        
        # Switch to data tab
        self.notebook.select(0)
        
        if len(data) > max_rows:
            self.show_status(f"Showing {max_rows} of {len(data)} rows")
    
    def show_summary(self, summary_text: str) -> None:
        """
        Display summary text.
        
        Args:
            summary_text: Summary text to display
        """
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, summary_text)
        
        # Switch to summary tab
        self.notebook.select(1)
    
    def show_report(self, report_text: str) -> None:
        """
        Display report text.
        
        Args:
            report_text: Report text to display
        """
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, report_text)
        
        # Switch to report tab
        self.notebook.select(2)
    
    def clear_all(self) -> None:
        """Clear all displays."""
        # Clear treeview
        self.tree.delete(*self.tree.get_children())
        
        # Clear text areas
        self.summary_text.delete(1.0, tk.END)
        self.report_text.delete(1.0, tk.END)
        
        # Reset status
        self.status_var.set("Ready")
    
    # ==================== RUN ====================
    
    def run(self) -> None:
        """Start the main event loop."""
        self.root.mainloop()