import pandas as pd
from datetime import datetime
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
import requests

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
    requests.post(url, data=data)

df = pd.read_csv('order_history.csv', names=[
    'timestamp', 'symbol', 'side', 'quantity', 'entry', 'tp', 'sl', 'close_price', 'profit_usdt'
])
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['date'] = df['timestamp'].dt.date

today = datetime.now().date()
daily_df = df[df['date'] == today]

total_profit = daily_df['profit_usdt'].sum()

msg = f"📊 [Báo cáo ngày {today}]\nSố lệnh: {len(daily_df)}\nTổng lời/lỗ: {round(total_profit, 2)} USDT"
send_telegram(msg)
