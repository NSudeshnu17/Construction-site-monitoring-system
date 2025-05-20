import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

DATA_FILE = "data/analysis_data.csv"

if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["timestamp", "label"]).to_csv(DATA_FILE, index=False)


def save_detection_data(detections):
    df = pd.read_csv(DATA_FILE)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_rows = pd.DataFrame([{"timestamp": now, "label": d} for d in detections])
    df = pd.concat([df, new_rows])
    df.to_csv(DATA_FILE, index=False)


def plot_compliance_trends():
    df = pd.read_csv(DATA_FILE)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    df["year"] = df["timestamp"].dt.isocalendar().year
    df["week_num"] = df["timestamp"].dt.isocalendar().week

    weekly = df.groupby(["year", "week_num", "label"]).size().unstack(fill_value=0)

    # Create vertical-style labels: "2025-20\n(May 13–19)"
    readable_labels = []
    for year, week in weekly.index:
        start_date = datetime.strptime(f"{year}-W{int(week):02d}-1", "%G-W%V-%u")
        end_date = start_date + pd.Timedelta(days=6)
        label = f"{year}-{week:02d}\n({start_date.strftime('%b %d')}–{end_date.strftime('%d')})"
        readable_labels.append(label)
    
    weekly.index = readable_labels

    df["month"] = df["timestamp"].dt.strftime("%Y-%m")
    monthly = df.groupby(["month", "label"]).size().unstack(fill_value=0)

    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    weekly.plot(kind="barh", ax=axes[0], title="Weekly Compliance")
    monthly.plot(kind="barh", ax=axes[1], title="Monthly Compliance")

    axes[0].set_xlabel("Detections")
    axes[1].set_xlabel("Detections")
    axes[0].set_ylabel("Week")
    axes[1].set_ylabel("Month")

    plt.tight_layout()
    return fig
