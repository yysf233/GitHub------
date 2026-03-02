import datetime
import time
import random

def main():
    print(f"--- 任务开始 ---")
    print(f"时间: {datetime.datetime.now()}")
    
    steps = ["初始化环境...", "连接数据库...", "抓取数据...", "处理数据...", "生成报告..."]
    
    for step in steps:
        print(f"[INFO] {step}")
        # 模拟任务耗时
        time.sleep(1) 
        
        # 模拟随机日志输出
        if random.random() < 0.3:
            print(f"[DEBUG] 处理细节: {random.randint(1000, 9999)}")

    print(f"--- 任务完成 ---")
    print(f"总耗时: {random.randint(5, 15)} 秒")

if __name__ == "__main__":
    main()
