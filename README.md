# 📦 OpsPulse — Fulfillment Operations Control Tower

**A Python-powered fulfillment operations dashboard with automated KPI reporting, inventory monitoring, and n8n workflow integration.**

[🚀 Live Application](https://opspulse-fulfillment.streamlit.app) | [💻 GitHub Repository](https://github.com/KrishJosh130417/OpsPulse)

---

## 📌 Project Overview

OpsPulse is an end-to-end operations analytics and reporting prototype designed to simulate the daily activities of a fresh-food fulfillment business.

The application enables operations teams to monitor order fulfillment, track dispatch performance, identify delivery delays, manage inventory allocation, and generate automated performance reports.

Built using **Python, Streamlit, Pandas, n8n, Google Sheets, and Gmail**, OpsPulse combines operational data analysis with workflow automation to demonstrate how repetitive reporting processes can be streamlined.

**Note:** This is a portfolio demonstration using fictional operational data, not actual company records.

## 🎯 Business Problem

Fulfillment operations teams frequently work with multiple datasets to monitor order processing, inventory availability, delivery performance, and operational exceptions.

Manual reporting can introduce several challenges:

- Time-consuming consolidation of operational data.
- Limited visibility into pending orders and fulfillment delays.
- Difficulty identifying low-stock products across fulfillment hubs.
- Repetitive preparation and distribution of performance reports.
- Lack of centralized reporting history.

OpsPulse addresses these challenges through a unified operational dashboard and an automated reporting workflow.

## ✨ Key Features

### 1. Operations Dashboard

An interactive dashboard displaying key fulfillment performance indicators:

- Total Orders
- Dispatched / Delivered Orders
- Dispatch Rate (%)
- Pending Orders
- On-Time Delivery Rate (%)
- Delivered Order Value (₹)
- Low-Stock / Stockout Alerts

Includes visualizations for daily order volumes and order status distribution.

Users can filter operational data by fulfillment hub and order date range.

### 2. Order Management

A data-entry interface for recording operational transactions.

Supported fields include:

- Order ID and Date
- Fulfillment Hub
- Product
- Quantity
- Order Status
- Promised Delivery Time
- Actual Delivery Time

Order records are maintained in a CSV-based ledger and incorporated into dashboard calculations.

### 3. Inventory Monitoring

Tracks inventory allocation and stock availability across fulfillment hubs.

**Inventory calculation:**

`Available Stock = Opening Stock + Received Stock - Allocated Stock`

The application compares available stock against predefined reorder levels to identify low-stock conditions.

This helps simulate inventory replenishment monitoring and operational exception management.

### 4. Automated KPI Reporting

OpsPulse integrates with n8n to automate the reporting process.

When a user submits a KPI report:

1. Python calculates the selected operational metrics.
2. Streamlit sends a JSON payload to an n8n production webhook.
3. n8n processes the incoming KPI data.
4. Google Sheets records the reporting summary.
5. Gmail delivers a formatted HTML performance report.

The email includes:

- Executive KPI summary
- Dispatch and on-time delivery performance bars
- Pending order and stock alerts
- Operational observations

### 5. Reporting History

Google Sheets maintains a history of submitted operational reports, including timestamps, hub selection, order counts, dispatch rates, delivery performance, revenue, and inventory alerts.

This creates a basic reporting audit trail for operational reviews.

## 🏗️ System Architecture

```text
               OPERATIONS USER
                      |
                      v
             STREAMLIT WEB APP
                      |
             PYTHON + PANDAS
                      |
          +-----------+-----------+
          |                       |
          v                       v
     CSV DATA STORAGE       KPI CALCULATIONS
     - orders.csv                 |
     - inventory.csv              |
                                  v
                         n8n WEBHOOK (POST)
                                  |
                                  v
                         GOOGLE SHEETS
                         Append KPI Record
                                  |
                                  v
                            GMAIL NODE
                                  |
                                  v
                       HTML PERFORMANCE EMAIL
```

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic and KPI calculations |
| Streamlit | Interactive web application |
| Pandas | Data processing, aggregation, and filtering |
| CSV | Prototype order and inventory storage |
| n8n Cloud | Workflow orchestration and automation |
| Webhooks / JSON | Application-to-automation integration |
| Google Sheets | Reporting history and KPI logging |
| Gmail | Automated HTML report delivery |
| GitHub | Version control and project hosting |
| Streamlit Community Cloud | Web application deployment |

## 📊 Sample Operational Metrics

The demonstration dataset includes the following example performance figures:

| KPI | Value |
|---|---:|
| Total Orders | 181 |
| Dispatched / Delivered | 161 |
| Dispatch Rate | 88.95% |
| Pending Orders | 12 |
| On-Time Delivery Rate | 43.55% |
| Delivered Order Value | ₹62,003 |
| Low-Stock Alerts | 0 |

These values are illustrative and may change as records or filters are updated.

## 📂 Project Structure

```text
OpsPulse/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
└── data/
    ├── orders.csv
    └── inventory.csv
```

**File descriptions:**

- `app.py` — Streamlit application, data-entry interfaces, KPI calculations, visualizations, and webhook integration.
- `requirements.txt` — Python package dependencies.
- `data/orders.csv` — Demonstration order records.
- `data/inventory.csv` — Demonstration inventory and allocation data.
- `.gitignore` — Excludes local development files and virtual environments.

## 🚀 Run Locally

### Prerequisites

- Python 3.11 or a compatible version
- pip
- Internet access for optional n8n integration

### 1. Clone the repository

```bash
git clone https://github.com/KrishJosh130417/OpsPulse.git
cd OpsPulse
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

### 3. Activate the environment

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 5. Launch the application

```powershell
streamlit run app.py
```

The application will normally open at:

`http://localhost:8501`

## 🔄 n8n Automation Workflow

The reporting automation consists of three connected nodes:

```text
Webhook Trigger
      |
      v
Google Sheets — Append Row
      |
      v
Gmail — Send HTML Report
```

### Webhook

- Method: `POST`
- Payload format: `JSON`
- Triggered from the Streamlit reporting interface.

### Example Payload

```json
{
  "source": "OpsPulse",
  "generated_at": "2026-11-23T00:04:52",
  "hub": "All hubs",
  "metrics": {
    "orders": 181,
    "dispatched": 161,
    "dispatch_rate": 88.95,
    "pending": 12,
    "on_time_rate": 43.55,
    "revenue": 62003
  },
  "low_stock_alerts": 0
}
```

### Google Sheets Logging

The workflow records these fields:

`generated_at`, `source`, `hub`, `orders`, `dispatched`, `dispatch_rate`, `pending`, `on_time_rate`, `revenue`, `low_stock_alerts`

### Automated Email

The Gmail node generates a visually formatted HTML report containing KPI cards, performance indicators, and operational attention areas.

The workflow has been tested with successful webhook submissions, Google Sheets entries, and email delivery.

## 🧪 Functional Testing

The prototype was tested for:

- Recording new orders in the ledger.
- Displaying operational KPIs and charts.
- Filtering data by fulfillment hub.
- Calculating available inventory and stock alerts.
- Sending JSON payloads to an n8n webhook.
- Appending KPI records to Google Sheets.
- Delivering HTML reports through Gmail.
- Deploying the application to Streamlit Community Cloud.

## ⚠️ Current Limitations

OpsPulse is a demonstration prototype rather than a production fulfillment management system.

- Operational data is fictional.
- Orders and inventory are stored in local CSV files.
- Changes made on Streamlit Community Cloud are not guaranteed to persist after restarts or redeployments.
- Concurrent data updates are not managed through a transactional database.
- The webhook integration requires a separately configured and published n8n workflow.
- Automated emails depend on valid Gmail credentials and the configured recipient.

## 🔮 Future Enhancements

- Migrate CSV storage to PostgreSQL or another persistent database.
- Add user authentication and role-based access.
- Introduce automated scheduled KPI reporting.
- Implement hub-wise performance comparisons and historical trends.
- Add inventory replenishment recommendations.
- Improve exception detection and operational alerting.
- Add automated testing and data validation.

## 💼 Skills Demonstrated

**Operations Analytics:** KPI monitoring, dispatch analysis, inventory allocation, exception tracking, and operational reporting.

**Python Development:** Data manipulation, calculations, validation, Streamlit application development, and HTTP integration.

**Workflow Automation:** n8n webhook integration, JSON transformation, Google Sheets logging, and automated Gmail reporting.

**Business Process Improvement:** Centralized reporting, reduced repetitive manual reporting steps, and improved operational visibility.

---

## 🔗 Project Links

**Live Dashboard:** https://opspulse-fulfillment.streamlit.app

**Source Code:** https://github.com/KrishJosh130417/OpsPulse

---

*OpsPulse is an independent portfolio project developed for learning and demonstrating operations analytics, Python application development, and workflow automation.*
