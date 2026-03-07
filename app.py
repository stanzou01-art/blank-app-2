import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime

st.set_page_config(
    page_title="贝叶斯海龟量化选股平台",
    page_icon="🐢",
    layout="wide"
)

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
        else:
            st.sidebar.info(f"🕐 最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        st.sidebar.success(f"📊 共 {len(df)} 个信号")
        
        df = df.sort_values('贝叶斯置信分', ascending=False)
        
        st.subheader("🏆 本周最高买入信号 Top 5")
        st.dataframe(
            df.head(5)[['代码', '名称', '行业', '最新价', '突破幅度 (%)', '贝叶斯置信分']],
            use_container_width=True,
            hide_index=True
        )
        
        with st.expander("📋 查看所有信号"):
            st.dataframe(df, use_container_width=True)
        
        st.subheader("📊 行业信号分布")
        industry_count = df['行业'].value_counts().head(10)
        st.bar_chart(industry_count)
        
        st.subheader("📈 贝叶斯置信分分布")
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=df['贝叶斯置信分'],
            nbinsx=20,
            marker_color='skyblue'
        ))
        fig.update_layout(template='plotly_dark', height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("📈 Top1 股票 K 线")
        first_stock = df.iloc[0]
        code = str(first_stock['代码']).zfill(6)
        
        try:
            if code.startswith('6'):
                yf_code = f"{code}.SS"
            else:
                yf_code = f"{code}.SZ"
            
            ticker = yf.Ticker(yf_code)
            df_hist = ticker.history(period="6mo")
            
            if len(df_hist) > 0:
                fig = go.Figure()
                fig.add_trace(go.Candlestick(
                    x=df_hist.index,
                    open=df_hist['Open'],
                    high=df_hist['High'],
                    low=df_hist['Low'],
                    close=df_hist['Close'],
                    name='K 线'
                ))
                
                df_hist['high_20'] = df_hist['High'].rolling(20).max()
                fig.add_trace(go.Scatter(
                    x=df_hist.index,
                    y=df_hist['high_20'],
                    mode='lines',
                    name='20 日突破线',
                    line=dict(color='orange', width=2, dash='dash')
                ))
                
                fig.update_layout(
                    title=f"{first_stock['名称']} ({code}) - 评分：{first_stock['贝叶斯置信分']}",
                    template='plotly_dark',
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ 无法获取 K 线数据")
        except Exception as e:
            st.warning(f"⚠️ K 线图加载失败：{e}")
        
    else:
        st.warning("⚠️ 数据文件为空，等待首次扫描完成")
        
except Exception as e:
    st.error(f"❌ 加载数据失败：{e}")

st.markdown("---")
st.caption("🌏 新加坡云端版 | 数据：yfinance | 策略：海龟 + 贝叶斯 | 仅供研究参考")