import pandas as pd

def inspect_csv(file_path):
    print(f"Inspecting file: {file_path}")
    print("-" * 50)
    
    try:
        df = pd.read_csv(file_path)
        
        print(f"TOTAL ROWS: {len(df)}")
        print("-" * 50)
        
        print("COLUMNS:")
        for col in df.columns:
            print(f"- {col}")
        print("-" * 50)
        
        print("DATA TYPES:")
        print(df.dtypes)
        print("-" * 50)
        
        print("FIRST 5 ROWS:")
        print(df.head(5).to_string())
        print("-" * 50)
        
    except Exception as e:
        print(f"Error reading CSV: {e}")

if __name__ == "__main__":
    inspect_csv("../data/historical_prices.csv")
