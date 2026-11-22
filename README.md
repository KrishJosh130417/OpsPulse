# OpsPulse — Fulfillment Operations Control Tower

Streamlit prototype for fictional fresh-food fulfillment operations. Includes order entry, dispatch/on-time KPIs, inventory allocation and reorder alerts, CSV export, and optional n8n webhook integration.

## Run

```powershell
python -m streamlit run app.py
```

The app generates demo CSVs in `data/` on first run. Data is fictional. Do not use for real operational decisions. The app uses local CSV storage and is not multi-user safe. For a deployed production version, replace local CSV with a database or authenticated Google Sheets integration.

## n8n integration

Create an n8n Webhook node with POST method and Production URL, connect it to an email/reporting workflow, activate it, and paste the URL into the Reports & Automation screen. The webhook receives `source`, `generated_at`, `hub`, `metrics`, and `low_stock_alerts`. Do not commit webhook URLs or credentials.

## Metric definitions

- Dispatch rate = (Delivered + Dispatched) / all orders × 100
- On-time delivery rate = Delivered orders whose actual minutes <= promised minutes / delivered orders × 100
- Delivered order value = sum(quantity × unit price) for Delivered orders; illustrative, not verified revenue
- Available stock = opening + received − allocated
- Low-stock alert = available stock <= reorder level
