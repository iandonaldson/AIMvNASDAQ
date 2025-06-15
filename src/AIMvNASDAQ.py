import pandas as pd
import datetime
import plotly.graph_objects as go
import plotly.io as pio

# --- Paths to the uploaded files ---
nasdaq_path = "../data/NASDAQCOM.csv"
ftse_path   = "../data/FTSE Index values_12.xlsx"

# --- Read NASDAQ data (FRED CSV) ---
nasdaq_df = (
    pd.read_csv(nasdaq_path, parse_dates=["observation_date"])
      .rename(columns={"observation_date": "date", "NASDAQCOM": "nas_close"})
)
nasdaq_df["date"] = nasdaq_df["date"].dt.date
nasdaq_df["nas_close"] = pd.to_numeric(nasdaq_df["nas_close"], errors="coerce")

# --- Read FTSE AIM data (LSE Excel) ---
ftse_raw = pd.read_excel(ftse_path, sheet_name="Index Values", skiprows=16)
ftse_df = (
    ftse_raw[["Date", "FTSE AIM All-Share"]]
      .rename(columns={"Date": "date", "FTSE AIM All-Share": "ftse_aim"})
)
ftse_df["date"] = pd.to_datetime(ftse_df["date"]).dt.date

# --- Merge and align ---
combined = pd.merge(nasdaq_df, ftse_df, on="date", how="inner")

# --- Base date ---
base_date = datetime.date(1997, 10, 20)
if base_date not in combined["date"].values:
    base_date = combined.loc[combined["date"] <= base_date, "date"].max()

base_vals = combined.loc[combined["date"] == base_date].iloc[0]
base_nas, base_aim = base_vals["nas_close"], base_vals["ftse_aim"]

# --- Normalise ---
norm_df = combined[combined["date"] >= base_date].copy()
norm_df["norm_NASDAQ"]   = norm_df["nas_close"] / base_nas
norm_df["norm_FTSE_AIM"] = norm_df["ftse_aim"] / base_aim
norm_df = norm_df[["date", "norm_FTSE_AIM", "norm_NASDAQ"]]

# --- Interactive Plotly line chart ---
fig = go.Figure()
fig.add_trace(go.Scatter(x=norm_df["date"], y=norm_df["norm_FTSE_AIM"],
                         mode="lines", name="FTSE AIM All-Share (base = 1)"))
fig.add_trace(go.Scatter(x=norm_df["date"], y=norm_df["norm_NASDAQ"],
                         mode="lines", name="NASDAQ Composite (base = 1)"))
fig.update_layout(
    title="Normalised Performance: FTSE AIM vs NASDAQ (Base 20‑Oct‑1997)",
    xaxis_title="Date",
    yaxis_title="Normalised Price (20‑Oct‑1997 = 1.0)"
)

# --- Save HTML ---
html_path = "/mnt/data/FTSE_vs_NASDAQ_normalised.html"
pio.write_html(fig, file=html_path, auto_open=False)

html_path
