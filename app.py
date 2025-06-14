from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

from analysis import analyze_driver_teammates, plot_teammate_comparison_plotly_separate

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
drivers_df = pd.read_csv(os.path.join(BASE_DIR, "datasets", "drivers.csv"))
results_df = pd.read_csv(os.path.join(BASE_DIR, "datasets", "results.csv"))
races_df = pd.read_csv(os.path.join(BASE_DIR, "datasets", "races.csv"))
results_df = results_df.merge(races_df[['raceId', 'year']], on='raceId', how='left')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/autocomplete")
def autocomplete():
    query = request.args.get("q", "").lower()
    matches = drivers_df[
        drivers_df["surname"].str.lower().str.contains(query) |
        drivers_df["forename"].str.lower().str.contains(query)
    ]
    names = (matches["forename"] + " " + matches["surname"]).tolist()
    return jsonify(names)

@app.route("/analyze", methods=["POST"])
def analyze():
    driver_name = request.form.get("driverName", "")
    matched = drivers_df[
        (drivers_df["forename"] + " " + drivers_df["surname"]).str.lower() == driver_name.lower()
    ]
    if matched.empty:
        return "Driver not found", 404

    driver_id = matched.iloc[0]["driverId"]
    summary_df = analyze_driver_teammates(driver_id, results_df, drivers_df)
    summary_df = summary_df.round(2)
    summary_df = summary_df[summary_df["Races Together"] >= 6]
    summary_df = summary_df.sort_values("Races Together", ascending=False)

    driver_row = drivers_df[drivers_df["driverId"] == driver_id].iloc[0]
    driver_label = f"{driver_row['forename']} {driver_row['surname']}"

    summary_tables = {
        "Races & Wins": summary_df[[
            "Teammate Name", "Races Together", "Times Teammate Beat Driver", "% Races Teammate Beat Driver"
        ]],
        "Points": summary_df[[
            "Teammate Name", "Total Teammate Points", f"Total {driver_label} Points"
        ]],
        "Avg Position": summary_df[[
            "Teammate Name", "Avg Teammate Pos", f"Avg {driver_label} Pos"
        ]]
    }

    # Generate separate plots for each section
    plot_sections = plot_teammate_comparison_plotly_separate(driver_id, summary_df, drivers_df)

    return render_template("result.html",
                           driver_name=driver_name,
                           plot_sections=plot_sections,
                           summary_tables=summary_tables)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
