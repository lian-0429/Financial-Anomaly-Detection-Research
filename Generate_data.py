import sqlite3
import random
from datetime import datetime, timedelta

num_cycles = 3000
start_time = datetime(2030, 1, 1, 0, 0, 0)

branch_failure_rates = {
    'HK': 0.150, 'SG': 0.127, 'US': 0.038,
    'CN': 0.118, 'UK': 0.074, 'NZ': 0.012, 'IN': 0.097
}

conn = sqlite3.connect('bank_batch_data.db')
cursor = conn.cursor()

cursor.execute('DROP TABLE IF EXISTS batch_logs')
cursor.execute('''CREATE TABLE batch_logs (
                    Timestamp TEXT, Cycle_ID TEXT, Branch_Code TEXT, 
                    Job_ID TEXT, Dependency_Job TEXT, Status TEXT, 
                    Duration_Sec INTEGER, Root_Cause_Type TEXT)''')

print("開始生成模擬資料...")

for cycle in range(num_cycles):
    # 對每一個分行分別計算機率並寫入
    for branch, fail_rate in branch_failure_rates.items():
        base_time = start_time + timedelta(hours=cycle * 0.2) + timedelta(minutes=random.randint(0, 10))
        is_root_cause_fail = random.random() < fail_rate

        # --- Job 1 ---
        if is_root_cause_fail:
            job1_status = 'FAILED'
            job1_dur = 0
            root_cause = random.choice(['網路傳輸異常', '人為操作失誤', '憑證權限過期'])
        else:
            job1_status = 'SUCCESS'
            job1_dur = random.randint(10, 30)
            root_cause = 'Normal'

        cursor.execute("INSERT INTO batch_logs VALUES (?,?,?,?,?,?,?,?)",
                       (base_time.strftime('%Y-%m-%d %H:%M:%S'), f"C_{cycle}", branch, 'TX_GET_01', 'START', job1_status, job1_dur, root_cause))

        # --- Job 2 ---
        time2 = base_time + timedelta(seconds=job1_dur + random.randint(5, 15))
        if job1_status == 'FAILED':
            job2_status = 'TIMEOUT'
            job2_dur = random.randint(1800, 3600)
            current_cause = f"受波及 (源頭:{root_cause})"
        else:
            job2_status = 'SUCCESS'
            job2_dur = random.randint(60, 120)
            current_cause = 'Normal'

        cursor.execute("INSERT INTO batch_logs VALUES (?,?,?,?,?,?,?,?)",
                       (time2.strftime('%Y-%m-%d %H:%M:%S'), f"C_{cycle}", branch, 'TX_CLS_02', 'TX_GET_01', job2_status, job2_dur, current_cause))

        # --- Job 3 ---
        time3 = time2 + timedelta(seconds=job2_dur + random.randint(5, 15))
        job3_status = 'FAILED' if job2_status == 'TIMEOUT' else 'SUCCESS'
        job3_dur = random.randint(20, 50) if job3_status == 'SUCCESS' else 0
        current_cause3 = f"受波及 (源頭:{root_cause})" if job3_status == 'FAILED' else 'Normal'

        cursor.execute("INSERT INTO batch_logs VALUES (?,?,?,?,?,?,?,?)",
                       (time3.strftime('%Y-%m-%d %H:%M:%S'), f"C_{cycle}", branch, 'TX_RPT_03', 'TX_CLS_02', job3_status, job3_dur, current_cause3))

conn.commit()
conn.close()
print("模擬資料已成功寫入，共有 7 家分行，每家 3000 個週期。")
