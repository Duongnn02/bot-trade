import streamlit as st
import pandas as pd
from datetime import datetime

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

df = load_data()

# Tính số dư ban đầu và hiện tại
initial_balance = 1000  # bạn có thể lấy giá trị này từ file hoặc config
current_balance = initial_balance + df['profit_usdt'].sum()

# Header
st.title("📈 BTC Futures Trading Dashboard")

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
        st.info("📅 Chưa có dữ liệu trong ngày để hiển thị biểu đồ.")

with tab2:
    monthly = df.groupby("month")["profit_usdt"].sum().reset_index()
    if not monthly.empty:
        st.line_chart(monthly.set_index("month"))
    else:
        st.info("🗓️ Chưa có dữ liệu theo tháng để hiển thị biểu đồ.")

# Bảng chi tiết
st.subheader("📋 Chi tiết giao dịch")
st.dataframe(df.sort_values("timestamp", ascending=False), use_container_width=True, height=500)

# Bộ lọc
with st.expander("🔍 Lọc theo ngày hoặc tháng"):
    selected_date = st.date_input("Chọn ngày", value=None)
    selected_month = st.selectbox("Chọn tháng", options=sorted(df['month'].astype(str).unique()), index=len(df['month'].unique()) - 1)

    if selected_date:
        filtered = df[df['date'] == selected_date]
        st.write(f"### Giao dịch ngày {selected_date} ({len(filtered)} lệnh)")
        st.dataframe(filtered, use_container_width=True)

    if selected_month:
        filtered = df[df['month'].astype(str) == selected_month]
        st.write(f"### Giao dịch tháng {selected_month} ({len(filtered)} lệnh)")
        st.dataframe(filtered, use_container_width=True)

# Ghi chú: Đòn bẩy đang là 100x và Stop Loss đang đặt ở mức 0.8% thay vì 1%.
