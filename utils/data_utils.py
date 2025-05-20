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
    df["week"] = df["timestamp"].dt.strftime("%Y-%U")
    df["month"] = df["timestamp"].dt.strftime("%Y-%m")

    weekly = df.groupby(["week", "label"]).size().unstack(fill_value=0)
    monthly = df.groupby(["month", "label"]).size().unstack(fill_value=0)

    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    weekly.plot(kind="bar", ax=axes[0], title="Weekly Compliance")
    monthly.plot(kind="bar", ax=axes[1], title="Monthly Compliance")
    plt.tight_layout()
    return fig
