import requests
import numpy as np
import pandas as pd
from datetime import datetime

print("=" * 50)
print("🚀 ربات تست کراس مکدی بیت‌کوین - با Binance")
print(f"⏰ زمان: {datetime.now()}")
print("=" * 50)

def get_binance_4h_data():
    """دریافت داده 4 ساعته بیت‌کوین از Binance"""
    try:
        # دریافت 100 کندل 4 ساعته از Binance
        url = "https://data.binance.com/api/v3/klines"
        params = {
            "symbol": "BTCUSDT",
            "interval": "4h",
            "limit": 100
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            prices = []
            for candle in data:
                # قیمت بسته شدن هر کندل
                close_price = float(candle[4])
                prices.append(close_price)
            
            print(f"✅ اتصال به Binance موفق!")
            print(f"📊 تعداد کندل‌های دریافت شده: {len(prices)}")
            print(f"💰 آخرین قیمت بیت‌کوین: ${prices[-1]:,.2f}")
            return prices
        else:
            print(f"❌ خطا از Binance: کد {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ خطا در اتصال به Binance: {e}")
        return None

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """محاسبه MACD"""
    prices_series = pd.Series(prices)
    
    # محاسبه EMA
    ema_fast = prices_series.ewm(span=fast, adjust=False).mean()
    ema_slow = prices_series.ewm(span=slow, adjust=False).mean()
    
    # خط MACD
    macd_line = ema_fast - ema_slow
    
    # خط سیگنال
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    
    return macd_line, signal_line

def check_cross(macd_line, signal_line):
    """تشخیص کراس مکدی"""
    if len(macd_line) < 2:
        return None, None
    
    prev_macd = macd_line.iloc[-2]
    prev_signal = signal_line.iloc[-2]
    curr_macd = macd_line.iloc[-1]
    curr_signal = signal_line.iloc[-1]
    
    # کراس صعودی (خرید)
    if prev_macd <= prev_signal and curr_macd > curr_signal:
        return "BUY 🟢", f"MACD از زیر به بالای سیگنال زد"
    
    # کراس نزولی (فروش)
    elif prev_macd >= prev_signal and curr_macd < curr_signal:
        return "SELL 🔴", f"MACD از بالا به زیر سیگنال زد"
    
    return None, None

# اجرای اصلی
prices = get_binance_4h_data()

if prices:
    print("\n📈 در حال محاسبه MACD...")
    macd, signal = calculate_macd(prices)
    
    # نمایش آخرین مقادیر
    print(f"\n📊 آخرین مقادیر:")
    print(f"   MACD Line: {macd.iloc[-1]:.4f}")
    print(f"   Signal Line: {signal.iloc[-1]:.4f}")
    print(f"   تفاوت: {(macd.iloc[-1] - signal.iloc[-1]):.4f}")
    
    # بررسی کراس
    cross_type, cross_detail = check_cross(macd, signal)
    
    print("\n" + "=" * 50)
    if cross_type:
        print(f"🎯 کراس مکدی تشخیص داده شد!")
        print(f"📢 نوع سیگنال: {cross_type}")
        print(f"📝 جزئیات: {cross_detail}")
    else:
        print(f"📭 هیچ کراس مکدی تشخیص داده نشد")
        
        # نمایش روند
        diff = macd.iloc[-1] - signal.iloc[-1]
        if diff > 0:
            print(f"📊 وضعیت فعلی: MACD بالای سیگنال (روند صعودی)")
        else:
            print(f"📊 وضعیت فعلی: MACD زیر سیگنال (روند نزولی)")
    
    print("=" * 50)
else:
    print("❌ دریافت داده با شکست مواجه شد")

print("\n✅ تست کامل شد!")
