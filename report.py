"""
Report Generation Module

Generates PDF and HTML reports from expense data, including graphical representations 
such as pie charts and bar graphs for analysis.
"""

import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from typing import Dict, Optional
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from utils import parse_dates, clean_dataframe


# -------- Utility Functions -------- #

def save_expense_chart(data: pd.DataFrame, filename: str) -> str:
    """
    Generates and saves a pie chart of expense categories.
    """
    try:
        if "amount" not in data.columns or "category" not in data.columns:
            raise ValueError("Missing required columns: 'amount' or 'category'")

        data["amount"] = pd.to_numeric(data["amount"], errors="coerce").fillna(0)
        category_totals = data.groupby("category")["amount"].sum()

        if category_totals.empty:
            raise ValueError("No valid data available for pie chart.")

        plt.figure(figsize=(6, 6))
        sns.set_palette("pastel")
        category_totals.plot.pie(autopct="%1.1f%%", startangle=90, wedgeprops={'edgecolor': 'black'})
        plt.title("Expense Breakdown by Category", fontsize=14, fontweight="bold")
        plt.ylabel("")
        chart_path = f"{filename}_chart.png"
        plt.savefig(chart_path, bbox_inches="tight")
        plt.close()
        return chart_path
    except Exception as e:
        print("Error generating pie chart:", e)
        return ""


def save_expense_bar_chart(data: pd.DataFrame, filename: str) -> str:
    """
    Generates and saves a bar chart of expenses over time.
    """
    try:
        if "date" not in data.columns or "amount" not in data.columns:
            raise ValueError("Missing required columns: 'date' or 'amount'")

        data = parse_dates(data, "date")
        data["amount"] = pd.to_numeric(data["amount"], errors="coerce").fillna(0)
        daily_totals = data.groupby("date")["amount"].sum()

        if daily_totals.empty:
            raise ValueError("No valid data available for bar chart.")

        plt.figure(figsize=(8, 4))
        sns.barplot(x=daily_totals.index.strftime("%Y-%m-%d"), y=daily_totals.values, palette="coolwarm")
        plt.xticks(rotation=45)
        plt.xlabel("Date", fontsize=12, fontweight="bold")
        plt.ylabel("Total Amount (₹)", fontsize=12, fontweight="bold")
        plt.title("Daily Expense Trend", fontsize=14, fontweight="bold")
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        chart_path = f"{filename}_bar_chart.png"
        plt.savefig(chart_path, bbox_inches="tight")
        plt.close()
        return chart_path
    except Exception as e:
        print("Error generating bar chart:", e)
        return ""


# -------- PDF Report Generation -------- #

def generate_pdf_report(data: pd.DataFrame, filename: str, filters: Optional[Dict] = None) -> bool:
    """
    Generates a PDF report containing expense details, pie charts, and bar graphs.
    """
    try:
        data = clean_dataframe(data)

        if data.empty:
            print("Error: No data available for PDF report.")
            return False

        doc = SimpleDocTemplate(filename, pagesize=landscape(letter))
        styles = getSampleStyleSheet()
        elements = [Paragraph("Expense Report", styles["Title"]), Spacer(1, 12)]

        if filters:
            filter_text = "Filters Applied: " + ", ".join(f"{k}: {v}" for k, v in filters.items())
            elements.append(Paragraph(filter_text, styles["Normal"]))
            elements.append(Spacer(1, 12))

        data.insert(0, "S.No", range(1, len(data) + 1))
        data["amount"] = data["amount"].apply(lambda x: f"₹{x:,.2f}")

        table_data = [data.columns.tolist()] + data.values.tolist()
        table = Table(table_data)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#ECF0F1")),
            ("GRID", (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))

        pie_chart = save_expense_chart(data, filename)
        bar_chart = save_expense_bar_chart(data, filename)

        if pie_chart:
            elements.append(Image(pie_chart, width=300, height=300))
            elements.append(Spacer(1, 20))
        if bar_chart:
            elements.append(Image(bar_chart, width=400, height=250))

        doc.build(elements)
        return True
    except Exception as e:
        print("PDF generation error:", e)
        return False


# -------- HTML Report Generation -------- #

def generate_html_report(data: pd.DataFrame, filters: Optional[Dict] = None) -> str:
    """
    Generates an HTML report with an expense table and visual graphs.
    """
    data = clean_dataframe(parse_dates(data, "date"))

    if data.empty:
        return "<h2>No data available for the report.</h2>"

    data["amount"] = data["amount"].apply(lambda x: f"₹{x:,.2f}")
    html_table = data.to_html(classes="table table-striped", index=False)

    pie_chart = save_expense_chart(data, "html_report")
    bar_chart = save_expense_bar_chart(data, "html_report")

    html_doc = f"""
    <html>
        <head>
            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css">
            <title>Expense Report</title>
        </head>
        <body>
            <div class="container">
            <h1 class="text-center">Expense Report</h1>
            <div class="text-center">
                <img src="{pie_chart}" width="300">
                <img src="{bar_chart}" width="400">
            </div>
            {html_table}
            </div>
        </body>
    </html>
    """
    return html_doc
