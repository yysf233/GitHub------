import json
import os
import datetime

# 读取本次运行的详细日志
log_file = "log.txt"
if os.path.exists(log_file):
    with open(log_file, "r", encoding='utf-8') as f:
        current_log = f.read()
else:
    current_log = "Log file not found."

# 获取当前时间 (北京时间简单处理: UTC+8)
#GitHub Actions 默认是 UTC，这里简单加 8 小时显示
utc_now = datetime.datetime.utcnow()
bj_now = utc_now + datetime.timedelta(hours=8)
timestamp_str = bj_now.strftime("%Y-%m-%d %H:%M:%S")

# 构造新的记录对象
new_record = {
    "id": os.environ.get("GITHUB_RUN_ID", "local-run"),
    "timestamp": timestamp_str,
    "status": os.environ.get("RUN_STATUS", "unknown"),
    "logs": current_log
}

# 读取历史数据
data_file = "frontend/data.json"
history = []

if os.path.exists(data_file):
    try:
        with open(data_file, "r", encoding='utf-8') as f:
            history = json.load(f)
    except json.JSONDecodeError:
        print("Existing data.json is corrupt, starting fresh.")
        history = []

# 把新记录插到最前面
history.insert(0, new_record)

# 只保留最近 50 条 (防止文件无限膨胀)
history = history[:50]

# 写回文件
with open(data_file, "w", encoding='utf-8') as f:
    json.dump(history, f, indent=2, ensure_ascii=False)

print(f"History updated with record at {timestamp_str}.")
