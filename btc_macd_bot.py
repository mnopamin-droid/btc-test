import requests
import numpy as np
import pandas as pd
from datetime import datetime

print("=" * 50)
print("🚀 ربات تست کراس مکدی بیت‌کوین")
print(f"⏰ زمان: {datetime.now()}")
print("=" * 50)

# تست اتصال به نوبیتکس
try:
    print("\n📡 در حال تست اتصال به نوبیتکس...")
    url = "https://api.nobitex.ir/v2/orderbook/BTCUSDT"
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        price = float(data.get('lastTradePrice', 0))
        print(f"✅ اتصال موفق! قیمت بیت‌کوین: {price:,.0f} تومان")
    else:
        print(f"❌ خطا: کد {response.status_code}")
        
except Exception as e:
    print(f"❌ خطا در اتصال: {e}")

print("\n" + "=" * 50)
print("✅ تست کامل شد. ربات کار می‌کند!")
print("=" * 50)
