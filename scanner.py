#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
云端 A 股扫描脚本 - yfinance 版本
GitHub Actions 自动运行
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import time
import os
import warnings

warnings.filterwarnings('ignore')

# =================配置=================
OUTPUT_DIR = 'data'
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'signals.csv')
SCAN_LIMIT = 100
TURTLE_LOOKBACK = 20
ATR_PERIOD = 14

# =================A 股代码列表=================
A_STOCKS = [
    {'code': '600519', 'name': '贵州茅台', 'sector': '白酒'},
    {'code': '600036', 'name': '招商银行', 'sector': '银行'},
    {'code': '601398', 'name': '工商银行', 'sector': '银行'},
    {'code': '601857', 'name': '中国石油', 'sector': '石油'},
    {'code': '600028', 'name': '中国石化', 'sector': '石油'},
    {'code': '000001', 'name': '平安银行', 'sector': '银行'},
    {'code': '000002', 'name': '万科 A', 'sector': '房地产'},
    {'code': '000858', 'name': '五粮液', 'sector': '白酒'},
    {'code': '000651', 'name': '格力电器', 'sector': '家电'},
    {'code': '000333', 'name': '美的集团', 'sector': '家电'},
    {'code': '002415', 'name': '海康威视', 'sector': '科技'},
    {'code': '000725', 'name': '京东方 A', 'sector': '科技'},
    {'code': '002594', 'name': '比亚迪', 'sector': '汽车'},
    {'code': '600887', 'name': '伊利股份', 'sector': '食品'},
    {'code': '600104', 'name': '上汽集团', 'sector': '汽车'},
    {'code': '600276', 'name': '恒瑞医药', 'sector': '医药'},
    {'code': '601318', 'name': '中国平安', 'sector': '保险'},
    {'code': '601628', 'name': '中国人寿', 'sector': '保险'},
    {'code': '600000', 'name': '浦发银行', 'sector': '银行'},
    {'code': '601288', 'name': '农业银行', 'sector': '银行'},
    {'code': '601988', 'name': '中国银行', 'sector': '银行'},
    {'code': '601668', 'name': '中国建筑', 'sector': '建筑'},
    {'code': '600019', 'name': '宝钢股份', 'sector': '钢铁'},
    {'code': '600030', 'name': '中信证券', 'sector': '证券'},
    {'code': '600031', 'name': '三一重工', 'sector': '机械'},
    {'code': '600036', 'name': '招商银行', 'sector': '银行'},
    {'code': '600048', 'name': '保利发展', 'sector': '房地产'},
    {'code': '600050', 'name': '中国联通', 'sector': '通信'},
    {'code': '600104', 'name': '上汽集团', 'sector': '汽车'},
    {'code': '600111', 'name': '北方稀土', 'sector': '资源'},
    {'code': '000100', 'name': 'TCL 科技', 'sector': '科技'},
    {'code': '000157', 'name': '中联重科', 'sector': '机械'},
    {'code': '000333', 'name': '美的集团', 'sector': '家电'},
    {'code': '000425', 'name': '徐工机械', 'sector': '机械'},
    {'code': '000538', 'name': '云南白药', 'sector': '医药'},
    {'code': '000568', 'name': '泸州老窖', 'sector': '白酒'},
    {'code': '000625', 'name': '长安汽车', 'sector': '汽车'},
    {'code': '000776', 'name': '广发证券', 'sector': '证券'},
    {'code': '000858', 'name': '五粮液', 'sector': '白酒'},
    {'code': '000895', 'name': '双汇发展', 'sector': '食品'},
    {'code': '002001', 'name': '新和成', 'sector': '化工'},
    {'code': '002007', 'name': '华兰生物', 'sector': '医药'},
    {'code': '002027', 'name': '分众传媒', 'sector': '传媒'},
    {'code': '002049', 'name': '紫光国微', 'sector': '科技'},
    {'code': '002142', 'name': '宁波银行', 'sector': '银行'},
    {'code': '002230', 'name': '科大讯飞', 'sector': '科技'},
    {'code': '002236', 'name': '大华股份', 'sector': '科技'},
    {'code': '002304', 'name': '洋河股份', 'sector': '白酒'},
    {'code': '002415', 'name': '海康威视', 'sector': '科技'},
    {'code': '002594', 'name': '比亚迪', 'sector': '汽车'},
]

def extend_stock_list(target_count):
    """自动补充股票代码"""
    base_codes = [
        '600000', '600004', '600006', '600007', '600008', '600009', '600010', '600011',
        '600015', '600016', '600018', '600019', '600020', '600021', '600022', '600023',
        '600025', '600026', '600027', '600028', '600029', '600030', '600031', '600033',
        '600035', '600036', '600037', '600038', '600039', '600048', '600050', '600053',
        '600054', '600056', '600060', '600061', '600062', '600064', '600066', '600067',
        '600068', '600079', '600085', '600087', '600088', '600089', '600096', '600098',
        '600100', '600104', '600108', '600109', '600110', '600111', '600115', '600118',
        '000001', '000002', '000027', '000028', '000039', '000060', '000063', '000069',
        '000089', '000100', '000157', '000333', '000425', '000538', '000568', '000625',
        '000651', '000725', '000776', '000783', '000858', '000895', '000938', '000963',
        '001979', '002001', '002007', '002027', '002049', '002142', '002230', '002236',
        '002304', '002415', '002594', '002714', '003816'
    ]
    
    result = A_STOCKS.copy()
    existing_codes = {s['code'] for s in result}
    
    for code in base_codes:
        if len(result) >= target_count:
            break
        if code not in existing_codes:
            result.append({
                'code': code,
                'name': f'股票{code}',
                'sector': '其他'
            })
            existing_codes.add(code)
    
    return result[:target_count]

