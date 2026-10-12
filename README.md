# StockSight — Retail Demand & Inventory Intelligence Platform

A beginner-friendly Streamlit web app starter for retail sales analysis, inventory health, and baseline demand forecasting.

## Run locally on macOS

1. Open Terminal and move into this folder.
2. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the app:

   ```bash
   streamlit run app.py
   ```

5. Open the local URL Streamlit prints (usually `http://localhost:8501`).

## Upload files

Upload CSVs with filenames containing `sales`, `inventory` or `stock`, and optionally `products` or `stores`. The Data Guide page lists expected columns.

## Important limitations

- This is a local starter application, not a secured multi-user production service.
- The forecast is a simple baseline using recent average demand, not the trained StockSight model.
- Gross margin, inventory turnover, and stockout rate are not calculated unless suitable cost/inventory data and definitions are supplied.
- Review data quality and metric definitions before making real purchasing decisions.
