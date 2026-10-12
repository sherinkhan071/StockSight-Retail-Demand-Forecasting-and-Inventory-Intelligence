# StockSight Retail Demand and Inventory Intelligence

StockSight is a retail business intelligence and inventory decision-support project designed to help operations teams reduce wasted inventory, prevent stockouts, and improve demand planning decisions.

## Business problem

Retail teams often face three critical issues:

- Overstocking: Too much inventory sits in stores and warehouses, tying up capital and increasing carrying costs.
- Stockouts: Fast-moving products sell out before the next replenishment cycle, causing lost revenue and poor customer experience.
- Poor demand planning: The business lacks a reliable signal for weekly and monthly stock requirements, especially for seasonal and promotional demand.

This project turns raw retail data into actionable inventory decisions by combining:

- sales trend analysis
- inventory health checks
- stockout and overstock risk scoring
- replenishment planning logic
- demand forecasting for short-term planning
- executive BI views for decision makers

## Project goals

1. Measure demand and inventory risk across products, stores, and categories.
2. Identify products that are overstocked, understocked, or at risk of stockout.
3. Forecast near-term demand using recent sales patterns and seasonality.
4. Recommend reorder points and replenishment priorities.
5. Deliver business-friendly BI outputs rather than only a sales dashboard.

## Data model

The project uses these core datasets:

- products: product details, category, brand, cost, selling price, lead time
- stores: store metadata, city, regional attributes, store type
- sales: daily sales by store and product
- inventory: opening stock, received quantity, sold quantity, closing stock
- promotions: discount campaigns and promotion types

## Decision-support outputs

The analysis produces:

- stockout and overstock risk indicators
- product and store health scores
- replenishment priority rankings
- forecasted demand for the next planning cycle
- recommended safety stock and reorder point logic

## Repository structure

- python/ – data cleaning, forecasting, and analysis scripts
- data/ – generated retail dataset
- sql/ – schema and analytical queries
- reports/ – business report and recommendation summaries
- powerbi/ – dashboard design and business intelligence documentation

## Recommended workflow

1. Clean and validate the retail data.
2. Calculate inventory-service metrics.
3. Detect overstock and understock segments.
4. Forecast short-term demand.
5. Prioritize replenishment by business risk.
6. Visualize the final insights in Power BI or similar BI tooling.

## How to run the project

From the project root:

```bash
python3 python/data_cleaning.py
python3 python/eda.py
python3 python/demand_forecasting.py
```

The scripts read the CSV data in the data folder and generate operational insights for inventory decision-making.

## Business value

This project helps retail operations improve:

- working capital efficiency
- sell-through performance
- customer service levels
- supplier planning and replenishment timing
- category-level stocking decisions

---

This is a decision-support project for retail inventory management, not just a sales summary.

## Live Tableau Dashboard

Explore the interactive StockSight dashboard on Tableau Public:

[Open StockSight Dashboard](https://public.tableau.com/app/profile/sherin.khan/viz/StockSightRetailDemandInventoryIntelligence/StockSightRetailDemandInventoryIntelligence?publish=yes)
