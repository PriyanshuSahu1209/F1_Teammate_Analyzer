import pandas as pd
import plotly.graph_objects as go

def analyze_driver_teammates(driver_id, results_df, drivers_df):
    driver_results = results_df[results_df['driverId'] == driver_id]
    constructor_years = driver_results[['constructorId', 'raceId']].merge(
        results_df[['raceId', 'year']], on='raceId'
    ).drop_duplicates()

    teammates_data = []
    for _, row in constructor_years.iterrows():
        year = row['year']
        constructor_id = row['constructorId']
        races_in_year = results_df[(results_df['constructorId'] == constructor_id) & (results_df['year'] == year)]
        teammates = races_in_year[races_in_year['driverId'] != driver_id]['driverId'].unique()
        for teammate_id in teammates:
            teammate_races = races_in_year[
                ((races_in_year['driverId'] == driver_id) | (races_in_year['driverId'] == teammate_id))
            ]
            race_ids = teammate_races['raceId'].unique()
            beat_count = 0
            teammate_points = 0
            driver_points = 0
            teammate_positions = []
            driver_positions = []
            for race in race_ids:
                race_data = teammate_races[teammate_races['raceId'] == race]
                if len(race_data) < 2:
                    continue
                race_data = race_data.sort_values(by='positionOrder')
                positions = race_data.set_index('driverId')['positionOrder'].to_dict()
                if teammate_id in positions and driver_id in positions:
                    if positions[teammate_id] < positions[driver_id]:
                        beat_count += 1
                    teammate_positions.append(positions[teammate_id])
                    driver_positions.append(positions[driver_id])
                points = race_data.set_index('driverId')['points'].to_dict()
                teammate_points += points.get(teammate_id, 0)
                driver_points += points.get(driver_id, 0)

            if len(driver_positions) == 0:
                continue

            forename = drivers_df.loc[drivers_df['driverId'] == teammate_id, 'forename'].values[0]
            surname = drivers_df.loc[drivers_df['driverId'] == teammate_id, 'surname'].values[0]
            name = f"{forename} {surname}"
            teammates_data.append({
                'Teammate Name': name,
                'Races Together': len(driver_positions),
                'Times Teammate Beat Driver': beat_count,
                'Total Teammate Points': teammate_points,
                f'Total Max Points': driver_points,
                'Avg Teammate Pos': round(sum(teammate_positions)/len(teammate_positions), 2),
                f'Avg Max Pos': round(sum(driver_positions)/len(driver_positions), 2),
                '% Races Teammate Beat Driver': round(100 * beat_count / len(driver_positions), 2)
            })

    df = pd.DataFrame(teammates_data)

    # Dynamic driver name column renaming
    driver_row = drivers_df[drivers_df['driverId'] == driver_id].iloc[0]
    driver_name = f"{driver_row['forename']} {driver_row['surname']}"
    df.rename(columns={
        f'Total Max Points': f'Total {driver_name} Points',
        f'Avg Max Pos': f'Avg {driver_name} Pos'
    }, inplace=True)

    df = df.groupby("Teammate Name", as_index=False).mean(numeric_only=True)
    df["Races Together"] = df["Races Together"].round().astype(int)
    df["Times Teammate Beat Driver"] = df["Times Teammate Beat Driver"].round().astype(int)
    df = df.sort_values("Races Together", ascending=False)
    return df

def plot_teammate_comparison_plotly_separate(driver_id, df, drivers_df):
    driver_row = drivers_df[drivers_df['driverId'] == driver_id].iloc[0]
    driver_name = f"{driver_row['forename']} {driver_row['surname']}"
    teammates = df["Teammate Name"]

    colors = {
        "red": "#FF3E41",
        "dark": "#343a40",
        "deep": "#DC3545"
    }

    plots = {}

    # 1. % Races Teammate Beat
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(x=teammates, y=df["% Races Teammate Beat Driver"], marker_color=colors["deep"]))
    fig1.update_layout(
        title=f"% Races Teammate Beat {driver_name}",
        height=400,
        plot_bgcolor="#fff",
        paper_bgcolor="#fff",
        margin=dict(l=40, r=30, t=50, b=40)
    )
    plots["Races & Wins"] = fig1.to_html(full_html=False)

    # 2. Avg Finishing Position
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=teammates, y=df["Avg Teammate Pos"], name="Avg Teammate Pos", marker_color=colors["deep"]))
    fig2.add_trace(go.Bar(x=teammates, y=df[f"Avg {driver_name} Pos"], name=f"Avg {driver_name} Pos", marker_color=colors["dark"]))
    fig2.update_layout(
        title="Average Finishing Position",
        barmode='group',
        height=400,
        plot_bgcolor="#fff",
        paper_bgcolor="#fff",
        margin=dict(l=40, r=30, t=50, b=40)
    )
    plots["Avg Position"] = fig2.to_html(full_html=False)

    # 3. Total Points
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=teammates, y=df["Total Teammate Points"], name="Teammate", marker_color=colors["deep"]))
    fig3.add_trace(go.Bar(x=teammates, y=df[f"Total {driver_name} Points"], name=driver_name, marker_color=colors["dark"]))
    fig3.update_layout(
        title="Total Points Comparison",
        barmode='group',
        height=400,
        plot_bgcolor="#fff",
        paper_bgcolor="#fff",
        margin=dict(l=40, r=30, t=50, b=40)
    )
    plots["Points"] = fig3.to_html(full_html=False)

    return plots
