# StockSight Retail Inventory Decision Support Report

## Executive summary

StockSight is designed to solve the operational problems that most retailers face: too much stock in some categories, too little in others, and poor visibility into the amount required for the next demand cycle. The project focuses on inventory intelligence, replenishment decisions, and demand planning rather than only tracking historical sales.

## Problem being solved

The business experiences three issues:

1. Overstocking: slow-moving products accumulate and lock up working capital.
2. Stockouts: popular products sell out before replenishment arrives, creating lost sales.
3. Poor demand planning: inventory levels do not respond well to weekly and monthly demand changes.

## What the analysis measures

The project evaluates the following decision points:

- Product-level demand intensity and sales volatility
- Inventory coverage by product and by store
- Risk of stockout based on demand versus available stock
- Risk of overstock based on coverage and low turnover
- Forecasted demand for the next 7 to 30 days
- Replenishment priority based on service risk and margin contribution

## Key decision-support logic

### 1. Stockout risk

A product is flagged as at risk when recent demand exceeds available stock or when closing stock consistently trends close to zero. This helps the planning team prioritize replenishment for popular SKUs.

### 2. Overstock risk

A product is flagged when stock coverage is unusually high relative to its historical sales rate. Overstocks lead to markdown pressure and excess carrying cost.

### 3. Demand forecasting

Demand is forecast using recent sales patterns, weekly seasonality, and category-level demand movements. This supports weekly replenishment and monthly inventory planning.

### 4. Reorder point guidance

The recommended reorder point blends:

- average daily demand
- lead time demand
- safety stock for volatility
- product criticality and store type

This creates a practical operating threshold rather than a purely theoretical inventory formula.

## Recommended BI pages

### Page 1: Executive overview

- total inventory value
- stockout rate
- overstock rate
- top risk categories
- sales vs demand forecast

### Page 2: Product health

- low-stock items
- excess-stock items
- product turnover
- demand forecast vs current stock

### Page 3: Store performance

- inventory coverage by store
- high-risk regions
- store-level stockout trends
- replenishment priority map

### Page 4: Promotion and seasonality

- promotional uplift by category
- impact on inventory pressure
- demand spikes after discount events

## Strategic recommendations

- Rebalance inventory toward high-velocity SKUs that drive revenue.
- Prioritize replenishment for products with high demand and long lead times.
- Reduce stock in low-turnover items with weak forecast confidence.
- Use safety stock for seasonal and promotional products.
- Build weekly operational reviews around stockout and overstock alerts.

## Conclusion

This project moves beyond sales reporting and answers real operating questions: what should be ordered, what should be reduced, and where risk is rising. The resulting inventory intelligence is designed to support faster and better decisions in retail operations.
