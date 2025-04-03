"""
Machine Learning Module

Enhanced machine learning functions for expense forecasting, categorization,
anomaly detection, and expense comparison.
"""

from typing import Dict
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import IsolationForest
from utils import parse_dates


def format_currency(amount: float) -> str:
    return f"₹{amount:,.2f}"


def forecast_expenses(data: pd.DataFrame, periods: int = 1) -> pd.DataFrame:
    """
    Forecast future expenses using linear regression on monthly aggregated data.
    """
    if data.empty:
        raise ValueError("No data available for forecasting.")
    
    # Parse dates and aggregate monthly expense data
    data = parse_dates(data, "date")
    df = data.copy().set_index("date")
    monthly = df.resample("M").sum().reset_index()
    monthly["month_num"] = np.arange(len(monthly))
    
    # Fit linear regression model
    X = monthly[["month_num"]]
    y = monthly["amount"]
    model = LinearRegression()
    model.fit(X, y)
    
    # Generate future predictions
    future = pd.DataFrame(np.arange(len(monthly), len(monthly) + periods), columns=["month_num"])
    pred = model.predict(future)
    last_date = monthly["date"].max()
    future_dates = pd.date_range(last_date + pd.offsets.MonthBegin(1), periods=periods, freq="M")
    
    forecast_df = pd.DataFrame({"date": future_dates, "forecast": pred})
    return forecast_df


def forecast_expenses_lstm(data: pd.DataFrame, periods: int = 1) -> pd.DataFrame:
    """
    Forecast future expenses using a simple LSTM model.
    In production, further preprocessing, validation, and tuning are recommended.
    """
    if data.empty:
        raise ValueError("No data available for LSTM forecasting.")
    
    # Parse dates and aggregate monthly expense data
    data = parse_dates(data, "date")
    df = data.copy().set_index("date")
    monthly = df.resample("M").sum().reset_index()
    monthly["month_num"] = np.arange(len(monthly))
    
    # Prepare data for LSTM: reshape into 3D array [samples, time steps, features]
    X = monthly[["month_num"]].values
    y = monthly["amount"].values
    X_lstm = X.reshape((X.shape[0], 1, X.shape[1]))
    
    # Build and train a simple LSTM model
    model = Sequential()
    model.add(LSTM(50, activation='relu', input_shape=(X_lstm.shape[1], X_lstm.shape[2])))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    model.fit(X_lstm, y, epochs=200, verbose=0)
    
    # Predict future values using the LSTM model
    future_vals = np.array([[len(monthly) + i] for i in range(periods)])
    future_lstm = future_vals.reshape((periods, 1, 1))
    pred = model.predict(future_lstm)
    last_date = monthly["date"].max()
    future_dates = pd.date_range(last_date + pd.offsets.MonthBegin(1), periods=periods, freq="M")
    
    forecast_df = pd.DataFrame({"date": future_dates, "forecast": pred.flatten()})
    return forecast_df


def categorize_expense(description: str) -> str:
    """
    Categorize an expense based on its description using a Naive Bayes classifier.
    """
    texts = [
        "lunch restaurant food dinner",
        "uber taxi bus transport",
        "rent apartment housing",
        "electricity water utilities",
        "movie cinema entertainment",
        "doctor hospital healthcare",
        "books school education",
        "shopping mall clothes shopping",
        "insurance policy insurance",
        "miscellaneous"
    ]
    labels = [
        "Food", "Transport", "Housing", "Utilities", "Entertainment", 
        "Healthcare", "Education", "Shopping", "Insurance", "Other"
    ]
    vec = TfidfVectorizer()
    X_train = vec.fit_transform(texts)
    clf = MultinomialNB()
    clf.fit(X_train, labels)
    X_input = vec.transform([description])
    prediction = clf.predict(X_input)
    return prediction[0] if prediction.size > 0 else "Other"


