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
        # آدرس اصلی Binance
        url = "https://api.binance.com/api/v3/klines"
        
        # پارامترهای درخواست
        params = {
            "symbol": "BTCUSDT",
            "interval": "4h",
            "limit": 100
        }
        
        # هدرهای مهم برای دور زدن محدودیت‌ها
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
        }
        
        print("📡 در حال اتصال به Binance...")
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        print(f"📊 کد وضعیت: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            prices = []
            for candle in data:
                close_price = float(candle[4])
                prices.append(close_price)
            
            print(f"✅ اتصال موفق!")
            print(f"📊 تعداد کندل‌ها: {len(prices)}")
            print(f"💰 آخرین قیمت: ${prices[-1]:,.2f}")
            print(f"🕒 زمان کندل آخر: {datetime.fromtimestamp(data[-1][6]/1000)}")
            return prices
        elif response.status_code == 403:
            print("❌ خطای دسترسی (403) - شاید نیاز به تغییر IP باشد")
            return None
        elif response.status_code == 404:
            print("❌ آدرس API اشتباه است (404)")
            return None
        else:
            print(f"❌ خطای ناشناخته: {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ خطا: زمان اتصال تمام شد")
        return None
    except Exception as e:
        print(f"❌ خطا: {type(e).__name__} - {e}")
        return None

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """محاسبه MACD با کتابخانه pandas"""
    try:
        prices_series = pd.Series(prices)
        
        # محاسبه EMA ها
        ema_fast = prices_series.ewm(span=fast, adjust=False).mean()
        ema_slow = prices_series.ewm(span=slow, adjust=False).mean()
        
        # خط MACD
        macd_line = ema_fast - ema_slow
        
        # خط سیگنال
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        
        return macd_line, signal_line
    except Exception as e:
        print(f"❌ خطا در محاسبه MACD: {e}")
        return None, None

def check_cross(macd_line, signal_line):
    """تشخیص کراس مکدی"""
    if macd_line is None or signal_line is None or len(macd_line) < 2:
        return None
    
    prev_macd = macd_line.iloc[-2]
    prev_signal = signal_line.iloc[-2]
    curr_macd = macd_line.iloc[-1]
    curr_signal = signal_line.iloc[-1]
    
    # کراس صعودی (خرید)
    if prev_macd <= prev_signal and curr_macd > curr_signal:
        return "BUY 🟢"
    
    # کراس نزولی (فروش)
    elif prev_macd >= prev_signal and curr_macd < curr_signal:
        return "SELL 🔴"
    
    return None

# اجرای اصلی
prices = get_binance_4h_data()

if prices and len(prices) > 0:
    print("\n📈 در حال محاسبه MACD...")
    macd, signal = calculate_macd(prices)
    
    if macd is not None:
        # نمایش آخرین مقادیر
        print(f"\n📊 آخرین مقادیر MACD:")
        print(f"   MACD Line: {macd.iloc[-1]:.4f}")
        print(f"   Signal Line: {signal.iloc[-1]:.4f}")
        print(f"   تفاوت: {(macd.iloc[-1] - signal.iloc[-1]):.4f}")
        
        # بررسی کراس
        cross_type = check_cross(macd, signal)
        
        print("\n" + "=" * 50)
        if cross_type:
            print(f"🎯 کراس مکدی تشخیص داده شد!")
            print(f"📢 نوع سیگنال: {cross_type}")
        else:
            print(f"📭 هیچ کراس مکدی تشخیص داده نشد")
            diff = macd.iloc[-1] - signal.iloc[-1]
            if diff > 0:
                print(f"📊 وضعیت فعلی: MACD بالای سیگنال (روند صعودی)")
            else:
                print(f"📊 وضعیت فعلی: MACD زیر سیگنال (روند نزولی)")
        print("=" * 50)
    else:
        print("❌ محاسبه MACD ممکن نبود")
else:
    print("❌ داده‌ای برای تحلیل وجود ندارد")

print("\n✅ تست کامل شد!")
