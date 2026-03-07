import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime

st.set_page_config(page_title="贝叶斯海龟量化选股平台", page_icon="🐢", layout="wide")
st.title("🐢 贝叶斯海龟量化选股平台")
st.markdown("**🌏 新加坡云端版 | 数据：yfinance | 自动每周一更新**")

DATA_FILE = 'data/signals.csv'

@st.cache_data(ttl=3600)
def load_signals():
    try:
        df = pd.read_csv(DATA_FILE, encoding='utf-8-sig')
        return df
    except Exception as e:
        st.error(f"❌ 无法加载数据：{e}")
        return None

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
        st.info("💡 提示：GitHub Actions 会在每周一自动运行扫描，你也可以手动触发")
except Exception as e:
    st.error(f"❌ 加载数据失败：{e}")

st.markdown("---")
st.caption("🌏 新加坡云端版 | 数据：yfinance | 策略：海龟 + 贝叶斯 | 仅供研究参考")