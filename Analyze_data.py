import sys
import sqlite3
import tkinter as tk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# 1. Data Processing
try:
    conn = sqlite3.connect('bank_batch_data.db')
    df = pd.read_sql_query("SELECT * FROM batch_logs", conn)
    conn.close()
except Exception as e:
    print(f"Error: {e}")
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
us_total, us_net, us_human, us_auth = get_branch_metrics('US')
sg_total, sg_net, sg_human, sg_auth = get_branch_metrics('SG')
cn_total, cn_net, cn_human, cn_auth = get_branch_metrics('CN')
uk_total, uk_net, uk_human, uk_auth = get_branch_metrics('UK')
nz_total, nz_net, nz_human, nz_auth = get_branch_metrics('NZ')
in_total, in_net, in_human, in_auth = get_branch_metrics('IN')




grand_net = hk_net + us_net + sg_net + cn_net + uk_net + nz_net + in_net
grand_human = hk_human + us_human + sg_human + cn_human + uk_human + nz_human + in_human
grand_auth = hk_auth + us_auth + sg_auth + cn_auth + uk_auth + nz_auth + in_auth

# 2. Tkinter UI (Professional English Dashboard)
root = tk.Tk()
root.title("Security Information and Event Management Monitoring Dashboard")
root.geometry("1450x820")
root.configure(bg='#121214')

# 3. Header
header_frame = tk.Frame(root, bg='#1A1A1E', height=60)
header_frame.pack(fill='x', side='top')
tk.Label(header_frame, text="  MOCK GLOBAL BANKING BATCH OPERATION CENTER", font=("Helvetica", 18, "bold"), fg='#FFFFFF',
         bg='#1A1A1E', anchor='w').pack(side='left', padx=20, pady=15)

# 4. Metrics Row
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

# 5. Main Content
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
create_detailed_status(left_frame, "US", "United States of America Branch", us_total, us_net, us_human, us_auth, "#FBBF24")
create_detailed_status(left_frame, "SG", "Singapore Branch", sg_total, sg_net, sg_human, sg_auth, "#FB923C")
create_detailed_status(left_frame, "CN", "China Branch", cn_total, cn_net, cn_human, cn_auth, "#F87171")
create_detailed_status(left_frame, "Uk", "United Kingdom Branch", uk_total, uk_net, uk_human, uk_auth, "#FBBF24")
create_detailed_status(left_frame, "NZ", "New Zealand Branch", nz_total, nz_net, nz_human, nz_auth, "#FB923C")
create_detailed_status(left_frame, "IN", "India Branch", in_total, in_net, in_human, in_auth, "#F87171")

# Right Panel
right_frame = tk.Frame(main_frame, bg='#1A1A1E', highlightbackground='#2D2D34', highlightthickness=1)
right_frame.pack(side='right', fill='both', expand=True, padx=8)

fig, ax1 = plt.subplots(figsize=(8, 5))
fig.patch.set_facecolor('#1A1A1E')
ax1.set_facecolor('#1A1A1E')
categories = ['Network Error', 'Human Error', 'Auth Error']
grand_totals = [grand_net, grand_human, grand_auth]
bars = ax1.bar(categories, grand_totals, color=['#F87171', '#FB923C', '#FBBF24'], width=0.4)
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
