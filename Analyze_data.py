'''import sys
import tkinter as tk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# -------------------------------------------------------------------------
# 1. 核心數據處理 (矩陣式交叉統計)
# -------------------------------------------------------------------------
try:
    df = pd.read_csv('simulated_bank_batch_flow_log.csv')
except FileNotFoundError:
    print("❌ 找不到原始資料，請確保先前生成的 'simulated_bank_batch_flow_log.csv' 在同個資料夾內。")
    sys.exit()

# 總體基本指標
total_logs = len(df)
total_branch_cycles = len(df[['Cycle_ID', 'Branch_Code']].drop_duplicates())

# 1. 篩選出所有「源頭(TX_GET_01)失敗」的紀錄
fail_logs = df[(df['Job_ID'] == 'TX_GET_01') & (df['Root_Cause_Type'] != 'Normal')]

# 2. 核心計算：利用 Pandas 的 crosstab 做出交叉矩陣 (分行 x 根因)
# 這會精準算出來：HK, NY, SG 各自在三大原因上各有幾筆
matrix_df = pd.crosstab(fail_logs['Branch_Code'], fail_logs['Root_Cause_Type'])

# 確保三個根因都有在欄位裡，避免隨機抽籤時少抽到某個導致報錯
for col in ['網路傳輸異常', '人為操作失誤', '憑證權限過期']:
    if col not in matrix_df.columns:
        matrix_df[col] = 0

# 3. 取得各分行的各項精準數據
hk_net = matrix_df.loc['HK', '網路傳輸異常']
hk_human = matrix_df.loc['HK', '人為操作失誤']
hk_auth = matrix_df.loc['HK', '憑證權限過期']

ny_net = matrix_df.loc['NY', '網路傳輸異常']
ny_human = matrix_df.loc['NY', '人為操作失誤']
ny_auth = matrix_df.loc['NY', '憑證權限過期']

sg_net = matrix_df.loc['SG', '網路傳輸異常']
sg_human = matrix_df.loc['SG', '人為操作失誤']
sg_auth = matrix_df.loc['SG', '憑證權限過期']

# 4. 計算三家分行的「各數據合計」(全行總計)
total_net = fail_logs[fail_logs['Root_Cause_Type'] == '網路傳輸異常'].shape[0]
total_human = fail_logs[fail_logs['Root_Cause_Type'] == '人為操作失誤'].shape[0]
total_auth = fail_logs[fail_logs['Root_Cause_Type'] == '憑證權限過期'].shape[0]
total_all_faults = len(fail_logs)

# 各分行受到連累的總異常數據 (包含自己源頭FAILED + 後續TIMEOUT的總量)
branch_faults = df[df['Status'].isin(['TIMEOUT', 'FAILED'])].groupby('Branch_Code').size()
hk_total_faults = branch_faults.get('HK', 0)
ny_total_faults = branch_faults.get('NY', 0)
sg_total_faults = branch_faults.get('SG', 0)

# -------------------------------------------------------------------------
# 2. 初始化 Tkinter 視窗
# -------------------------------------------------------------------------
root = tk.Tk()
root.title("🏦 全球海外分行批次作業 - 智慧維運與資安監控大屏 (SIEM Dashboard)")
root.geometry("1450x820")
root.configure(bg='#121214')

font_title = ("Microsoft JhengHei", 18, "bold")
font_metric_val = ("Helvetica", 32, "bold")
font_metric_lbl = ("Microsoft JhengHei", 11)

# -------------------------------------------------------------------------
# 3. 上方主標題
# -------------------------------------------------------------------------
header_frame = tk.Frame(root, bg='#1A1A1E', height=60)
header_frame.pack(fill='x', side='top')

title_label = tk.Label(header_frame, text="Banking Batch Operation Center", font=font_title, fg='#FFFFFF',
                       bg='#1A1A1E', anchor='w')
title_label.pack(side='left', padx=20, pady=15)

status_label = tk.Label(header_frame, text="SYSTEM STATUS: RUNNING (LIVE RISK DETECTED)",
                        font=("Helvetica", 10, "bold"), fg='#E67E22', bg='#26262B', padx=10, pady=5)
status_label.pack(side='right', padx=20, pady=15)

# -------------------------------------------------------------------------
# 4. 上方資訊卡 (改為展示三家分行數據合計的「全行總體根本原因」)
# -------------------------------------------------------------------------
metrics_frame = tk.Frame(root, bg='#121214')
metrics_frame.pack(fill='x', side='top', padx=15, pady=15)


def create_card(parent, title, value, color):
    card = tk.Frame(parent, bg='#1A1A1E', highlightbackground='#2D2D34', highlightthickness=1)
    card.pack(side='left', expand=True, fill='both', padx=8, pady=5)
    lbl = tk.Label(card, text=title, font=font_metric_lbl, fg='#A0A0AA', bg='#1A1A1E')
    lbl.pack(pady=(12, 2))
    val = tk.Label(card, text=f"{value:,}", font=font_metric_val, fg=color, bg='#1A1A1E')
    val.pack(pady=(0, 12))
    return card


create_card(metrics_frame, "全行網路傳輸異常合計", total_net, "#F87171")
create_card(metrics_frame, "全行人為操作失誤合計", total_human, "#FBBF24")
create_card(metrics_frame, "全行憑證權限過期合計", total_auth, "#FB923C")

# -------------------------------------------------------------------------
# 5. 中間主版面：左側精準分類通報、右側滿版矩陣統計圖
# -------------------------------------------------------------------------
main_frame = tk.Frame(root, bg='#121214')
main_frame.pack(fill='both', expand=True, side='top', padx=15, pady=5)

# (左側) 異常事件精準分類通報看板
left_frame = tk.Frame(main_frame, bg='#1A1A1E', width=450, highlightbackground='#2D2D34', highlightthickness=1)
left_frame.pack(side='left', fill='both', expand=False, padx=8)
left_frame.pack_propagate(False)

left_title = tk.Label(left_frame, text="各海外分行異常事件分類通報", font=("Microsoft JhengHei", 13, "bold"),
                      fg='#FFFFFF', bg='#26262B', anchor='w', padx=15, pady=8)
left_title.pack(fill='x')


def create_detailed_status(parent, code, name, total, net, human, auth, color):
    b_frame = tk.Frame(parent, bg='#222227', pady=10, padx=15)
    b_frame.pack(fill='x', padx=15, pady=8)

    # 頂部標題與總量
    top_f = tk.Frame(b_frame, bg='#222227')
    top_f.pack(fill='x')
    tk.Label(top_f, text=f"【{code}】{name}", font=("Microsoft JhengHei", 11, "bold"), fg='#FFFFFF', bg='#222227').pack(
        side='left')
    tk.Label(top_f, text=f"共 {total:,} 筆", font=("Helvetica", 12, "bold"), fg=color, bg='#222227').pack(side='right')

    # 細項數據顯示 (直接打出每一筆背後的原因數量)
    detail_str = f" └ 網路異常: {net} 筆  |  人為疏失: {human} 筆  |  憑證過期: {auth} 筆"
    tk.Label(b_frame, text=detail_str, font=("Microsoft JhengHei", 9), fg='#A0A0AA', bg='#222227', anchor='w').pack(
        fill='x', pady=(5, 0))


# 渲染三個分行的精準數據
create_detailed_status(left_frame, "HK", "HK branch - Anomaly data", hk_total_faults, hk_net, hk_human, hk_auth, "#F87171")
create_detailed_status(left_frame, "NY", "NY branch - Anomaly data", ny_total_faults, ny_net, ny_human, ny_auth, "#FBBF24")
create_detailed_status(left_frame, "SG", "SG branch - Anomaly data", sg_total_faults, sg_net, sg_human, sg_auth, "#FB923C")

# 增加一格：全行大總計看板，讓畫面在左邊就完美統計
total_frame = tk.Frame(left_frame, bg='#1E293B', pady=10, padx=15)
total_frame.pack(fill='x', padx=15, pady=15)
tk.Label(total_frame, text="📊 三家分行個數據合計 (全行總計)", font=("Microsoft JhengHei", 11, "bold"), fg='#38BDF8',
         bg='#1E293B').pack(anchor='w')
total_detail = f" 總故障源頭: {total_all_faults} 次\n 網路: {total_net} 筆 | 人為: {total_human} 筆 | 憑證: {total_auth} 筆"
tk.Label(total_frame, text=total_detail, font=("Microsoft JhengHei", 10), fg='#F1F5F9', bg='#1E293B', justify='left',
         anchor='w').pack(fill='x', pady=5)

# (右側) 滿版精準矩陣統計圖
right_frame = tk.Frame(main_frame, bg='#1A1A1E', highlightbackground='#2D2D34', highlightthickness=1)
right_frame.pack(side='right', fill='both', expand=True, padx=8)

plt.style.use('dark_background')
# 終極中文防亂碼強制設定
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'DFKai-SB', 'Arial']
plt.rcParams['axes.unicode_minus'] = False
import matplotlib

matplotlib.rc('font', family='Microsoft JhengHei')

# 建立單一圖表，放大拉滿
fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor('#1A1A1E')
ax.set_facecolor('#1A1A1E')

# 💥 畫出「分組長條圖」，橫軸是分行，柱子是三大根因
matrix_df.plot(kind='bar', color=['#FBBF24', '#FB923C', '#F87171'], ax=ax, width=0.6, rot=0)

ax.set_title("Root Cause Matrix Analysis", fontsize=13, fontweight='bold', pad=15)
ax.set_xlabel("Branch Code", fontsize=11, labelpad=10)
ax.set_ylabel("Count", fontsize=11, labelpad=10)
ax.grid(axis='y', linestyle='--', alpha=0.3)

# 調整圖例(Legend)位置與字體
ax.legend(title="Malfunction reason", prop={'size': 10.5}, facecolor='#222227', edgecolor='#2D2D34')

plt.tight_layout()

canvas = FigureCanvasTkAgg(fig, master=right_frame)
canvas.draw()
canvas.get_tk_widget().pack(fill='both', expand=True, padx=15, pady=15)


print("🚀 終極精準矩陣儀表板已成功開通！")
root.mainloop()

'''
import sys
import tkinter as tk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# -------------------------------------------------------------------------
# 1. Data Processing
# -------------------------------------------------------------------------
try:
    df = pd.read_csv('simulated_bank_batch_flow_log.csv')