def enhanced_categorize_expense(description: str) -> str:
    """
    Categorize an expense using advanced NLP techniques.
    Currently a placeholder that falls back to basic Naive Bayes categorization.
    """
    return categorize_expense(description)


def fraud_detection(new_amount: float, hist: pd.Series) -> bool:
    """
    Detect if a new expense is anomalous compared to historical expenses.

    If historical data is insufficient, a simple mean and standard deviation rule is applied.
    Otherwise, IsolationForest is used for anomaly detection.
    """
    if hist.empty or len(hist) < 10:
        mean, std = hist.mean(), hist.std()
        return new_amount > mean + 2 * std if std else False

    X = hist.values.reshape(-1, 1)
    iso = IsolationForest(contamination=0.05, random_state=0)
    iso.fit(X)
    return iso.predict([[new_amount]])[0] == -1


def personalized_budget_recommendation(data: pd.DataFrame) -> Dict[str, float]:
    """
    Provide a personalized monthly budget recommendation for each expense category,
    calculated as 90% of the average monthly expense for that category.
    """
    if data.empty:
        return {}
    
    data = parse_dates(data, "date")
    data.set_index("date", inplace=True)
    monthly = data.groupby("category").resample("M").sum()["amount"].reset_index()
    avg_by_cat = monthly.groupby("category")["amount"].mean().to_dict()
    recommendations = {cat: val * 0.9 for cat, val in avg_by_cat.items()}
    return recommendations


def smart_expense_insights(data: pd.DataFrame) -> str:
    """
    Generate a summary of expense insights including total expense, top spending category,
    and average monthly expense.
    """
    if data.empty:
        return "No data available."
    
    total = data["amount"].sum()
    cat_sums = data.groupby("category")["amount"].sum()
    top_cat = cat_sums.idxmax() if not cat_sums.empty else "N/A"
    
    data = parse_dates(data, "date")
    data.set_index("date", inplace=True)
    monthly = data.resample("M").sum()
    avg_monthly = monthly["amount"].mean() if not monthly.empty else 0
    
    return f"Total: {format_currency(total)}, Top: {top_cat}, Avg(Month): {format_currency(avg_monthly)}"


def spending_categories(data: pd.DataFrame) -> Dict[str, float]:
    """
    Categorize expenses into groups such as 'Must', 'Need', and 'Want' based on category mapping.
    """
    mapping = {
        "Must": ["Housing", "Utilities", "Food", "Transport"],
        "Need": ["Healthcare", "Insurance", "Education"],
        "Want": ["Entertainment", "Shopping", "Other"]
    }
    cat_dict = {"Must": 0, "Need": 0, "Want": 0}
    
    for _, row in data.iterrows():
        cat = row["category"]
        amt = row["amount"]
        if cat in mapping["Must"]:
            cat_dict["Must"] += amt
        elif cat in mapping["Need"]:
            cat_dict["Need"] += amt
        else:
            cat_dict["Want"] += amt
    return cat_dict


def balance_trend(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the cumulative expense trend over time.
    """
    data = data.sort_values("date")
    data["cumulative"] = data["amount"].cumsum()
    return data[["date", "cumulative"]]


def compare_expenses(data: pd.DataFrame) -> str:
    """
    Compare expenses between the last two months and provide percentage change and a suggestion.
    """
    if data.empty:
        return "No data available for comparison."
    
    data = parse_dates(data, "date")
    data.set_index("date", inplace=True)
    monthly = data.resample("M").sum()
    
    if len(monthly) < 2:
        return "Not enough data for comparison."
    
    current = monthly.iloc[-1]["amount"]
    previous = monthly.iloc[-2]["amount"]
    
    if previous == 0:
        return "No expenses in the previous month to compare."
    
    change = ((current - previous) / previous) * 100
    suggestion = ("Great job! Your expenses decreased." if change < 0 
                else "Your expenses increased. Consider reviewing your spending habits.")
    
    return (f"Current: {format_currency(current)}, Previous: {format_currency(previous)}, "
            f"Change: {change:.2f}%. {suggestion}")
