# 🏁 F1 Teammate Analyzer

A web-based tool that allows Formula 1 fans, analysts, and researchers to compare the performance of any F1 driver against their teammates across seasons using real race data. Built with Python, Flask, pandas, Plotly, and Bootstrap.

---

## 📌 Project Overview

In Formula 1, a driver’s best benchmark is often their teammate — someone competing with identical machinery. This project visualizes teammate comparisons over the course of a driver’s career using data analysis and interactive charts.

Key features:
- Dynamic teammate comparison summary tables
- Interactive bar charts using Plotly
- Predictive driver name search
- Custom season data integration
- Constructor and driver filters

---

## 📊 Technologies Used

- Python
- Flask (for the web app backend)
- Jupyter Notebook (for data integration)
- pandas (for data processing)
- seaborn & Plotly (for visualization)
- Bootstrap 5 (for frontend styling)

---

## 🧠 Dataset

- Base dataset: [Kaggle Formula 1 World Championship 1950–2021](https://www.kaggle.com/rohanrao/formula-1-world-championship-1950-2020)
- 2025 Season Extension: Manually scraped from [Formula1.com](https://www.formula1.com)
- Total: 13+ .csv files, including results.csv, drivers.csv, races.csv, pit_stops.csv, qualifying.csv, etc.

The dataset was cleaned and merged using a custom Jupyter Notebook. The 2025 data was manually added up to the Spanish Grand Prix.

---

## 🚀 How to Run Locally

1. Clone the repository
```bash
git clone https://github.com/your-username/f1-teammate-analyzer.git
cd f1-teammate-analyzer 
```

2. Install required packages
```bash
pip install -r requirements.txt
```

3. Place the dataset .csv files inside a folder named datasets/

4.Run the Flask app

```bash
python app.py
```

5. Open your browser and go to http://127.0.0.1:5000/
