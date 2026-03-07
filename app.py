import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime, timedelta
import json
import os

st.set_page_config(page_title="贝叶斯海龟量化选股平台", page_icon="🐢", layout="wide")
st.title("🐢 贝叶斯海龟量化选股平台")
st.markdown("**🌏 新加坡云端版 | 6 因子策略 | 自动每周一更新**")

DATA_FILE = 'data/signals.csv'
PERFORMANCE_FILE = 'data/performance.json'

@st.cache_data(ttl=3600)
def load_signals():
    try:
        df = pd.read_csv(DATA_FILE, encoding='utf-8-sig')
        return df
    except:
        return None

def load_performance():
    try:
        with open(PERFORMANCE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {'weeks': []}

st.sidebar.header("📊 信息面板")

try:
    df = load_signals()
    if df is not None and not df.empty:
        if '扫描时间' in df.columns:
            last_update = df['扫描时间'].iloc[0]
            st.sidebar.info(f"🕐 最后更新：{last_update}")
        st.sidebar.success(f"📊 共 {len(df)} 个信号")
        df = df.sort_values('贝叶斯置信分', ascending=False)
        st.subheader("🏆 本周最高买入信号 Top 5")
        st.dataframe(df.head(5)[['代码', '名称', '行业', '最新价', '突破幅度 (%)', '贝叶斯置信分']], use_container_width=True, hide_index=True)
        with st.expander("📋 查看所有信号"):
            st.dataframe(df, use_container_width=True)
        st.subheader("📊 行业信号分布")
        st.bar_chart(df['行业'].value_counts().head(10))
    else:
        st.warning("⚠️ 数据文件为空，等待首次扫描完成")
except Exception as e:
    st.error(f"❌ 加载数据失败：{e}")

# 盈亏曲线
st.subheader("📈 策略盈亏曲线跟踪")
perf_data = load_performance()
if perf_data['weeks']:
    all_returns = []
    dates = []
    for week in perf_data['weeks']:
        week_date = datetime.strptime(week['date'], '%Y-%m-%d')
        week_return = 0
        count = 0
        for stock in week['stocks']:
            try:
                code = stock['code']
                entry_price = stock['entry_price']
                yf_code = f"{code}.SS" if code.startswith('6') else f"{code}.SZ"
                ticker = yf.Ticker(yf_code)
                hist = ticker.history(start=week['date'], period="5d")
                if len(hist) > 1:
                    exit_price = hist['Close'].iloc[-1]
                    ret = (exit_price - entry_price) / entry_price * 100
                    week_return += ret
                    count += 1
            except:
                pass
        if count > 0:
            week_return /= count
            all_returns.append(week_return)
            dates.append(week_date)
    if all_returns:
        cumulative_return = [(1 + r/100) for r in all_returns]
        for i in range(1, len(cumulative_return)):
            cumulative_return[i] *= cumulative_return[i-1]
        cumulative_return = [(r - 1) * 100 for r in cumulative_return]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=cumulative_return, mode='lines+markers', name='策略收益', line=dict(color='green', width=3)))
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        fig.update_layout(title="📊 策略累计收益曲线", xaxis_title="日期", yaxis_title="累计收益 (%)", template='plotly_white', height=400)
        st.plotly_chart(fig, use_container_width=True)
        st.info(f"📊 共跟踪 {len(perf_data['weeks'])} 周，最新周收益：{all_returns[-1]:.2f}%")
    else:
        st.info("⏳ 数据不足，需要更多周的扫描数据来生成盈亏曲线")
else:
    st.info("⏳ 等待首次扫描完成，之后将开始跟踪盈亏")

st.markdown("---")
st.caption("🌏 新加坡云端版 | 6 因子策略：突破 40% + 成交 20% + 相对强度 15% + 波动率 10% + 均线 10% + 振幅 5%")