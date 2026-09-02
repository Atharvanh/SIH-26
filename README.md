# AgriEdge

## Backend setup
1. Navigate to the `backend` directory: `cd backend`
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run the server: `python run.py`

## Frontend setup
1. Navigate to the `frontend` directory: `cd frontend`
2. Install dependencies: `npm install`
3. Run the development server: `npm run dev`

## Data Setup
Download the historical dataset from https://www.kaggle.com/datasets/anishaman07/agmarknet-india-commodity-prices-oct24-aug25 and place it at `backend/data/historical_prices.csv` before running ingestion.
