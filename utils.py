"""
utils.py

Common utility functions for data preprocessing and handling.
"""

import pandas as pd
import numpy as np
import re


def parse_dates(df: pd.DataFrame, column: str = "date") -> pd.DataFrame:
    """
    Convert a specified column of the DataFrame to datetime format.
    """
    if column not in df.columns:
        print(f"Warning: Column '{column}' not found in DataFrame.")
        return df

    def try_parse(date_str):
        if pd.isnull(date_str) or str(date_str).strip() == "":
            return pd.NaT
        if isinstance(date_str, str) and len(date_str) == 10:
            parts = date_str.split("-")
            try:
                if int(parts[0]) > 31:
                    return pd.to_datetime(date_str, format="%Y-%m-%d", errors="coerce")
                return pd.to_datetime(date_str, format="%d-%m-%Y", errors="coerce")
            except ValueError:
                return pd.to_datetime(date_str, errors="coerce")
        return pd.to_datetime(date_str, errors="coerce")

    df[column] = df[column].apply(try_parse)
    
    # Remove rows where date parsing failed
    df.dropna(subset=[column], inplace=True)

    return df


def convert_currency(value) -> str:
    """
    Convert a numeric value to Indian Rupee (₹) formatted string.
    """
    try:
        value = float(str(value).replace(",", "").strip())
        return f"₹{value:,.2f}"
    except ValueError:
        return "Invalid Amount"


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the given DataFrame by:
    - Removing fully empty rows.
    - Dropping duplicate records.
    - Filling missing numeric values with 0.
    - Stripping whitespace from string values.
    - Converting non-numeric data in numeric columns to NaN.
    """
    df = df.dropna(how="all").drop_duplicates()

    for col in df.select_dtypes(include=["number"]).columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip()

    return df


def filter_dataframe(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    Apply filters to a DataFrame based on column conditions.
    """
    for key, value in filters.items():
        if key in df.columns and value not in [None, "All", ""]:
            if df[key].dtype == object:
                df = df[df[key].str.contains(str(value), case=False, na=False)]
            else:
                df = df[df[key] == value]

    return df


def extract_numeric_value(text: str) -> float:
    """
    Extracts the first numeric value from a given text string.
    """
    match = re.search(r"\d+[\.,]?\d*", text)
    return float(match.group().replace(",", "")) if match else None
