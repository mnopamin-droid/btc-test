import requests
import pandas as pd
import os
from datetime import datetime

# دریافت اطلاعات از Secrets گیت‌هاب
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def send_telegram(message):
    """ارسال پیام به ربات تلگرام"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ تلگرام توکن یا چت آیدی تنظیم نشده است.")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("✅ پیام به تلگرام ارسال شد.")
            return True
        else:
            print(f"❌ خطا در ارسال به تلگرام: {response.text}")
            return False
    except Exception as e:
        print(f"❌ خطا: {e}")
        return False

def get_kucoin_1min_data():
    """دریافت داده 1 دقیقه‌ای بیت‌کوین از KuCoin"""
    try:
        url = "https://api.kucoin.com/api/v1/market/candles"
        params = {
            "symbol": "BTC-USDT",
            "type": "1min",
            "limit": 100
        }
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data['code'] == '200000':
                candles = data['data']
                prices = [float(candle[2]) for candle in candles]
                prices.reverse()
                print(f"✅ دریافت {len(prices)} کندل 1 دقیقه‌ای از KuCoin")
                print(f"💰 آخرین قیمت: ${prices[-1]:,.2f}")
                return prices
        print(f"❌ خطا از KuCoin: {response.status_code}")
        return None
    except Exception as e:
        print(f"❌ خطا در اتصال به KuCoin: {e}")
        return None

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """محاسبه MACD"""
    prices_series = pd.Series(prices)
    ema_fast = prices_series.ewm(span=fast, adjust=False).mean()
    ema_slow = prices_series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    return macd_line, signal_line

def check_cross(macd_line, signal_line):
    """تشخیص کراس مکدی"""
    if len(macd_line) < 2:
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

def main():
    print("=" * 50)
    print("🚀 ربات تست کراس مکدی بیت‌کوین (تایم‌فریم 1 دقیقه)")
    print(f"⏰ زمان اجرا: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # دریافت داده
    prices = get_kucoin_1min_data()
    if not prices:
        send_telegram("⚠️ خطا در دریافت داده از KuCoin (تست 1 دقیقه)")
        return
    
    # محاسبه MACD
    macd, signal = calculate_macd(prices)
    
    # نمایش در لاگ
    print(f"\n📊 MACD Line: {macd.iloc[-1]:.4f}")
    print(f"📊 Signal Line: {signal.iloc[-1]:.4f}")
    print(f"📊 تفاوت: {(macd.iloc[-1] - signal.iloc[-1]):.4f}")
    
    # بررسی کراس
    cross_type = check_cross(macd, signal)
    
    if cross_type:
        price = prices[-1]
        time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # ساخت پیام تلگرامی
        message = f"""<b>🔔 سیگنال جدید بیت‌کوین (تست)</b>

<b>⏱️ تایم‌فریم:</b> 1 دقیقه
<b>نوع سیگنال:</b> {cross_type}
<b>قیمت فعلی:</b> ${price:,.0f}
<b>زمان:</b> {time_str}

<b>📊 مقادیر MACD:</b>
MACD Line: {macd.iloc[-1]:.2f}
Signal Line: {signal.iloc[-1]:.2f}
<b>تفاوت:</b> {(macd.iloc[-1] - signal.iloc[-1]):.2f}

<i>#BTC #MACD #1min #Test</i>"""
        
        print(f"\n🎯 {cross_type} تشخیص داده شد!")
        print(f"📝 پیام به تلگرام ارسال می‌شود...")
        
        # ارسال به تلگرام
        send_telegram(message)
    else:
        print("\n📭 هیچ کراس مکدی تشخیص داده نشد")
        
    print("=" * 50)
    print("✅ تست کامل شد!")

if __name__ == "__main__":
    main()