except FileNotFoundError:
    print("❌ Error: 'simulated_bank_batch_flow_log.csv' not found.")
    sys.exit()

total_logs = len(df)
total_branch_cycles = len(df[['Cycle_ID', 'Branch_Code']].drop_duplicates())
fail_logs = df[(df['Job_ID'] == 'TX_GET_01') & (df['Root_Cause_Type'] != 'Normal')]


def get_branch_metrics(branch_code):
    b_df = df[(df['Branch_Code'] == branch_code) & (df['Status'].isin(['TIMEOUT', 'FAILED']))]
    total_faults = len(b_df)
    b_root_fails = df[
        (df['Branch_Code'] == branch_code) & (df['Job_ID'] == 'TX_GET_01') & (df['Root_Cause_Type'] != 'Normal')]

    net_count = len(b_root_fails[b_root_fails['Root_Cause_Type'] == '網路傳輸異常']) * 3
    human_count = len(b_root_fails[b_root_fails['Root_Cause_Type'] == '人為操作失誤']) * 3
    auth_count = len(b_root_fails[b_root_fails['Root_Cause_Type'] == '憑證權限過期']) * 3
    return total_faults, net_count, human_count, auth_count


hk_total, hk_net, hk_human, hk_auth = get_branch_metrics('HK')
ny_total, ny_net, ny_human, ny_auth = get_branch_metrics('NY')
sg_total, sg_net, sg_human, sg_auth = get_branch_metrics('SG')

