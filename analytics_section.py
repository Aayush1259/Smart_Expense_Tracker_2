"""
Analytics Section Module

This module defines the AnalyticsFrame class that displays various visual analytics
and interactive charts for expense data using both static (Matplotlib/Seaborn)
and interactive (Plotly) graphs.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import pandas as pd
import seaborn as sns
import plotly.express as px
from plotly.offline import plot
from typing import Any

from ml import (
    forecast_expenses, personalized_budget_recommendation,
    smart_expense_insights, spending_categories, balance_trend
)
from utils import parse_dates

TEXT_COLOR = "#2C3E50"
PRIMARY_COLOR = "#3498DB"
ACCENT_RED = "#E74C3C"
ACCENT_YELLOW = "#F1C40F"
ACCENT_GREEN = "#2ECC71"
ACCENT_BLUE = "#1ABC9C"
GRAY_COLOR = "#BDC3C7"
BACKGROUND_COLOR = "#FFFFFF"

ALL_CATEGORIES = [
    "Food", "Transport", "Housing", "Utilities", "Entertainment",
    "Healthcare", "Education", "Shopping", "Insurance", "Other"
]

CATEGORY_COLORS = {
    "Food": "#FF5733",         
    "Transport": "#FFC300",    
    "Housing": "#C70039",      
    "Utilities": "#900C3F",    
    "Entertainment": "#581845",
    "Healthcare": "#28B463",   
    "Education": "#1F618D",    
    "Shopping": "#D4AC0D",     
    "Insurance": "#7D3C98",    
    "Other": "#566573"         
}

class AnalyticsFrame(ttk.Frame):
    def __init__(self, parent: tk.Widget, db: Any, *args, **kwargs) -> None:
        """
        Initialize the AnalyticsFrame.
        """
        super().__init__(parent, padding="10", *args, **kwargs)
        self.db = db
        self.create_widgets()

    def create_widgets(self) -> None:
        """Create and layout UI widgets for filtering, analysis, and charts."""
        # Summary Label
        self.summary_label = ttk.Label(
            self, text="", font=("Segoe UI", 12, "italic"), foreground=PRIMARY_COLOR
        )
        self.summary_label.pack(pady=(0, 10))

        # Filter Frame for date range and category selection
        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        self._create_date_range_widgets(filter_frame)
        self._create_category_selection(filter_frame)

        # Analysis Type and Analyze Button
        analysis_frame = ttk.Frame(self)
        analysis_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(analysis_frame, text="Analysis Type:", foreground=TEXT_COLOR).pack(side=tk.LEFT, padx=5)
        self.analysis_type = tk.StringVar(value="Monthly")
        for opt in ["Weekly", "Monthly", "Yearly"]:
            ttk.Radiobutton(analysis_frame, text=opt, variable=self.analysis_type, value=opt).pack(side=tk.LEFT, padx=5)
        ttk.Button(analysis_frame, text="Analyze", command=self.show_analysis).pack(side=tk.RIGHT, padx=5)

        # AI/ML Feature Buttons
        ai_frame = ttk.Frame(self)
        ai_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(ai_frame, text="Forecast Expenses", command=self.show_forecast).pack(side=tk.LEFT, padx=5)
        ttk.Button(ai_frame, text="Budget Recommendation", command=self.show_budget_recommendation).pack(side=tk.LEFT, padx=5)
        ttk.Button(ai_frame, text="Spending Categories", command=self.show_spending_categories).pack(side=tk.LEFT, padx=5)
        ttk.Button(ai_frame, text="Balance Trend", command=self.show_balance_trend).pack(side=tk.LEFT, padx=5)
        ttk.Button(ai_frame, text="Interactive Chart", command=self.show_interactive_chart).pack(side=tk.LEFT, padx=5)

        # Canvas Frame for Charts
        self.canvas_frame = ttk.Frame(self)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        # Initialize Summary
        self.update_summary()

    def _create_date_range_widgets(self, parent: ttk.Frame) -> None:
        """Create date range selection widgets."""
        ttk.Label(parent, text="From:", foreground=TEXT_COLOR).grid(row=0, column=0, padx=5, sticky="e")
        self.start_date = DateEntry(parent, width=12, background="white", foreground=TEXT_COLOR, date_pattern="yyyy-mm-dd")
        self.start_date.grid(row=0, column=1, padx=5)
        ttk.Label(parent, text="To:", foreground=TEXT_COLOR).grid(row=0, column=2, padx=5, sticky="e")
        self.end_date = DateEntry(parent, width=12, background="white", foreground=TEXT_COLOR, date_pattern="yyyy-mm-dd")
        self.end_date.grid(row=0, column=3, padx=5)

    def _create_category_selection(self, parent: ttk.Frame) -> None:
        """Create multi-select category listbox widget."""
        ttk.Label(parent, text="Categories:", foreground=TEXT_COLOR).grid(
            row=1, column=0, sticky="e", padx=5, pady=(5, 0)
        )
        self.category_listbox = tk.Listbox(parent, selectmode=tk.MULTIPLE, height=5, exportselection=False)
        for cat in ALL_CATEGORIES:
            self.category_listbox.insert(tk.END, cat)
        self.category_listbox.grid(row=1, column=1, columnspan=3, sticky="we", padx=5, pady=(5, 0))

    def update_summary(self) -> None:
        """Update the summary label with overall expense insights."""
        data = pd.DataFrame(
            self.db.get_expenses(),
            columns=["id", "date", "amount", "category", "description"]
        )
        insights = smart_expense_insights(data)
        self.summary_label.config(text=f"Expense Insights: {insights}")

    def show_analysis(self) -> None:
        """Retrieve and filter expense data, then display a bar chart and a pie chart."""
        data = pd.DataFrame(
            self.db.get_expenses(),
            columns=["id", "date", "amount", "category", "description"]
        )
        if data.empty:
            messagebox.showinfo("No Data", "No expense data available.")
            return

        data = parse_dates(data, "date")
        data = self._apply_date_filter(data)
        if data.empty:
            messagebox.showinfo("No Data", "No expense data within the selected date range.")
            return

        data = self._apply_category_filter(data)
        if data.empty:
            messagebox.showinfo("No Data", "No expense data for the selected categories.")
            return

        self._clear_charts()
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        sns.set_style("whitegrid")
        sns.set_palette([ACCENT_RED, ACCENT_YELLOW, ACCENT_BLUE])
        data.set_index("date", inplace=True)

        freq, label = self._get_resample_params()
        df_resampled = data.resample(freq).sum()
        self.plot_barchart(ax1, df_resampled, label)
        self.plot_pie_chart(ax2, data.reset_index())
        fig.tight_layout(pad=1.0)
        self.plot_canvas(fig)

    def _apply_date_filter(self, data: pd.DataFrame) -> pd.DataFrame:
        """Filter the data by the selected date range."""
        start = pd.to_datetime(self.start_date.get_date())
        end = pd.to_datetime(self.end_date.get_date())
        return data[(data["date"] >= start) & (data["date"] <= end)]

    def _apply_category_filter(self, data: pd.DataFrame) -> pd.DataFrame:
        """Filter the data by the selected categories."""
        selected_indices = self.category_listbox.curselection()
        if selected_indices:
            selected_cats = [self.category_listbox.get(i) for i in selected_indices]
            data = data[data["category"].isin(selected_cats)]
        return data

    def _get_resample_params(self) -> tuple[str, str]:
        """Return resampling parameters based on the analysis type."""
        freq = self.analysis_type.get()
        if freq == "Weekly":
            return "W-Mon", "Weekly"
        elif freq == "Monthly":
            return "M", "Monthly"
        else:
            return "Y", "Yearly"

    def plot_barchart(self, ax: Any, df: pd.DataFrame, label: str) -> None:
        """Plot a bar chart for aggregated expense amounts."""
        if df.empty:
            ax.text(0.5, 0.5, "No data", ha="center", va="center", color=PRIMARY_COLOR, fontsize=12)
            return

        bars = ax.bar(df.index, df["amount"], color=PRIMARY_COLOR)
        ax.set_title(f"{label} Expense Trend", fontsize=14, fontweight="bold", color=PRIMARY_COLOR)
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Total Amount (₹)", fontsize=12)

        locator = mdates.AutoDateLocator()
        formatter = mdates.ConciseDateFormatter(locator)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)

        if len(df) <= 20:
            for bar in bars:
                height = bar.get_height()
                label_str = f'₹{height/1000:.1f}k' if height >= 1000 else f'₹{height:,.0f}'
                ax.annotate(
                    label_str,
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', color=TEXT_COLOR, fontsize=8
                )
        else:
            ax.text(0.5, 0.95, "Labels skipped (too many bars)",
                    ha='center', va='top', transform=ax.transAxes,
                    fontsize=9, color="#555555")

        ax.tick_params(axis="both", labelsize=10)
        ax.grid(True, linestyle="--", alpha=0.7)
        ax.set_axisbelow(True)

    def plot_pie_chart(self, ax: Any, data: pd.DataFrame) -> None:
        """Plot a pie chart of expense distribution by category."""
        cat_totals = data.groupby("category")["amount"].sum()
        if cat_totals.empty:
            ax.text(0.5, 0.5, "No data", ha="center", va="center", color=PRIMARY_COLOR, fontsize=12)
        else:
            colors = [CATEGORY_COLORS.get(cat, ACCENT_BLUE) for cat in cat_totals.index]
            explode = [0.1] + [0] * (len(cat_totals) - 1)
            ax.pie(
                cat_totals, labels=cat_totals.index, autopct='%1.1f%%',
                startangle=90, colors=colors, explode=explode,
                textprops={'fontsize': 10, 'color': TEXT_COLOR}
            )
            ax.set_title("Expense Distribution by Category", fontsize=14, fontweight="bold", color=PRIMARY_COLOR)

    def show_forecast(self) -> None:
        """Display forecasted expense data using linear regression."""
        data = self._get_data()
        if data.empty:
            return
        forecast_df = forecast_expenses(data, periods=1)
        if forecast_df.empty:
            messagebox.showinfo("Forecast", "Unable to forecast.")
            return
        self._clear_charts()
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.plot(forecast_df["date"], forecast_df["forecast"], marker='o', color=ACCENT_RED)
        ax.set_title("Next Month Forecast", fontsize=14, fontweight="bold", color=ACCENT_RED)
        ax.set_xlabel("Forecast Date", fontsize=12)
        ax.set_ylabel("Forecast Amount (₹)", fontsize=12)
        locator = mdates.AutoDateLocator()
        formatter = mdates.ConciseDateFormatter(locator)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
        ax.tick_params(axis="both", labelsize=10)
        self.plot_canvas(fig)

    def show_budget_recommendation(self) -> None:
        """Display personalized budget recommendations per category."""
        data = self._get_data()
        if data.empty:
            return
        recommendations = personalized_budget_recommendation(data)
        if not recommendations:
            messagebox.showinfo("Budget Recommendation", "Not enough data for recommendations.")
            return
        self._clear_charts()
        fig, ax = plt.subplots(figsize=(6, 3))
        categories = list(recommendations.keys())
        try:
            budget_values = [
                float(str(value).replace("₹", "").replace(",", ""))
                for value in recommendations.values()
            ]
        except Exception as e:
            messagebox.showerror("Budget Recommendation Error", f"Error processing budget values: {e}")
            return
        ax.bar(categories, budget_values, color=ACCENT_YELLOW)
        ax.set_title("Budget Recommendations", fontsize=14, fontweight="bold", color=ACCENT_YELLOW)
        ax.set_xlabel("Category", fontsize=12)
        ax.set_ylabel("Recommended Budget (₹)", fontsize=12)
        ax.tick_params(axis="both", labelsize=10)
        self.plot_canvas(fig)

    def show_spending_categories(self) -> None:
        """Display spending categorized as Must, Need, and Want."""
        data = self._get_data()
        if data.empty:
            return
        spending_data = spending_categories(data)
        self._clear_charts()
        fig, ax = plt.subplots(figsize=(6, 3))
        categories = list(spending_data.keys())
        amounts = list(spending_data.values())
        colors = [CATEGORY_COLORS.get(cat, ACCENT_BLUE) for cat in categories]
        ax.bar(categories, amounts, color=colors)
        ax.set_title("Spending Categories", fontsize=14, fontweight="bold", color=ACCENT_BLUE)
        ax.set_xlabel("Category", fontsize=12)
        ax.set_ylabel("Amount Spent (₹)", fontsize=12)
        ax.tick_params(axis="both", labelsize=10)
        self.plot_canvas(fig)

    def show_balance_trend(self) -> None:
        """Display cumulative balance trend over time."""
        data = self._get_data()
        if data.empty:
            return
        trend_data = balance_trend(data)
        self._clear_charts()
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.plot(trend_data["date"], trend_data["cumulative"], color=ACCENT_GREEN, marker="o")
        ax.set_title("Balance Trend", fontsize=14, fontweight="bold", color=ACCENT_GREEN)
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Cumulative Amount (₹)", fontsize=12)
        locator = mdates.AutoDateLocator()
        formatter = mdates.ConciseDateFormatter(locator)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
        ax.tick_params(axis="both", labelsize=10)
        self.plot_canvas(fig)

    def show_interactive_chart(self) -> None:
        """Open an interactive expense trend chart in the web browser."""
        data = self._get_data()
        if data.empty:
            return
        fig = px.line(
            data, x="date", y="amount", color="category",
            title="Expense Trend (Interactive)",
            labels={"amount": "Amount (₹)", "date": "Date"}
        )
        fig.update_layout(template="plotly_dark", xaxis_title="Date", yaxis_title="Expense (₹)")
        plot(fig, auto_open=True)

    def _get_data(self) -> pd.DataFrame:
        """Retrieve and parse expense data from the database."""
        data = pd.DataFrame(
            self.db.get_expenses(),
            columns=["id", "date", "amount", "category", "description"]
        )
        if data.empty:
            messagebox.showinfo("No Data", "No expense data available.")
            return pd.DataFrame()
        return parse_dates(data, "date")

    def _clear_charts(self) -> None:
        """Clear any existing charts from the canvas frame."""
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

    def plot_canvas(self, figure: plt.Figure) -> None:
        """Embed a matplotlib figure in the Tkinter canvas."""
        canvas = FigureCanvasTkAgg(figure, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        plt.close(figure)
