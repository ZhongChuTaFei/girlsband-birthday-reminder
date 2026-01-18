import json
import logging
from datetime import datetime
import pytz
import os
import requests
import re

# 设置日志格式（东京时间）
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s][%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logging.Formatter.converter = lambda *args: datetime.now(pytz.timezone("Asia/Tokyo")).timetuple()

WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # 从环境变量读取 webhook

# 企划代号映射表
PROJECT_MAP = {
    "GBC": "嘎嘣脆"
}

def escape_markdown(text):
    """转义 Markdown 特殊符号，防止被解释"""
    special_chars = r"\`*#"
    for ch in special_chars:
        text = text.replace(ch, f"\\{ch}")
    return text

def load_birthdays(file_path='birthdays.json'):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 对 JSON 数据里的每个字段做转义，防止 Markdown 渲染
    escaped_data = []
    for entry in data:
        escaped_entry = []
        for i, item in enumerate(entry):
            if i < len(entry) - 1:
                escaped_entry.append(escape_markdown(str(item)))  # 除最后一项外都转义
            else:
                escaped_entry.append(item)  # 最后一项保持原样
        escaped_data.append(escaped_entry)
    return escaped_data

def get_today_in_tokyo():
    tz_tokyo = pytz.timezone('Asia/Tokyo')
    dt = datetime.now(tz_tokyo)
    date_raw = dt.strftime("%m-%d")
    readable_date = f"{int(dt.month)}月{int(dt.day)}日"

    if dt.minute == 0:
        current_time = f"{dt.hour}点整"
    else:
        current_time = f"{dt.hour}点{dt.strftime('%M')}分"  # 分钟补零

    return date_raw, readable_date, current_time

def build_message(entry, readable_date, current_time):

    if len(entry) == 4:
        role, band, position, _ = entry
        return f"现在是日本时间{readable_date}{current_time}，{readable_date}是{band}的{position}，**{role}**的生日，祝他生日快乐🎉！", role
    elif len(entry) == 5:
        name, role, band, position, _ = entry
        if role.endswith("ex"):
            clean_role = role[:-2]  # 去掉末尾的 "ex"
            return f"现在是日本时间{readable_date}{current_time}，{readable_date}是{band}的{position}，{clean_role}的前声优**{name}**的生日，祝他生日快乐🎉！", name
        else:
            return f"现在是日本时间{readable_date}{current_time}，{readable_date}是{band}的{position}，{role}的声优**{name}**的生日，祝他生日快乐🎉！", name

    return None, None

def send_message(msg, project_name):
    body = {
        "msgtype": "markdown",
        "markdown": {
            "content": f"# 🎂 <font color=\"warning\">**{project_name}生日提醒**</font>\n>{msg}"
        }
    }
    response = requests.post(WEBHOOK_URL, json=body)
    logging.info(f"已发送生日提醒，内容: {msg}，状态码: {response.status_code}")

def main():
    birthdays = load_birthdays()
    date_raw, readable_date, current_time = get_today_in_tokyo()

    for entry in birthdays:
        # --- 步骤 A: 初始化默认值 ---
        project_name = "邦多利"       # 默认企划名
        check_item = str(entry[-1])  # 拿最后一项检查
        
        # --- 步骤 B: 判断最后一项是 日期 还是 企划代号 ---
        if not re.match(r"^\d{2}-\d{2}$", check_item):
            # 如果不是日期（例如是 "GBC"）
            code = check_item
            project_name = PROJECT_MAP.get(code, code) # 查字典：GBC -> 嘎嘣脆
            
            data_entry = entry[:-1]      # 数据变成去掉 GBC 的部分
            target_date = data_entry[-1] # 日期是倒数第二项
        else:
            # 如果是日期（标准数据）
            data_entry = entry
            target_date = check_item
        if target_date == date_raw:
            msg, identifier = build_message(data_entry, readable_date, current_time)
            if msg:
                send_message(msg, project_name)
                logging.info(f"已发送 {identifier} 的生日提醒")

if __name__ == "__main__":
    main()
