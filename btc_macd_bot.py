import requests
import pandas as pd
from datetime import datetime

print("=" * 50)
print("🚀 ربات تست کراس مکدی بیت‌کوین - با KuCoin (جایگزین بایننس)")
print(f"⏰ زمان: {datetime.now()}")
print("=" * 50)

def get_kucoin_4h_data():
    """دریافت داده 4 ساعته بیت‌کوین از KuCoin"""
    try:
        # آدرس API عمومی KuCoin (بدون نیاز به کلید)
        url = "https://api.kucoin.com/api/v1/market/candles"
        params = {
            "symbol": "BTC-USDT",
            "type": "4hour",
            "limit": 100
        }
        
        print("📡 در حال اتصال به KuCoin...")
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data['code'] == '200000':
                candles = data['data']
                # KuCoin: هر کندل شامل [زمان, بازشدن, بسته شدن, بالا, پایین, حجم]
                prices = [float(candle[2]) for candle in candles]  # قیمت بسته شدن
                prices.reverse()  # مرتب‌سازی از قدیم به جدید
                
                print(f"✅ اتصال موفق!")
                print(f"📊 تعداد کندل‌ها: {len(prices)}")
                print(f"💰 آخرین قیمت: ${prices[-1]:,.2f}")
                return prices
            else:
                print(f"❌ خطای KuCoin: {data['code']}")
                return None
        else:
            print(f"❌ خطا در اتصال: کد {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ خطا: {type(e).__name__} - {e}")
        return None

# محاسبه MACD و تشخیص کراس (دقیقاً مانند قبل)
def calculate_macd(prices, fast=12, slow=26, signal=9):
    try:
        prices_series = pd.Series(prices)
        ema_fast = prices_series.ewm(span=fast, adjust=False).mean()
        ema_slow = prices_series.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        return macd_line, signal_line
    except Exception as e:
        print(f"❌ خطا در محاسبه MACD: {e}")
        return None, None

def check_cross(macd_line, signal_line):
    if macd_line is None or signal_line is None or len(macd_line) < 2:
        return None
    prev_macd = macd_line.iloc[-2]
    prev_signal = signal_line.iloc[-2]
    curr_macd = macd_line.iloc[-1]
    curr_signal = signal_line.iloc[-1]
    
    if prev_macd <= prev_signal and curr_macd > curr_signal:
        return "BUY 🟢"
    elif prev_macd >= prev_signal and curr_macd < curr_signal:
        return "SELL 🔴"
    return None

# اجرای اصلی
prices = get_kucoin_4h_data()

if prices and len(prices) > 0:
    print("\n📈 در حال محاسبه MACD...")
    macd, signal = calculate_macd(prices)
    
    if macd is not None:
        print(f"\n📊 آخرین مقادیر MACD:")
        print(f"   MACD Line: {macd.iloc[-1]:.4f}")
        print(f"   Signal Line: {signal.iloc[-1]:.4f}")
        
        cross_type = check_cross(macd, signal)
        
        print("\n" + "=" * 50)
        if cross_type:
            print(f"🎯 کراس مکدی تشخیص داده شد: {cross_type}")
        else:
            print(f"📭 هیچ کراس مکدی تشخیص داده نشد")
        print("=" * 50)
    else:
        print("❌ محاسبه MACD ممکن نبود")
else:
    print("❌ داده‌ای برای تحلیل وجود ندارد")

print("\n✅ تست کامل شد!")
