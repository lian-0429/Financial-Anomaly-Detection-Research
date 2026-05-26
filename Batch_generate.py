import csv
import random
from datetime import datetime, timedelta

num_cycles = 3000
branches = ['HK', 'SG', 'NY']
start_time = datetime(2026, 5, 1, 0, 0, 0)


with open('simulated_bank_batch_flow_log.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Timestamp', 'Cycle_ID', 'Branch_Code', 'Job_ID', 'Dependency_Job', 'Status', 'Duration_Sec', 'Root_Cause_Type'])

    for cycle in range(num_cycles):
        for branch in branches:
            base_time = start_time + timedelta(hours=cycle * 0.2) + timedelta(minutes=random.randint(0, 10))

            is_root_cause_fail = random.random() < 0.361

            if is_root_cause_fail:
                job1_status = 'FAILED'
                job1_dur = 0
                root_cause = random.choice(['網路傳輸異常', '人為操作失誤', '憑證權限過期'])
            else:
                job1_status = 'SUCCESS'
                job1_dur = random.randint(10, 30)
                root_cause = 'Normal'  

            time1 = base_time
            writer.writerow([time1.strftime('%Y-%m-%d %H:%M:%S'), f"C_{cycle}", branch, 'TX_GET_01', 'START', job1_status, job1_dur, root_cause])

            time2 = time1 + timedelta(seconds=job1_dur + random.randint(5, 15))
            if job1_status == 'FAILED':
                job2_status = 'TIMEOUT'
                job2_dur = random.randint(1800, 3600)
                current_cause = f"受波及 (源頭:{root_cause})"
            else:
                job2_status = 'SUCCESS'
                job2_dur = random.randint(60, 120)
                current_cause = 'Normal'
            writer.writerow([time2.strftime('%Y-%m-%d %H:%M:%S'), f"C_{cycle}", branch, 'TX_CLS_02', 'TX_GET_01', job2_status, job2_dur, current_cause])

            time3 = time2 + timedelta(seconds=job2_dur + random.randint(5, 15))
            job3_status = 'FAILED' if job2_status == 'TIMEOUT' else 'SUCCESS'
            job3_dur = random.randint(20, 50) if job3_status == 'SUCCESS' else 0
            current_cause3 = f"受波及 (源頭:{root_cause})" if job3_status == 'FAILED' else 'Normal'
            writer.writerow([time3.strftime('%Y-%m-%d %H:%M:%S'), f"C_{cycle}", branch, 'TX_RPT_03', 'TX_CLS_02', job3_status, job3_dur, current_cause3])
