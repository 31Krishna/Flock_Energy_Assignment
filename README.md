Urja Meter Analytics Dashboard

A data analytics and visualization project built for the Flock Energy
take-home assignment. The project extracts electricity meter data from
the Urja operations portal, calculates energy consumption from
cumulative meter readings, performs analysis, and presents the results
through an interactive Streamlit dashboard.

Project Overview

The goal of this project is to analyze electricity meter data and
provide useful operational insights such as:

Total number of meters

Total energy consumption

Consumption by installation status

Consumption by manufacturer

Consumption by phase type

Daily energy consumption trends

Voltage statistics

Faulty meter analysis

Highest and lowest consuming meters

Filtered data export

Key Finding

The kwh value returned by the energy endpoint is a cumulative meter
reading, not interval consumption.

Therefore, consumption is calculated per meter using the difference
between consecutive readings:

df = df.sort_values(["meterId", "timestamp"])
df["consumption"] = df.groupby("meterId")["kwh"].diff()

This prevents cumulative readings from being incorrectly summed and
gives the actual interval consumption.

Dataset

The extracted dataset contains:

403 meters

16,389 energy records

43,997.96 kWh total calculated consumption

The first reading for each meter has no previous reading, so its
calculated consumption is NaN. This is expected.

Dashboard

The Streamlit dashboard provides interactive filters for:

Installation status

Manufacturer

Phase type

Dashboard Sections

Overall KPIs

Meter installation status

Meters by manufacturer

Meters by phase type

Consumption analysis

Average consumption by phase

Daily energy consumption trend

Voltage analysis

Faulty meter analysis

Top 10 consuming meters

Lowest 10 consuming meters

Filtered energy and meter data

CSV download options

Project Structure

Flock_Energy_Assignment/
│
├── app/
│   ├── __init__.py
│   ├── analyze.py
│   ├── client.py
│   ├── config.py
│   ├── dashboard.py
│   ├── insights.py
│   └── main.py
│
├── data/
│   ├── energy.csv
│   ├── meter_analysis.csv
│   └── meters.csv
│
├── .env.example
├── .gitignore
├── PROTOCOL.md
├── README.md
└── requirements.txt

API / Portal Protocol

The project uses the Urja operations portal and its meter-related
endpoints.

The main requests identified during network investigation are:

POST /login
GET  /api/portal/meters/search?q=&page=1
GET  /api/portal/meters/{meter_id}/geo
GET  /api/portal/meters/{meter_id}/energy

The login establishes the authenticated session required for subsequent
portal requests. Detailed protocol and API observations are documented
in PROTOCOL.md.

Installation

Clone the repository:

git clone https://github.com/31Krishna/Flock_Energy_Assignment.git
cd Flock_Energy_Assignment

Create a virtual environment. On Windows:

python -m venv .venv
.venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Environment Variables

Create a .env file in the project root and use .env.example as the
template:

PORTAL_EMAIL=your_email
PORTAL_PASSWORD=your_password
BASE_URL=https://urja-ops.flockenergy.tech

Never commit .env to GitHub. Credentials are excluded through
.gitignore.

Run the Dashboard

From the project root:

streamlit run app/dashboard.py

Then open the local Streamlit URL, normally http://localhost:8501.

Data Extraction Workflow

Urja Portal
    ↓
Authentication
    ↓
Meter Search
    ↓
Meter Details
    ↓
Energy Data Extraction
    ↓
CSV Data Storage
    ↓
Data Cleaning & Analysis
    ↓
Streamlit Dashboard

The portal applies rate limiting, so extraction uses controlled request
pacing and retry/backoff handling for HTTP 429 responses.

Technologies Used

Python

Pandas

Streamlit

Requests

Plotly

python-dotenv

Git & GitHub

Analysis Approach

Consumption Calculation

Because kwh is cumulative, interval consumption is calculated with:

groupby("meterId")["kwh"].diff()

Daily Consumption

Daily consumption is calculated from interval consumption values
rather than summing the cumulative kwh column.

Meter-Level Analysis

Consumption is aggregated by meter and combined with meter metadata to
analyze installation status, manufacturer, phase type, faulty meters,
and high/low consuming meters.

Voltage Analysis

The voltR readings are used to calculate average, minimum, and maximum
voltage and to visualize the voltage distribution.

Key Results

The current extracted dataset and analysis produce:

Metric                                  Value

Total Meters                              403
Energy Records                         16,389
Total Consumption               43,997.96 kWh
Average Consumption / Meter        109.18 kWh

Future Improvements

Automated scheduled data extraction

Database storage instead of CSV files

Additional power-quality metrics

Consumption anomaly detection

Historical trend comparison

Automated dashboard refresh

Authentication and role-based dashboard access

Author

Krishna Tiwari

GitHub: https://github.com/31Krishna