grand_net = hk_net + ny_net + sg_net
grand_human = hk_human + ny_human + sg_human
grand_auth = hk_auth + ny_auth + sg_auth

# -------------------------------------------------------------------------
# 2. Tkinter UI (Professional English Dashboard)
# -------------------------------------------------------------------------
root = tk.Tk()
root.title("Global Banking Batch Operations - SIEM Monitoring Dashboard")
root.geometry("1450x820")
root.configure(bg='#121214')

# -------------------------------------------------------------------------
# 3. Header
# -------------------------------------------------------------------------
header_frame = tk.Frame(root, bg='#1A1A1E', height=60)
header_frame.pack(fill='x', side='top')
tk.Label(header_frame, text=" GLOBAL BANKING BATCH OPERATION CENTER", font=("Helvetica", 18, "bold"), fg='#FFFFFF',
         bg='#1A1A1E', anchor='w').pack(side='left', padx=20, pady=15)
tk.Label(header_frame, text="STATUS: OPERATIONAL (LIVE RISKS DETECTED)", font=("Helvetica", 10, "bold"), fg='#E67E22',
         bg='#26262B', padx=10, pady=5).pack(side='right', padx=20, pady=15)

# -------------------------------------------------------------------------
# 4. Metrics Row
# -------------------------------------------------------------------------
metrics_frame = tk.Frame(root, bg='#121214')
metrics_frame.pack(fill='x', side='top', padx=15, pady=15)


