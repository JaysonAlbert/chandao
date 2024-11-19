# %%
import os
import subprocess
import openai
from datetime import datetime
from collections import defaultdict
import json
import re

# 配置 OpenAI API

openai.api_key = "123123123"
openai.api_base = "http://chat.openai.com/v1"  # 替换为你的自定义 API 地址

def get_git_logs(repo_path, author, since, until):
    """提取指定时间范围内的日志记录"""
    os.chdir(repo_path)
    subprocess.run(
    ["git", "checkout", "develop"]
    )
    subprocess.run(["git", "pull", "upstream", "develop"])
    result = subprocess.run(
        [
            "git", "log", 
            "--author", author,
            f"--since={since}", 
            f"--until={until}", 
            "--date=short", 
            "--no-merges",  # 排除合并提交
            "--pretty=format:%ad %s"
        ],
        stdout=subprocess.PIPE, text=True
    )
    logs = result.stdout.split("\n")
    return logs

def group_logs_by_day(logs):
    """将日志按日期分组"""
    grouped_logs = defaultdict(list)
    for log in logs:
        try:
            date, message = log.split(" ", 1)
        except Exception as e:
            print(f"日志处理失败： {log}")
        grouped_logs[date].append(message)
    return grouped_logs

def estimate_tasks_with_ai(date, messages):
    """使用大模型进行任务拆分和工时估算"""
    prompt = f"以下是 {date} 的开发日志：\n" + "\n".join(messages) + \
             "\n请根据日志内容总结开发任务，当天有多个任务时，可总结任务，以减少任务总数量，并估算每个任务所需工时（小时），保证任务总工时为8小时。以JSON格式返回，示例如下：" \
             '\n[{"task": "任务描述", "hours": 4}, {"task": "任务描述", "hours": 4}]'
    response = openai.ChatCompletion.create(
        model="gpt4",
        messages=[{"role": "user", "content": prompt}]
    )
    return extract_json_from_ai_response(response['choices'][0]['message']['content'])

def extract_json_from_ai_response(ai_response):
    """从AI返回的文本中提取JSON结构"""
    try:
        # 使用正则表达式提取 ```json``` 内的部分
        json_str = re.search(r"```json\n(.*?)\n```", ai_response, re.S).group(1)
        # 将提取的JSON字符串解析为Python对象
        return json.loads(json_str)
    except Exception as e:
        print(f"提取JSON失败: {e}")
        return None

def analyze_work(repo_paths, author, since, until):
    """综合分析所有仓库的日志并生成每日任务报告"""
    all_logs = []
    for repo_path in repo_paths:
        logs = get_git_logs(repo_path, author, since, until)
        all_logs.extend(logs)
    
    grouped_logs = group_logs_by_day(all_logs)
    report = {}
    for date, messages in grouped_logs.items():
        ai_response = estimate_tasks_with_ai(date, messages)
        report[date] = ai_response
    return report

def save_report(report, output_file):
    """保存报告到文件"""
    with open(output_file, "w") as f:
        json.dump(report, f, ensure_ascii=False, indent=4) 

# 示例运行
repo_paths = [
    "project1", 
    "project2"
             ]  # Git 仓库路径列表
author = "au"  # 开发者邮箱或名字
output_file = "work_summary.json"
since = "2024-09-15"  # 开始时间
until = "2024-11-19"  # 结束时间

report = analyze_work(repo_paths, author, since, until)
save_report(report, output_file)

print(f"工作概况已生成，保存至 {output_file}")
