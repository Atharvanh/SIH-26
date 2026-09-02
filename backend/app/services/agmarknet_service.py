import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

AGMARKNET_API_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
API_KEY = os.getenv("AGMARKNET_API_KEY")

import time

def fetch_mandi_prices(state=None, commodity=None, market=None, limit=1000, offset=0):
    if not API_KEY:
        logger.error("AGMARKNET_API_KEY is not set.")
        return []

    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": limit,
        "offset": offset
    }
    
    if state:
        params["filters[state.keyword]"] = state
    if commodity:
        params["filters[commodity.keyword]"] = commodity
    if market:
        params["filters[market.keyword]"] = market

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(AGMARKNET_API_URL, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Check if response is empty
            if not response.text.strip():
                logger.warning(f"Empty response from API on attempt {attempt+1}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return []
                
            data = response.json()
            
            records = data.get("records", [])
            parsed_records = []
            
            for record in records:
                try:
                    parsed = {
                        "state": record.get("state"),
                        "district": record.get("district"),
                        "market": record.get("market"),
                        "commodity": record.get("commodity"),
                        "variety": record.get("variety"),
                        "grade": record.get("grade"),
                        "arrival_date": record.get("arrival_date"),
                        "min_price": float(record.get("min_price", 0)) if record.get("min_price") else None,
                        "max_price": float(record.get("max_price", 0)) if record.get("max_price") else None,
                        "modal_price": float(record.get("modal_price", 0)) if record.get("modal_price") else None,
                    }
                    parsed_records.append(parsed)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error parsing record: {record}. Error: {e}")
                    continue
                    
            return parsed_records
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed on attempt {attempt+1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                return []
        except ValueError as e:
            logger.error(f"Failed to parse JSON response on attempt {attempt+1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                return []
    
    return []


def fetch_all_pages(state, commodity, max_records=5000):
    all_records = []
    limit = 1000
    offset = 0
    
    while len(all_records) < max_records:
        records = fetch_mandi_prices(state=state, commodity=commodity, limit=limit, offset=offset)
        
        if not records:
            break
            
        all_records.extend(records)
        
        if len(records) < limit:
            # No more data available
            break
            
        offset += limit
        
    return all_records[:max_records]
