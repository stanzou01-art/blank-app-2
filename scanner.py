#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import time
import os
import warnings
import json

warnings.filterwarnings('ignore')

OUTPUT_DIR = 'data'
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'signals.csv')
PERFORMANCE_FILE = os.path.join(OUTPUT_DIR, 'performance.json')
SCAN_LIMIT = 1000
TURTLE_LOOKBACK = 20
ATR_PERIOD = 14

def extend_stock_list(target_count):
    base_codes = [
        '600000', '600004', '600006', '600007', '600008', '600009', '600010', '600011',
        '600015', '600016', '600018', '600019', '600020', '600021', '600022', '600023',
        '600025', '600026', '600027', '600028', '600029', '600030', '600031', '600033',
        '600035', '600036', '600037', '600038', '600039', '600048', '600050', '600053',
        '600054', '600056', '600060', '600061', '600062', '600064', '600066', '600067',
        '600068', '600079', '600085', '600087', '600088', '600089', '600096', '600098',
        '600099', '600100', '600101', '600102', '600103', '600104', '600105', '600106',
        '600107', '600108', '600109', '600110', '600111', '600112', '600113', '600114',
        '600115', '600116', '600117', '600118', '600119', '600120', '600121', '600122',
        '600123', '600125', '600126', '600127', '600128', '600129', '600130', '600131',
        '600132', '600133', '600135', '600136', '600137', '600138', '600139', '600141',
        '600143', '600145', '600146', '600148', '600149', '600150', '600151', '600152',
        '600153', '600155', '600156', '600157', '600158', '600159', '600160', '600161',
        '600162', '600163', '600165', '600166', '600167', '600168', '600169', '600170',
        '600171', '600172', '600173', '600175', '600176', '600177', '600178', '600179',
        '600180', '600182', '600183', '600184', '600185', '600186', '600187', '600188',
        '600189', '600190', '600191', '600192', '600193', '600195', '600196', '600197',
        '600198', '600199', '600200', '600201', '600202', '600203', '600206', '600207',
        '600208', '600210', '600211', '600212', '600213', '600215', '600216', '600217',
        '600218', '600219', '600220', '600221', '600222', '600223', '600225', '600226',
        '600227', '600228', '600229', '600230', '600231', '600232', '600233', '600235',
        '600236', '600237', '600238', '600239', '600240', '600241', '600242', '600243',
        '600246', '600247', '600248', '600249', '600250', '600251', '600252', '600255',
        '600256', '600257', '600258', '600259', '600260', '600261', '600262', '600263',
        '600265', '600266', '600267', '600268', '600269', '600270', '600271', '600272',
        '600273', '600275', '600276', '600277', '600278', '600279', '600280', '600281',
        '600282', '600283', '600284', '600285', '600287', '600288', '600289', '600290',
        '600291', '600292', '600293', '600295', '600297', '600298', '600299', '600300',
        '000001', '000002', '000004', '000005', '000006', '000007', '000008', '000009',
        '000010', '000011', '000012', '000014', '000016', '000019', '000020', '000021',
        '000022', '000023', '000024', '000025', '000026', '000027', '000028', '000029',
        '000030', '000031', '000032', '000034', '000035', '000036', '000037', '000039',
        '000040', '000042', '000043', '000045', '000046', '000048', '000049', '000050',
        '000055', '000056', '000058', '000059', '000060', '000061', '000062', '000063',
        '000065', '000066', '000068', '000069', '000070', '000078', '000088', '000089',
        '000090', '000096', '000099', '000100', '000150', '000151', '000153', '000155',
        '000156', '000157', '000158', '000159', '000160', '000161', '000165', '000166',
        '000301', '000333', '000338', '000400', '000401', '000402', '000403', '000404',
        '000405', '000406', '000407', '000408', '000409', '000410', '000411', '000413',
        '000415', '000416', '000417', '000418', '000419', '000420', '000421', '000422',
        '000423', '000425', '000426', '000428', '000429', '000430', '000488', '000498',
        '000501', '000502', '000503', '000504', '000505', '000506', '000507', '000509',
        '000510', '000511', '000513', '000514', '000516', '000517', '000518', '000519',
        '000520', '000521', '000523', '000524', '000525', '000526', '000527', '000528',
        '000529', '000530', '000531', '000532', '000533', '000534', '000536', '000537',
        '000538', '000539', '000540', '000541', '000543', '000544', '000545', '000546',
        '000547', '000548', '000550', '000551', '000552', '000553', '000554', '000555',
        '000557', '000558', '000559', '000560', '000561', '000562', '000563', '000564',
        '000565', '000566', '000567', '000568', '000569', '000570', '000571', '000572',
        '000573', '000576', '000581', '000582', '000584', '000585', '000586', '000587',
        '000589', '000590', '000591', '000592', '000593', '000595', '000596', '000597',
        '000598', '000599', '000600', '000601', '000602', '000603', '000605', '000606',
        '000607', '000608', '000609', '000610', '000611', '000612', '000613', '000615',
        '000616', '000617', '000619', '000620', '000622', '000623', '000625', '000626',
        '000627', '000628', '000629', '000630', '000631', '000632', '000633', '000635',
        '000636', '000637', '000638', '000639', '000650', '000651', '000652', '000655',
        '000656', '000657', '000659', '000661', '000662', '000663', '000665', '000666',
        '000667', '000668', '000669', '000670', '000671', '000672', '000673', '000676',
        '000677', '000678', '000679', '000680', '000681', '000682', '000683', '000685',
        '000686', '000687', '000688', '000690', '000691', '000692', '000695', '000697',
        '000698', '000700', '000701', '000702', '000703', '000705', '000707', '000708',
        '000709', '000710', '000711', '000712', '000713', '000715', '000716', '000717',
        '000718', '000719', '000720', '000721', '000722', '000723', '000725', '000726',
        '000727', '000728', '000729', '000731', '000732', '000733', '000735', '000736',
        '000737', '000738', '000739', '000748', '000750', '000751', '000752', '000753',
        '000755', '000756', '000758', '000759', '000760', '000761', '000762', '000766',
        '000767', '000768', '000776', '000777', '000778', '000779', '000780', '000782',
        '000783', '000785', '000786', '000788', '000789', '000790', '000791', '000792',
        '000793', '000795', '000796', '000797', '000798', '000799', '000800', '000801',
        '000802', '000803', '000806', '000807', '000808', '000809', '000810', '000811',
        '000812', '000813', '000815', '000816', '000818', '000819', '000820', '000821',
        '000822', '000823', '000825', '000826', '000827', '000828', '000829', '000830',
        '000831', '000833', '000835', '000836', '000837', '000838', '000839', '000848',
        '000850', '000851', '000852', '000856', '000858', '000859', '000860', '000861',
        '000862', '000863', '000868', '000869', '000875', '000876', '000877', '000878',
        '000880', '000881', '000882', '000883', '000885', '000886', '000887', '000888',
        '000889', '000890', '000892', '000893', '000895', '000897', '000898', '000900',
        '000901', '000902', '000903', '000905', '000906', '000908', '000909', '000910',
        '000911', '000912', '000913', '000915', '000916', '000917', '000918', '000919',
        '000920', '000921', '000922', '000923', '000925', '000926', '000927', '000928',
        '000929', '000930', '000931', '000932', '000933', '000935', '000936', '000937',
        '000938', '000939', '000948', '000949', '000950', '000951', '000952', '000953',
        '000955', '000956', '000957', '000958', '000959', '000960', '000961', '000962',
        '000963', '000965', '000966', '000967', '000968', '000969', '000970', '000971',
        '000972', '000973', '000975', '000976', '000977', '000978', '000979', '000980',
        '000981', '000982', '000983', '000985', '000987', '000988', '000989', '000990',
        '000993', '000995', '000996', '000997', '000998', '000999',
    ]
    unique_codes = list(dict.fromkeys(base_codes))
    if len(unique_codes) < target_count:
        for i in range(600000, 606000):
            code = str(i)
            if code not in unique_codes and len(unique_codes) < target_count:
                unique_codes.append(code)
        for i in range(0, 4000):
            code = str(i).zfill(6)
            if code not in unique_codes and len(unique_codes) < target_count:
                unique_codes.append(code)
    result = []
    for code in unique_codes[:target_count]:
        if code.startswith('6'):
            sector = '沪市'
        elif code.startswith('3'):
            sector = '创业板'
        elif code.startswith('0'):
            sector = '深市'
        else:
            sector = '其他'
        result.append({'code': code, 'name': f'股票{code}', 'sector': sector})
    return result

