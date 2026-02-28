"""
Download 5paisa scrip master and create a lookup function
"""
import requests
import pandas as pd
import json

def download_scrip_master():
    """Download scrip master from 5paisa"""
    url = "https://openapi.5paisa.com/VendorsAPI/Service1.svc/ScripMaster/segment/All"
    
    print("Downloading scrip master from 5paisa...")
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        
        df.to_csv('5paisa_scrip_master.csv', index=False)
        print(f"Downloaded {len(df)} instruments")
        print(f"Saved to: 5paisa_scrip_master.csv")
        
        return df
    else:
        print(f"Failed to download: {response.status_code}")
        return None

def find_scrip_code(symbol, exchange="NSE"):
    """Find scrip code for a symbol"""
    try:
        df = pd.read_csv('5paisa_scrip_master.csv')
        
        result = df[
            (df['Name'].str.upper() == symbol.upper()) & 
            (df['Exch'] == 'N' if exchange == 'NSE' else 'B')
        ]
        
        if not result.empty:
            scrip_code = result.iloc[0]['Scripcode']
            name = result.iloc[0]['Name']
            print(f"\nSymbol: {name}")
            print(f"Exchange: {exchange}")
            print(f"Scrip Code: {scrip_code}")
            return scrip_code
        else:
            print(f"Symbol {symbol} not found on {exchange}")
            return None
    except FileNotFoundError:
        print("Scrip master not found. Downloading...")
        download_scrip_master()
        return find_scrip_code(symbol, exchange)

if __name__ == "__main__":
    df = download_scrip_master()
    
    if df is not None:
        print("\n" + "="*60)
        print("Sample scrip codes:")
        print("="*60)
        
        common_stocks = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ITC']
        
        for symbol in common_stocks:
            find_scrip_code(symbol)