# =================数据获取=================

def get_yfinance_code(code):
    """转换 A 股代码为 yfinance 格式"""
    code = str(code).zfill(6)
    if code.startswith('6'):
        return f"{code}.SS"
    else:
        return f"{code}.SZ"

def get_stock_history(code, days=90):
    """获取个股历史数据"""
    try:
        yf_code = get_yfinance_code(code)
        ticker = yf.Ticker(yf_code)
        df = ticker.history(period=f"{days}d")
        
        if df is None or len(df) < 30:
            return None
        
        df = df.reset_index()
        df = df.rename(columns={
            'Date': 'date',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })
        
        if 'volume' not in df.columns:
            df['volume'] = 0
        
        return df
    except:
        return None

# =================策略逻辑=================

def get_market_prior():
    """计算市场先验概率"""
    try:
        ticker = yf.Ticker("000001.SS")
        df = ticker.history(period="1y")
        
        if len(df) < 60:
            return 0.5
        
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        ma60 = df['Close'].rolling(60).mean().iloc[-1]
        current_price = df['Close'].iloc[-1]
        
        if current_price > ma20 and ma20 > ma60:
            return 0.75
        elif current_price > ma60:
            return 0.60
        else:
            return 0.40
    except:
        return 0.50

def calculate_likelihood(df):
    """计算个股突破似然度"""
    if len(df) < TURTLE_LOOKBACK + 5:
        return 0.0
    
    high_20 = df['high'].rolling(TURTLE_LOOKBACK).max().iloc[-2]
    current_close = df['close'].iloc[-1]
    current_vol = df['volume'].iloc[-1]
    avg_vol_20 = df['volume'].rolling(20).mean().iloc[-1]
    
    if avg_vol_20 == 0 or high_20 == 0:
        return 0.0
    
    is_breakout = current_close > high_20
    if not is_breakout:
        return 0.0
    
    breakout_strength = (current_close - high_20) / high_20
    volume_ratio = current_vol / (avg_vol_20 + 1e-6)
    
    strength_score = min(breakout_strength * 100, 1.0)
    volume_score = min((volume_ratio - 1) / 2, 1.0) if volume_ratio > 1 else 0.0
    
    likelihood = 0.6 * strength_score + 0.4 * volume_score
    return likelihood

def analyze_stock(code, name, sector):
    """分析单只股票"""
    df = get_stock_history(code)
    if df is None:
        return None
    
    prior = get_market_prior()
    likelihood = calculate_likelihood(df)
    
    if likelihood == 0:
        return None
    
    score = prior * likelihood
    
    df['tr'] = np.maximum(df['high']-df['low'], 
                          np.maximum(abs(df['high']-df['close'].shift(1)), 
                                     abs(df['low']-df['close'].shift(1))))
    atr = df['tr'].rolling(ATR_PERIOD).mean().iloc[-1]
    
    latest_price = df['close'].iloc[-1]
    high_20 = df['high'].rolling(TURTLE_LOOKBACK).max().iloc[-2]
    
    if high_20 == 0:
        return None
    
    breakout_pct = (latest_price - high_20) / high_20 * 100
    
    return {
        '代码': code,
        '名称': name,
        '行业': sector,
        '最新价': round(latest_price, 2),
        '突破幅度 (%)': round(breakout_pct, 2),
        '贝叶斯置信分': round(score, 4),
        'ATR': round(atr, 2),
        '数据日期': datetime.now().strftime('%Y-%m-%d'),
        '扫描时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

# =================主流程=================

def run_scan():
    """执行扫描"""
    print("=" * 50)
    print("🐢 贝叶斯海龟量化选股 - 云端自动扫描")
    print("=" * 50)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    stock_pool = extend_stock_list(SCAN_LIMIT)
    print(f"✅ 准备扫描 {len(stock_pool)} 只股票")
    
    results = []
    success_count = 0
    fail_count = 0
    
    print(f"\n🔍 开始扫描...\n")
    
    for i, stock in enumerate(stock_pool):
        code = stock['code']
        name = stock['name']
        sector = stock['sector']
        
        if (i + 1) % 20 == 0:
            print(f"📈 进度：{i+1}/{len(stock_pool)} - 信号：{success_count}")
        
        res = analyze_stock(code, name, sector)
        if res:
            results.append(res)
            success_count += 1
        else:
            fail_count += 1
        
        time.sleep(0.3)
    
    if results:
        df_result = pd.DataFrame(results)
        df_result = df_result.sort_values('贝叶斯置信分', ascending=False)
        df_result.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
        
        print("\n" + "=" * 50)
        print(f"✅ 扫描完成！")
        print(f"📊 成功：{success_count} | 失败：{fail_count}")
        print(f"🎯 发现 {len(results)} 个买入信号")
        print(f"💾 结果已保存至：{OUTPUT_FILE}")
        print("=" * 50)
        
        print("\n🏆 Top 5 买入信号：")
        print(df_result.head(5)[['代码', '名称', '行业', '贝叶斯置信分', '突破幅度 (%)']].to_string(index=False))
        
        return True
    else:
        print("\n❌ 未发现符合策略的信号")
        pd.DataFrame().to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
        return False

if __name__ == "__main__":
    run_scan()