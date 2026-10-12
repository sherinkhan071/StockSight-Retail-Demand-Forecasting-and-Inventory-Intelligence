# Power BI Retail Inventory Intelligence

This project is designed to support inventory decision-making through an operational BI layer, not just a report of historical sales.

## Dashboard objective

The BI layer should help teams answer questions like:

- Which products are at risk of stockout?
- Which products are overstocked and tying up capital?
- Which stores need replenishment first?
- Which categories need demand planning attention?
- How should promotion activity influence stock levels?

## Recommended Power BI pages

### 1. Executive summary

- total inventory value
- stockout rate
- overstock share
- sales vs forecast
- high-priority stores

### 2. Demand and replenishment planning

- weekly demand trend
- forecast vs actual
- replenishment gaps
- reorder point alerts
- lead-time impact by product

### 3. Inventory health

- days of supply
- fill rate risk
- stock coverage
- slow movers vs fast movers
- category-by-category inventory health

### 4. store performance and regional control

- city and region risk matrix
- store-level stockout and overstock signals
- inventory position by store type

### 5. promotion and seasonal impact

- promotional uplift
- demand lift from campaigns
- inventory pressure caused by events

## KPI definitions

- stockout rate: percentage of inventory periods with no available stock or zero closing stock
- overstock rate: percentage of SKUs with high inventory coverage versus demand
- inventory turnover: how quickly stock cycles through the business
- service level: proportion of customer demand fulfilled from available stock
- reorder point: threshold where replenishment should be triggered

## Decision-support value

This BI layer should be built for operational teams, planners, category managers, and supply chain staff. It emphasizes actions, not just reporting.

The most valuable outcome is a working system that identifies where inventory is too high, too low, or forecasted to become problematic in the next planning cycle.