def create_card(parent, title, value, color):
    card = tk.Frame(parent, bg='#1A1A1E', highlightbackground='#2D2D34', highlightthickness=1)
    card.pack(side='left', expand=True, fill='both', padx=8, pady=5)
    tk.Label(card, text=title, font=("Helvetica", 11), fg='#A0A0AA', bg='#1A1A1E').pack(pady=(12, 2))
    tk.Label(card, text=f"{value:,}", font=("Helvetica", 32, "bold"), fg=color, bg='#1A1A1E').pack(pady=(0, 12))


create_card(metrics_frame, "Total System Logs Processed", total_logs, "#38BDF8")
create_card(metrics_frame, "Network Latency Faults", grand_net, "#F87171")
create_card(metrics_frame, "Human/Auth Errors", grand_human + grand_auth, "#FBBF24")

# -------------------------------------------------------------------------
# 5. Main Content
# -------------------------------------------------------------------------
main_frame = tk.Frame(root, bg='#121214')
main_frame.pack(fill='both', expand=True, side='top', padx=15, pady=5)

# Left Panel
left_frame = tk.Frame(main_frame, bg='#1A1A1E', width=480, highlightbackground='#2D2D34', highlightthickness=1)
left_frame.pack(side='left', fill='both', expand=False, padx=8)
left_frame.pack_propagate(False)
tk.Label(left_frame, text="Regional Incident Analysis", font=("Helvetica", 13, "bold"), fg='#FFFFFF', bg='#26262B',
         anchor='w', padx=15, pady=8).pack(fill='x')


def create_detailed_status(parent, code, name, total, net, human, auth, color):
    b_frame = tk.Frame(parent, bg='#222227', pady=10, padx=15)
    b_frame.pack(fill='x', padx=15, pady=8)
    top_line = tk.Frame(b_frame, bg='#222227')
    top_line.pack(fill='x')
    tk.Label(top_line, text=f"[{code}] {name}", font=("Helvetica", 11, "bold"), fg='#FFFFFF', bg='#222227').pack(
        side='left')
    tk.Label(top_line, text=f"Total: {total:,}", font=("Helvetica", 12, "bold"), fg=color, bg='#222227').pack(
        side='right')

    detail_str = f" ├─ Network Error: {net:,}\n ├─ Human Error: {human:,}\n └─ Auth/Perm Error: {auth:,}"
    tk.Label(b_frame, text=detail_str, font=("Helvetica", 10), fg='#A0A0AA', bg='#222227', justify='left',
             anchor='w').pack(fill='x', pady=(5, 0))


create_detailed_status(left_frame, "HK", "Hong Kong Branch", hk_total, hk_net, hk_human, hk_auth, "#F87171")
create_detailed_status(left_frame, "NY", "New York Branch", ny_total, ny_net, ny_human, ny_auth, "#FBBF24")
create_detailed_status(left_frame, "SG", "Singapore Branch", sg_total, sg_net, sg_human, sg_auth, "#FB923C")

# Right Panel
right_frame = tk.Frame(main_frame, bg='#1A1A1E', highlightbackground='#2D2D34', highlightthickness=1)
right_frame.pack(side='right', fill='both', expand=True, padx=8)

fig, ax1 = plt.subplots(figsize=(8, 5))
fig.patch.set_facecolor('#1A1A1E')
ax1.set_facecolor('#1A1A1E')
categories = ['Network Error', 'Human Error', 'Auth Error']
grand_totals = [grand_net, grand_human, grand_auth]
bars = ax1.bar(categories, grand_totals, color=['#F87171', '#FB923C', '#FBBF24'], width=0.4)
ax1.set_title("Global Incident Root Cause Aggregation", fontsize=13, fontweight='bold', pad=15, color='white')
ax1.set_ylabel("Incident Count", color='white')
ax1.tick_params(axis='x', colors='white')
ax1.tick_params(axis='y', colors='white')
ax1.grid(axis='y', linestyle='--', alpha=0.3)

for bar in bars:
    height = bar.get_height()
    ax1.annotate(f'{height:,}', xy=(bar.get_x() + bar.get_width() / 2, height), xytext=(0, 3),
                 textcoords="offset points", ha='center', va='bottom', fontsize=10, color='white')

canvas = FigureCanvasTkAgg(fig, master=right_frame)
canvas.draw()
canvas.get_tk_widget().pack(fill='both', expand=True, padx=15, pady=15)

root.mainloop()
