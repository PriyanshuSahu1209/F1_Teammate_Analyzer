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
            "Teammate Name",
            "Races Together",
            f"Times Teammate Beat {driver_label}",
            f"% Races Teammate Beat {driver_label}"
        ]],
        "Points": summary_df[[
            "Teammate Name",
            "Total Teammate Points",
            f"Total {driver_label} Points"
        ]],
        "Avg Position": summary_df[[
            "Teammate Name",
            "Avg Teammate Pos",
            f"Avg {driver_label} Pos"
        ]]
    }

    plot_sections = plot_teammate_comparison_plotly_separate(driver_id, summary_df, drivers_df)

    # === AI Summary Engine ===
    total_teammates = len(summary_df)
    total_races = summary_df["Races Together"].sum()
    beat_col = f"Times Teammate Beat {driver_label}"
    total_times_beaten = summary_df[beat_col].sum()
    avg_driver_pos = summary_df[f"Avg {driver_label} Pos"].mean()
    avg_teammate_pos = summary_df["Avg Teammate Pos"].mean()

    best_teammate_row = summary_df.loc[summary_df[beat_col].idxmax()]
    worst_teammate_row = summary_df.loc[summary_df[beat_col].idxmin()]

    best_teammate = best_teammate_row["Teammate Name"]
    best_beats = int(best_teammate_row[beat_col])
    best_avg = float(best_teammate_row["Avg Teammate Pos"])

    worst_teammate = worst_teammate_row["Teammate Name"]
    worst_beats = int(worst_teammate_row[beat_col])
    worst_avg = float(worst_teammate_row["Avg Teammate Pos"])

    summary_parts = []

    # === One Teammate Case ===
    if total_teammates == 1:
        summary_parts.append(
            f"{driver_label} has only raced alongside one teammate, {best_teammate}, "
            f"who beat them in {best_beats} out of {int(total_races)} races."
        )
        summary_parts.append(
            f"{driver_label} averaged a finishing position of {avg_driver_pos:.2f}, "
            f"while {best_teammate} averaged {avg_teammate_pos:.2f}."
        )

    # === Undefeated Case ===
    elif total_times_beaten == 0:
        summary_parts.append(
            f"{driver_label} was never beaten by any of their {total_teammates} teammates across {int(total_races)} races."
        )
        summary_parts.append(
            f"They averaged a finishing position of {avg_driver_pos:.2f}, "
            f"while teammates averaged {avg_teammate_pos:.2f}."
        )

    # === Always Beaten Case ===
    elif total_times_beaten == total_races:
        summary_parts.append(
            f"{driver_label} was beaten in every one of their {int(total_races)} races by their teammates."
        )
        summary_parts.append(
            f"Their average finishing position was {avg_driver_pos:.2f}, "
            f"compared to {avg_teammate_pos:.2f} for teammates."
        )

    # === Normal Case ===
    else:
        summary_parts.append(
            f"{driver_label} raced alongside {total_teammates} teammates in {int(total_races)} races, "
            f"and was beaten {int(total_times_beaten)} time{'s' if total_times_beaten != 1 else ''} overall."
        )
        summary_parts.append(
            f"Their average finishing position was {avg_driver_pos:.2f}, "
            f"while teammates averaged {avg_teammate_pos:.2f}."
        )

    # === Always include best + worst if multiple teammates ===
    if total_teammates > 1:
        if best_beats > 0:
            if best_beats == 1:
                phrasing = f"beat them once"
            elif best_beats / total_races >= 0.7:
                phrasing = f"dominated with {best_beats} wins"
            else:
                phrasing = f"beat them {best_beats} times"
        else:
            phrasing = f"never beat them"
        summary_parts.append(
            f"The strongest teammate was {best_teammate}, who {phrasing} and averaged a finish of {best_avg:.2f}."
        )

        if best_teammate != worst_teammate:
            if worst_beats == 0:
                summary_parts.append(
                    f"The weakest was {worst_teammate}, who never managed to beat {driver_label} "
                    f"and averaged {worst_avg:.2f} per race."
                )
            elif worst_beats == 1:
                summary_parts.append(
                    f"{worst_teammate} beat them just once, with an average finish of {worst_avg:.2f}."
                )
            else:
                summary_parts.append(
                    f"{worst_teammate} beat them only {worst_beats} times and averaged {worst_avg:.2f}."
                )

    summary_text = " ".join(summary_parts)


    return render_template("result.html",
                           driver_name=driver_name,
                           plot_sections=plot_sections,
                           summary_tables=summary_tables,
                           summary_text=summary_text)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