def get_yfinance_code(code):
    code = str(code).zfill(6)
    if code.startswith('6'):
        return f"{code}.SS"
    else:
        return f"{code}.SZ"

def get_stock_history(code, days=90):
    try:
        yf_code = get_yfinance_code(code)
        ticker = yf.Ticker(yf_code)
        df = ticker.history(period=f"{days}d")
        if df is None or len(df) < 30:
            return None
        df = df.reset_index()
        df = df.rename(columns={'Date': 'date', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'})
        if 'volume' not in df.columns:
            df['volume'] = 0
        return df
    except:
        return None

def get_market_prior():
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

def calculate_likelihood(df, benchmark_df=None):
    if len(df) < TURTLE_LOOKBACK + 20:
        return 0.0
    high_20 = df['high'].rolling(TURTLE_LOOKBACK).max().iloc[-2]
    current_close = df['close'].iloc[-1]
    if current_close <= high_20:
        return 0.0
    breakout_strength = (current_close - high_20) / high_20
    strength_score = min(breakout_strength * 100, 1.0)
    current_vol = df['volume'].iloc[-1]
    avg_vol_20 = df['volume'].rolling(20).mean().iloc[-1]
    if avg_vol_20 == 0:
        volume_score = 0.0
    else:
        volume_ratio = current_vol / avg_vol_20
        volume_score = min((volume_ratio - 1) / 2, 1.0) if volume_ratio > 1 else 0.0
    stock_return = (df['close'].iloc[-1] - df['close'].iloc[-20]) / df['close'].iloc[-20]
    if benchmark_df is not None and len(benchmark_df) >= 20:
        benchmark_return = (benchmark_df['close'].iloc[-1] - benchmark_df['close'].iloc[-20]) / benchmark_df['close'].iloc[-20]
        if benchmark_return != 0:
            relative_strength = stock_return / benchmark_return
            rs_score = min(max(relative_strength, 0), 1.0)
        else:
            rs_score = 0.5
    else:
        rs_score = 0.5
    if len(df) >= 30:
        vol_recent = df['close'].iloc[-10:].std()
        vol_previous = df['close'].iloc[-30:-10].std()
        if vol_previous > 0:
            vcp_ratio = vol_recent / vol_previous
            vcp_score = min(max(1.5 - vcp_ratio, 0), 1.0)
        else:
            vcp_score = 0.5
    else:
        vcp_score = 0.5
    ma5 = df['close'].rolling(5).mean().iloc[-1]
    ma10 = df['close'].rolling(10).mean().iloc[-1]
    ma20 = df['close'].rolling(20).mean().iloc[-1]
    if ma5 > ma10 > ma20:
        ma_score = 1.0
    elif ma5 > ma20 and ma10 > ma20:
        ma_score = 0.7
    elif ma5 > ma20:
        ma_score = 0.5
    else:
        ma_score = 0.3
    current_high = df['high'].iloc[-1]
    current_low = df['low'].iloc[-1]
    current_open = df['open'].iloc[-1]
    if current_open > 0:
        amplitude = (current_high - current_low) / current_open
        if 0.03 <= amplitude <= 0.08:
            amp_score = 1.0
        elif 0.02 <= amplitude < 0.03 or 0.08 < amplitude <= 0.12:
            amp_score = 0.7
        else:
            amp_score = 0.4
    else:
        amp_score = 0.5
    likelihood = (
        0.40 * strength_score +
        0.20 * volume_score +
        0.15 * rs_score +
        0.10 * vcp_score +
        0.10 * ma_score +
        0.05 * amp_score
    )
    return likelihood

def analyze_stock(code, name, sector, benchmark_df=None):
    df = get_stock_history(code)
    if df is None:
        return None
    prior = get_market_prior()
    likelihood = calculate_likelihood(df, benchmark_df)
    if likelihood == 0:
        return None
    score = prior * likelihood
    df['tr'] = np.maximum(df['high']-df['low'], np.maximum(abs(df['high']-df['close'].shift(1)), abs(df['low']-df['close'].shift(1))))
    atr = df['tr'].rolling(ATR_PERIOD).mean().iloc[-1]
    latest_price = df['close'].iloc[-1]
    high_20 = df['high'].rolling(TURTLE_LOOKBACK).max().iloc[-2]
    if high_20 == 0:
        return None
    breakout_pct = (latest_price - high_20) / high_20 * 100
    return {
        '代码': code, '名称': name, '行业': sector,
        '最新价': round(latest_price, 2), '突破幅度 (%)': round(breakout_pct, 2),
        '贝叶斯置信分': round(score, 4), 'ATR': round(atr, 2),
        '数据日期': datetime.now().strftime('%Y-%m-%d'),
        '扫描时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def load_performance():
    if os.path.exists(PERFORMANCE_FILE):
        with open(PERFORMANCE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'weeks': []}

def save_performance(perf_data):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(PERFORMANCE_FILE, 'w', encoding='utf-8') as f:
        json.dump(perf_data, f, ensure_ascii=False, indent=2)

def update_performance(signals_df):
    perf_data = load_performance()
    week_data = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'stocks': []
    }
    for _, row in signals_df.head(10).iterrows():
        week_data['stocks'].append({
            'code': row['代码'],
            'name': row['名称'],
            'entry_price': row['最新价'],
            'score': row['贝叶斯置信分']
        })
    perf_data['weeks'].append(week_data)
    save_performance(perf_data)
    print(f"✅ 已保存盈亏跟踪数据，共 {len(perf_data['weeks'])} 周")
    return perf_data

def run_scan():
    print("=" * 50)
    print("🐢 贝叶斯海龟量化选股 - 6 因子增强版")
    print("=" * 50)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("📊 获取上证指数数据...")
    benchmark_df = get_stock_history('000001')
    stock_pool = extend_stock_list(SCAN_LIMIT)
    print(f"✅ 准备扫描 {len(stock_pool)} 只股票")
    results = []
    success_count = 0
    valid_count = 0
    print(f"\n🔍 开始扫描...\n")
    start_time = time.time()
    for i, stock in enumerate(stock_pool):
        code = stock['code']
        name = stock['name']
        sector = stock['sector']
        if (i + 1) % 100 == 0:
            elapsed = time.time() - start_time
            eta = (elapsed / (i + 1)) * (len(stock_pool) - i - 1)
            print(f"📈 进度：{i+1}/{len(stock_pool)} - 信号：{success_count} - 有效：{valid_count} - 剩余：{eta/60:.1f}分钟")
        res = analyze_stock(code, name, sector, benchmark_df)
        if res:
            results.append(res)
            success_count += 1
        df_test = get_stock_history(code)
        if df_test is not None:
            valid_count += 1
        time.sleep(0.15)
    elapsed = time.time() - start_time
    if results:
        df_result = pd.DataFrame(results)
        df_result = df_result.sort_values('贝叶斯置信分', ascending=False)
        df_result.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
        print(f"✅ 已保存 {len(results)} 个信号到 {OUTPUT_FILE}")
        update_performance(df_result)
        print("\n" + "=" * 50)
        print(f"✅ 扫描完成！")
        print(f"⏱️  总耗时：{elapsed/60:.1f}分钟")
        print(f"📊 扫描总数：{len(stock_pool)}")
        print(f"📊 有效数据：{valid_count}")
        print(f"🎯 买入信号：{len(results)}")
        print(f"📈 信号率：{len(results)/valid_count*100:.2f}%")
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
