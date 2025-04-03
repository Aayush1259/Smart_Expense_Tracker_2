"""
Advanced Categorization Module

This module provides an advanced expense categorization function that simulates
a transformer-based model using simple keyword matching. The implementation is 
modular, well-structured, and ready for future improvements (e.g., integration 
with an actual transformer model).
"""

from typing import List, Dict


# Mapping of categories to associated keywords for matching.
CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "Food": ["restaurant", "dinner", "lunch", "cafe", "meal", "snack", "food", "breakfast"],
    "Transport": ["uber", "taxi", "bus", "train", "ride", "metro", "travel", "commute"],
    "Housing": ["rent", "apartment", "housing", "mortgage", "lease", "property"],
    "Utilities": ["electricity", "water", "utility", "bill", "internet", "gas"],
    "Entertainment": ["movie", "theater", "concert", "event", "show", "entertainment"],
    "Healthcare": ["health", "clinic", "doctor", "hospital", "pharmacy", "medicine"],
    "Education": ["education", "tuition", "school", "books", "courses"],
    "Shopping": ["shopping", "clothes", "electronics", "store", "mall", "purchase"],
    "Insurance": ["insurance", "life insurance", "health insurance", "car insurance"]
}


def advanced_categorize_expense(description: str) -> str:
    if not description:
        return "Other"

    lower_desc = description.lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in lower_desc for keyword in keywords):
            return category

    # Fallback category
    return "Other"


def test_advanced_categorization() -> None:

    test_cases = [
        "Lunch at the cafe",
        "Uber ride to the airport",
        "Monthly rent for apartment",
        "Electricity bill payment",
        "Bought a new pair of shoes",
        "Visit to the doctor for a checkup",
        "Shopping at the mall",
        "Car insurance premium"
    ]

    print("Advanced Categorization Test Cases:")
    for description in test_cases:
        category = advanced_categorize_expense(description)
        print(f"Description: {description!r} -> Category: {category}")


if __name__ == "__main__":
    test_advanced_categorization()
