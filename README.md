# StockSight — Retail Demand & Inventory Intelligence Platform

A Streamlit application for retail sales analysis, inventory health, baseline demand forecasting, and an optional AI Analyst.

## Run locally on macOS

1. Open Terminal and move into this folder.
2. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Start the main dashboard (the file shown in the project screenshot):

   ```bash
   streamlit run stocksight_welcome_app.py
   ```

   To run the alternate app instead, use `streamlit run app.py`. Pick one entry point for deployment and keep the hosting command consistent.

5. Open the URL Streamlit prints, usually `http://localhost:8501`.

## AI Analyst / Ollama configuration

The AI Analyst is optional and requires a reachable Ollama service with the configured model available (default model: `llama3.2:3b`). Locally, install and start Ollama, then pull the model:

```bash
ollama pull llama3.2:3b
```

By default, StockSight calls `http://localhost:11434/api/generate`. To use another Ollama service, set `STOCKSIGHT_OLLAMA_URL` to the base URL (without `/api/generate`), for example:

```bash
export STOCKSIGHT_OLLAMA_URL="http://localhost:11434"
```

On a hosted deployment, `localhost` means the host/container itself, not your laptop. Configure a reachable, access-controlled Ollama endpoint or disable the AI Analyst. Never expose an unauthenticated Ollama service to the public internet.

## Upload files

Upload CSVs with filenames containing `sales`, `inventory` or `stock`, and optionally `products` or `stores`. The Data Guide page lists expected columns.

## Deployment notes

- Install dependencies from `requirements.txt` using the hosting platform's build process.
- Suggested Streamlit start command: `streamlit run stocksight_welcome_app.py --server.port $PORT --server.address 0.0.0.0` (adjust `$PORT` syntax for the host; Streamlit Community Cloud typically uses its configured app entry point).
- Local JSON files may not persist on ephemeral hosts or across redeployments. Use a persistent database/storage service if manually entered data must be retained.
- Do not commit credentials, `.env` files, or Streamlit secrets. Use the hosting platform's secret/environment-variable settings.
- Run the app and validate all pages against representative CSV files after deployment.

## Important limitations

- This is a starter application and has not been verified as a secured multi-user production service.
- The forecast is a baseline using recent average demand, not necessarily a trained production model.
- Gross margin, inventory turnover, and stockout rate should only be used when appropriate source data and definitions are supplied.
- Review data quality and metric definitions before making purchasing decisions.
