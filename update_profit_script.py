import pandas as pd
from datetime import datetime
from binance.client import Client
from config import BINANCE_API_KEY, BINANCE_API_SECRET, SYMBOL

client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
client.FUTURES_URL = 'https://testnet.binancefuture.com/fapi'

# Đọc dữ liệu
cols = ['timestamp', 'symbol', 'side', 'quantity', 'entry', 'tp', 'sl', 'close_price', 'profit_usdt']
df = pd.read_csv('order_history.csv', names=cols, header=0)

# Chuyển định dạng ngày
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Cập nhật các lệnh chưa có giá đóng
updated = 0
for i, row in df.iterrows():
    if pd.isna(row['close_price']) or row['close_price'] == '':
        try:
            trades = client.futures_account_trades(symbol=SYMBOL)
            for trade in reversed(trades):
                t_time = datetime.fromtimestamp(trade['time'] / 1000)
                if abs((t_time - row['timestamp']).total_seconds()) < 600:
                    close_price = float(trade['price'])
                    qty = float(row['quantity'])
                    entry = float(row['entry'])
                    profit = (close_price - entry) * qty if row['side'] == 'LONG' else (entry - close_price) * qty
                    df.at[i, 'close_price'] = round(close_price, 2)
                    df.at[i, 'profit_usdt'] = round(profit, 2)
                    updated += 1
                    break
        except Exception as e:
            print("Lỗi cập nhật:", e)

# Ghi lại dữ liệu
if updated > 0:
    df.to_csv('order_history.csv', index=False)
    print(f"✅ Đã cập nhật {updated} lệnh đã khớp TP/SL")
else:
    print("⚠️ Không có lệnh nào cần cập nhật.")
