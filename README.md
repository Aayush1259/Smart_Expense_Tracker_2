# 💰 Smart Expense Tracker  
Smart Expense Tracker is a powerful and intuitive personal finance management application designed to help users track, analyze, and manage expenses efficiently. Built using Python, Tkinter, and SQLite, this tool provides interactive data visualization, automated reports, and smart financial insights. 
It includes advanced analytics, such as expense forecasting, budget recommendations, anomaly detection, and spending categorization to help users make better financial decisions. Users can also export data, generate detailed PDF/HTML reports, and automate scheduled reports via email. 
The application features a modern user interface with light/dark mode, making it user-friendly and visually appealing for seamless financial tracking. 🚀

---

## 📌 Features  

### 1️⃣ Expense Entry  
- Record expenses with **date, category, amount, and description**.
- **Auto-categorization** of expenses.
- Supports **multiple currencies** (with conversion support).  

### 2️⃣ Data Visualization & Analytics  
- **Interactive charts & graphs** for better financial insights.
- **Expense breakdown by category** (Pie Charts).
- **Daily/Weekly/Monthly spending trends** (Bar Charts & Line Graphs).
- **Budget recommendation graphs** based on spending patterns.
- **Forecast future expenses** using machine learning.  

### 3️⃣ Reports & Exports  
- **Generate detailed PDF and HTML reports** with all graphs and insights.
- **Scheduled reports via email**.
- Export expenses to **CSV or Excel** for external analysis.  

### 4️⃣ Smart Insights & Budgeting  
- **AI-powered budget recommendations**.
- **Anomaly detection** to flag unusually high expenses.
- **Spending categorization** into **Must, Need, and Want**.  

### 5️⃣ Modern & Responsive UI  
- **Toggle between Light & Dark mode** for better visibility.
- **Clean and minimalistic design** with intuitive navigation.  

---

## 🚀 Technologies Used  
- **Python**: Core logic and backend processing.  
- **Pandas**: Data handling and processing.  
- **Matplotlib & Seaborn**: Charts & data visualization.  
- **ReportLab**: PDF report generation.  
- **SQLite**: Lightweight local database storage.  
- **Tkinter**: GUI for the desktop version.  
- **Flask (Optional)**: API for web-based version.  

---

## 📊 Machine Learning Models Used
- The Smart Expense Tracker integrates machine learning for enhanced financial insights:

### 1️⃣ Expense Forecasting
- **Model Used:** Linear Regression
  
- **Purpose:** Predicts future expenses based on historical spending patterns.

### 2️⃣ Budget Recommendation
- **Model Used:** K-Means Clustering
  
- **Purpose:** Suggest a monthly budget by categorizing users into different spending behavior groups.

### 3️⃣ Anomaly Detection
- **Model Used:** Isolation Forest
  
- **Purpose:** Flags unusually high expenses compared to past spending trends.

### 4️⃣ Auto-Categorization of Expenses
- **Model Used:** Naïve Bayes Classifier

- **Purpose:** Automatically assigns a category to new expense entries based on previous data.

---
## 📂 Project Structure  

- Expense Tracker/
- ├── main.py
- ├── analytics_section.py                 
- ├── utils.py         
- ├── database.py                 
- │── report.py
- │── import_export.py       
- │── export.py
- │── receipt_capture.py
- │── ml.py
- │── requirements.txt
- │── README.md
- │── .gitignore
- │── advanced_categorization.py
- │── expense_tracker.db 

---

## 💻 Installation & Setup  

### Prerequisites  
📌 Install **Python 3.x** on your system.  
📌 Install pip (Python package manager).  

### Step 1: Clone the Repository  
```sh
git clone https://github.com/Aayush1259/Smart_Expense_Tracker_2.git
cd Smart_Expense_Tracker_2
```

### Step 2: Install Dependencies
```sh
pip install -r requirements.txt
```

### Step 3: Run the Application
```sh
python main.py
```

---

# 📊 How It Works  

## 🔹 Expense Entry & Storage  
- Users add expenses using a simple form with fields: date, amount, category, and description.
- Expenses are stored securely in an SQLite database for easy retrieval and analysis.

## 🔹 Data Analytics 
- Users can filter expense data using "From" and "To" date pickers and select analysis types like:
  - **Bar Charts:** Display expense trends over time.
  - **Pie Charts:** Show expense distribution across categories.
  - **Line Graphs:** Track cumulative spending trends.

## 🔹 Forecasting & Budgeting  
- Uses machine learning (linear regression) to forecast future expenses.
- Generates personalized budget recommendations based on spending history.

## 🔹 Anomaly Detection
- The app flags unusually high expenses by comparing new entries with historical data.
- Alerts users when spending behavior deviates significantly from normal patterns.

## 🔹 Additional Insights
- Categorizes expenses into Must, Need, and Want to help prioritize spending.
- Shows cumulative expense trends over time for better financial planning.

---

## 📌 Future Improvements  
🔹 **Google Sheets Integration** - Sync data to the cloud.  
🔹 **Mobile Version** - Develop a mobile app using Flutter or React Native.  
🔹 **Voice-Based Expense Entry** - Use AI assistants for hands-free tracking.  
🔹 **Multi-User Support** - Allow multiple accounts with authentication.  
