from binance.client import Client
from binance.enums import *
from datetime import datetime
import math, csv, requests, os
from config import *

# === INIT CLIENT ===
client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
client.FUTURES_URL = 'https://testnet.binancefuture.com/fapi'

# === TELEGRAM ===
def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        requests.post(url, data=data)
    except:
        print("❌ Không gửi được Telegram")

# === CHUYỂN SANG HEDGE MODE ===
def ensure_hedge_mode():
    try:
        mode = client.futures_get_position_mode()
        if not mode['dualSidePosition']:
            client.futures_change_position_mode(dualSidePosition=True)
            print("✅ Đã bật Hedge Mode.")
        else:
            print("✅ Hedge Mode đã bật.")
    except Exception as e:
        print("❌ Lỗi Hedge Mode:", e)

# === LẤY SỐ DƯ ===
def get_balance():
    balance_data = client.futures_account_balance()
    for item in balance_data:
        if item['asset'] == 'USDT':
            return float(item['balance'])
    return 0.0

# === ROUND QUANTITY ===
def adjust_quantity(symbol, quantity):
    step_size = {
        'BTCUSDT': 0.001,
        'ETHUSDT': 0.001
    }
    step = step_size.get(symbol, 0.001)
    return math.floor(quantity / step) * step

# === GHI LỊCH SỬ LỆNH ===
def log_order(symbol, side, entry, tp, sl, quantity):
    row = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), symbol, side, quantity, round(entry, 2), round(tp, 2), round(sl, 2), '', '']
    file_exists = os.path.isfile("order_history.csv")
    with open("order_history.csv", "a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['timestamp', 'symbol', 'side', 'quantity', 'entry', 'tp', 'sl', 'close_price', 'profit_usdt'])
        writer.writerow(row)

# === KIỂM TRA ĐANG CÓ VỊ THẾ KHÔNG ===
def has_open_position(position_side):
    positions = client.futures_position_information(symbol=SYMBOL)
    for pos in positions:
        if pos['positionSide'] == position_side and float(pos['positionAmt']) != 0:
            return True
    return False

# === ĐẶT LỆNH LONG/SHORT ===
def place_order(symbol, side, quantity, entry_price):
    position_side = 'LONG' if side == SIDE_BUY else 'SHORT'

    if has_open_position(position_side):
        print(f"⚠️ Đã có lệnh {position_side}, bỏ qua!")
        return

    # TP 1.5% / SL 0.8%
    tp_price = entry_price * 1.015 if position_side == 'LONG' else entry_price * 0.985
    sl_price = entry_price * 0.992 if position_side == 'LONG' else entry_price * 1.008

    order = client.futures_create_order(
        symbol=symbol,
        side=side,
        type=FUTURE_ORDER_TYPE_MARKET,
        quantity=quantity,
        positionSide=position_side
    )

    if 'avgFillPrice' in order:
        avg_price = float(order['avgFillPrice'])
    elif 'fills' in order and len(order['fills']) > 0:
        avg_price = float(order['fills'][0]['price'])
    else:
        avg_price = entry_price

    # TP
    client.futures_create_order(
        symbol=symbol,
        side=SIDE_SELL if side == SIDE_BUY else SIDE_BUY,
        type=FUTURE_ORDER_TYPE_TAKE_PROFIT_MARKET,
        stopPrice=round(tp_price, 2),
        closePosition=True,
        positionSide=position_side
    )

    # SL
    client.futures_create_order(
        symbol=symbol,
        side=SIDE_SELL if side == SIDE_BUY else SIDE_BUY,
        type=FUTURE_ORDER_TYPE_STOP_MARKET,
        stopPrice=round(sl_price, 2),
        closePosition=True,
        positionSide=position_side
    )

    log_order(symbol, position_side, avg_price, tp_price, sl_price, quantity)

    print(f"✅ Đã vào lệnh {position_side} | Giá: {avg_price:.2f} | TP: {tp_price:.2f} | SL: {sl_price:.2f}")
    send_telegram(f"[BOT] {position_side} | Giá: {avg_price:.2f} | TP: {tp_price:.2f} | SL: {sl_price:.2f}")

# === CHẠY BOT ===
def execute_trade():
    now = datetime.now()
    if now.second != 0:
        print("🕐 Không phải đầu phút. Đợi đến đúng giây 00 mới vào lệnh test.")
        return


    ensure_hedge_mode()
    client.futures_change_leverage(symbol=SYMBOL, leverage=LEVERAGE)

    balance = get_balance()
    order_value = balance * TRADE_PERCENT * LEVERAGE

    ticker = client.futures_mark_price(symbol=SYMBOL)
    price = float(ticker['markPrice'])

    quantity = adjust_quantity(SYMBOL, order_value / price)

    print(f"\n➡️ Vào lệnh BTCUSDT @ {price:.2f} | Qty: {quantity}")

    place_order(SYMBOL, SIDE_BUY, quantity, price)   # Long
    place_order(SYMBOL, SIDE_SELL, quantity, price)  # Short

# === MAIN ===
execute_trade()
