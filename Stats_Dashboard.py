import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from binance.client import Client
from config import *

st.set_page_config(page_title="Futures Trading Dashboard", layout="wide")

# Load dữ liệu
@st.cache_data
def load_data():
    df = pd.read_csv("order_history.csv")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date
    df['month'] = df['timestamp'].dt.to_period("M")
    df['profit_usdt'] = pd.to_numeric(df['profit_usdt'], errors='coerce').fillna(0.0)
    return df

@st.cache_data
def get_initial_balance():
    client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
    client.FUTURES_URL = 'https://testnet.binancefuture.com/fapi'
    balance_data = client.futures_account_balance()
    for item in balance_data:
        if item['asset'] == 'USDT':
            return float(item['balance'])
    return 0.0

df = load_data()
initial_balance = get_initial_balance()
current_balance = initial_balance + df['profit_usdt'].sum()

# Header
st.title("📈 BTC Futures Trading Dashboard")

# Đếm ngược đến lệnh tiếp theo (theo giây để test nến 1 phút)
now = datetime.now()
next_minute = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
time_left = next_minute - now

with st.expander("⏳ Đếm ngược đến thời điểm vào lệnh test (1 phút)"):
    st.metric("⏱️ Còn lại", f"{time_left.seconds} giây")
    st.info("👉 Khi còn 0 giây, bot sẽ vào lệnh (nếu bạn chạy bằng cron mỗi phút để test)")

# KPI tổng quan
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📌 Tổng lệnh", len(df))
with col2:
    st.metric("💰 Tổng lời/lỗ", f"{df['profit_usdt'].sum():.2f} USDT")
with col3:
    st.metric("📅 Ngày gần nhất", str(df['date'].max()))
with col4:
    st.metric("💼 Số dư hiện tại", f"{current_balance:.2f} USDT")

# Tabs biểu đồ
tab1, tab2 = st.tabs(["📊 Theo ngày", "📈 Theo tháng"])

with tab1:
    daily = df.groupby("date")["profit_usdt"].sum().reset_index()
    if not daily.empty:
        st.bar_chart(daily.set_index("date"))
    else:
        st.warning("⚠️ Không có dữ liệu để hiển thị biểu đồ theo ngày.")

with tab2:
    monthly = df.groupby("month")["profit_usdt"].sum().reset_index()
    if not monthly.empty:
        st.line_chart(monthly.set_index("month"))
    else:
        st.warning("⚠️ Không có dữ liệu để hiển thị biểu đồ theo tháng.")

# Bảng chi tiết
st.subheader("📋 Chi tiết giao dịch")
st.dataframe(df.sort_values("timestamp", ascending=False), use_container_width=True, height=500)

# Bộ lọc
with st.expander("🔍 Lọc theo ngày hoặc tháng"):
    selected_date = st.date_input("Chọn ngày", value=None)
    selected_month = st.selectbox("Chọn tháng", options=sorted(df['month'].unique().astype(str)), index=len(df['month'].unique()) - 1)

    if selected_date:
        filtered = df[df['date'] == selected_date]
        st.write(f"### Giao dịch ngày {selected_date} ({len(filtered)} lệnh)")
        st.dataframe(filtered, use_container_width=True)

    if selected_month:
        filtered = df[df['month'].astype(str) == selected_month]
        st.write(f"### Giao dịch tháng {selected_month} ({len(filtered)} lệnh)")
        st.dataframe(filtered, use_container_width=True)
