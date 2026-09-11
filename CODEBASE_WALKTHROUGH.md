# AgriEdge Codebase Walkthrough

Welcome to the AgriEdge codebase! If you're a team member preparing to explain our app's logic to judges, this document is your cheat sheet. It translates the code into plain English, explaining *why* we built things the way we did.

## 1. The Big Picture

When a farmer opens the AgriEdge app, the process follows a smooth, data-driven flow:
First, the farmer checks the **Price Intelligence** screen (`PriceIntel.jsx`). The frontend asks the backend for price forecasts (`forecast_service.py`) and a recommendation on whether to sell now or wait (`sale_window_service.py`). 
If the farmer decides to sell, they go to the **Create Lot** screen (`CreateLot.jsx`) and enter their crop details. When they hit "Find Best Buyers", the frontend creates a virtual "Lot" (a batch of produce) in the database (`lots.py` router), and then asks the matching engine (`buyer_matching_service.py`) to find the most profitable buyer. 
The backend calculates road distances (`distance_service.py`) and crunch the actual take-home pay for the farmer—factoring in transport costs, commission, and buyer reliability (`net_realization_service.py`). The farmer sees a ranked list of buyers and clicks "Accept This Offer", which instantly creates an Offer record, marks the Lot as Sold, and spins up a Logistics tracker (`offers.py` router). The farmer is then redirected to the **Order Status** screen (`OrderStatus.jsx`) to track the delivery or raise disputes, while the buyer sees the order on their read-only **Buyer Dashboard** (`BuyerDashboard.jsx`).

---

## 2. Backend Walkthrough (The "Brain")

### `forecast_service.py`
**What it solves:** Predicts what the crop price will be over the next 7 days based on recent history.
**How it works:** 
The function `generate_forecast` pulls the last 30 days of actual historical prices from our database. It calculates a simple "Moving Average" (the average price over a rolling window) to smooth out wild daily spikes. It then uses "Exponential Smoothing"—a technique that gives more weight to the most recent days' prices. Finally, it extends this smoothed trend line 7 days into the future. It's essentially saying, "Based on the momentum of the last week, where is the price drifting?"
**Simplifying Assumption:** We use simple exponential smoothing instead of a massive machine learning model (like ARIMA or Prophet) because it's blazing fast, requires no external AI APIs to run, and is perfectly sufficient for a short 7-day window.

### `sale_window_service.py`
**What it solves:** Answers the ultimate farmer question: "Should I sell today, or hold my crop for a few days?"
**How it works:** 
The `calculate_sale_window` function is the core decision engine. It takes the 7-day price forecast and looks at the *slope* (is the price generally going up or down?). 
But a rising price isn't enough! It checks `perishability_assumptions.py` to see:
1. **Can the crop survive?** (e.g., Cabbage rots fast, Wheat lasts months).
2. **What does storage cost per day?** 
It calculates the predicted profit of waiting minus the cost of storing it. If the net profit of waiting is better than selling today, it recommends "Hold". Finally, it runs a "Confidence Gate": if recent historical prices have been wildly bouncing up and down (high volatility), it lowers its confidence score, warning the farmer that the market is risky.
**Simplifying Assumption:** We assume a flat daily storage cost per quintal for each perishability tier. In reality, storage costs fluctuate based on local warehouse availability. 

### `distance_service.py`
**What it solves:** Estimates how far a farmer is from a buyer to calculate transport costs.
**How it works:**
The `estimate_road_distance_km` function takes the GPS coordinates (latitude and longitude) of the farmer and the buyer. It uses the "Haversine formula" to calculate the exact straight-line distance across the curvature of the Earth ("as the crow flies"). Because roads are rarely perfectly straight, it multiplies that straight-line distance by a "road curvature factor" (1.3x) to get a highly realistic estimate of actual driving distance.
**Simplifying Assumption:** We use a mathematical multiplier (1.3x) instead of making live calls to Google Maps API. This keeps our app free, completely offline-capable (no API timeouts), and incredibly fast.

### `net_realization_service.py`
**What it solves:** Strips away the illusion of a high price by calculating the *actual* money the farmer takes home.
**How it works:**
The `calculate_net_realization` function takes the buyer's initial offered price and starts subtracting the hidden costs.
- **Gross Revenue:** Offered Price × Quantity.
- **Transport Cost:** Distance (km) × Quantity × a flat rate (₹2.5/km/quintal).
- **Commission Cost:** A flat 2% mandi/platform fee taken from the gross.
- **Reliability Penalty:** We financially penalize buyers who pay late. If a buyer pays on time 90% of the time, they have a 10% failure rate. We multiply that failure rate by a risk factor (0.1) and subtract it from the gross.
**Concrete Worked Example (Cabbage in Aralamoodu):**
Imagine a farmer has 10 quintals of Cabbage. A buyer 20 km away offers ₹2200/quintal.
1. Gross Revenue = 10 * 2200 = ₹22,000
2. Transport Cost = 20 km * 10 qtl * ₹2.5 = -₹500
3. Commission Cost = 2% of ₹22,000 = -₹440
4. If the buyer pays on-time 80% of the time (20% failure): Penalty = 20 * 0.1 * (22,000/100) = -₹440
5. **Net Take-Home** = ₹22,000 - 500 - 440 - 440 = **₹20,620 total** (or ₹2,062 per quintal). 
Even if another buyer offered ₹2250, if they were 100km away with a terrible payment record, their Net Realization would be far lower!

### `buyer_matching_service.py`
**What it solves:** Finds the most profitable buyers for a specific lot of produce.
**How it works:**
The `match_and_rank_buyers` function first filters out bad fits. If the buyer doesn't buy Cabbage, demands Grade A when the farmer has Grade B, or wants a minimum of 50 quintals when the farmer only has 10, they are instantly dropped.
For the remaining eligible buyers, it calls the distance service and the net realization service. Finally, it sorts the buyers so the one offering the highest *Net Realization* is at the top. It also calculates a "naive comparison"—showing the farmer exactly how much money they would have lost if they had blindly sold to the buyer with the highest sticker price instead of our smart recommendation.

---

## 3. Frontend Walkthrough (The "Face")

### `PriceIntel.jsx`
When the farmer opens this screen, they select their crop and location from a dropdown. The frontend instantly fires two API calls to the backend: one for the 30-day history + 7-day forecast (`/api/forecast`), and one for the Sell vs. Hold recommendation (`/api/sale-window`).
Once the data returns, the frontend plots it on a beautiful line chart using the `recharts` library. Historical prices are drawn as a solid line, and the forecast is drawn as a dashed line. Below the chart, a color-coded recommendation card (Green for Sell, Amber for Hold) displays the backend's exact reasoning and confidence score.

### `CreateLot.jsx`
This is a two-step screen.
**Step 1:** The farmer inputs what they have (e.g., 10 quintals of Grade A Cabbage). When they click "Find Best Buyers", the frontend calls `createLot()` to register the crop in the database, generating a real tracking ID.
**Step 2:** The frontend then calls `matchBuyers()`. When the ranked list of buyers returns, it renders them as a list of cards. The top card is highlighted. The frontend displays the breakdown of transport and reliability costs so the farmer understands *why* a buyer is ranked #1. When the farmer clicks "Accept This Offer", the frontend tells the backend to create an `Offer`, update the `Lot` status, and auto-generate a `Logistics` tracker, before pushing the user to the Order Status page.

---

## 4. Judge Cross-Reference Table

| If a judge asks about... | The logic lives in... | One-sentence explanation you can give out loud |
| :--- | :--- | :--- |
| **Price Forecasting** | `forecast_service.py` | "We use an exponential smoothing algorithm over the last 30 days of data to project a 7-day trend, avoiding the overhead of heavy ML models." |
| **Sell vs. Hold Logic** | `sale_window_service.py` | "We calculate if the expected price rise outpaces the daily cost of storing that specific crop, factoring in its maximum shelf life." |
| **Confidence Scoring** | `sale_window_service.py` | "We look at the volatility—if prices have been wildly fluctuating over the last month, we lower our confidence score to warn the farmer of market risk." |
| **True Profitability** | `net_realization_service.py` | "We subtract estimated transport costs, platform commission, and a strict penalty for a buyer's late-payment history from the gross offered price." |
| **Ranking Buyers** | `buyer_matching_service.py` | "We filter buyers by crop, grade, and quantity minimums, then rank the eligible ones strictly by highest net realization, not highest sticker price." |
| **Distance Calculation** | `distance_service.py` | "We calculate the exact GPS Haversine distance and multiply it by a 1.3 road curvature factor to estimate driving distance without needing expensive Maps APIs." |
| **Transaction Lifecycle** | `offers.py` & `logistics.py` | "When an offer is accepted, the backend automatically transitions the lot to 'Sold' and spins up a tracked logistics record that moves from Requested to Delivered." |

---

## 5. Known Limitations (Honest disclaimers for judges)

We deliberately simplified certain aspects to focus on the core value proposition for the hackathon timeframe. If asked about production readiness, acknowledge these:

* **Fixed Transport Formula:** We use a flat ₹2.5 per km per quintal formula. In production, this would integrate with a live logistics bidding API or dynamic freight pricing based on current fuel costs.
* **Perishability Constraints:** Storage costs and max hold days in `perishability_assumptions.py` are static rules of thumb. In production, this would factor in local weather data and the exact type of cold-storage available to the farmer.
* **Static Buyer Profiles:** The buyers and their reliability scores (`simulated_buyers.py`) are simulated data for the demo. In production, the "on-time payment percentage" would be dynamically calculated from the buyer's actual historical transactions on our platform.
* **Absence of User Auth:** We skipped login screens and JWT tokens to focus purely on the decision-engine and data flow, using fixed IDs (e.g., `demo-farmer-1`) for the demo.
