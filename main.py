import json
import logging
from datetime import datetime
import pytz
import os
import requests

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
    if not isinstance(text, str):
        return text
    special_chars = r"\`*#"
    for ch in special_chars:
        text = text.replace(ch, f"\\{ch}")
    return text

def load_birthdays(file_path='data.json'):
    """读取新版 JSON 并进行 Markdown 转义"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    escaped_data = []
    for entry in data:
        escaped_entry = {}
        for key, value in entry.items():
            # 日期和企划代号本身不需要转义，其他字符串内容进行转义
            if key in ["birthday", "project"]:
                escaped_entry[key] = value
            else:
                escaped_entry[key] = escape_markdown(str(value))
        escaped_data.append(escaped_entry)
    return escaped_data

def get_today_in_tokyo():
    """获取东京时间"""
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
    """根据字典键值构建生日祝福文本"""
    band = entry.get("band", "")
    position = entry.get("role", "")
    name = entry.get("name", "")
    
    # 判断是否存在 'character' 字段来区分是声优还是角色
    if "character" in entry:
        character = entry["character"]
        if character.endswith("ex"):
            clean_character = character[:-2]  # 去掉末尾的 "ex"
            msg = f"现在是日本时间{readable_date}{current_time}，{readable_date}是{band}的{position}，{clean_character}的前声优**{name}**的生日，祝她生日快乐🎉！"
        else:
            msg = f"现在是日本时间{readable_date}{current_time}，{readable_date}是{band}的{position}，{character}的声优**{name}**的生日，祝她生日快乐🎉！"
        return msg, name
    else:
        # 如果没有 character 字段，说明当前这层就是角色本身
        msg = f"现在是日本时间{readable_date}{current_time}，{readable_date}是{band}的{position}，**{name}**的生日，祝她生日快乐🎉！"
        return msg, name

def send_message(msg, project_name):
    """发送 Webhook 请求"""
    if not WEBHOOK_URL:
        logging.warning("未配置 WEBHOOK_URL 环境变量，跳过发送。")
        return
        
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
        # 直接通过 key 获取日期进行比对
        target_date = entry.get("birthday")
        
        if target_date == date_raw:
            # 解析企划名：如果有 project 字段就走映射表，没有就默认邦多利
            project_code = entry.get("project")
            if project_code:
                project_name = PROJECT_MAP.get(project_code, project_code)
            else:
                project_name = "邦多利"
                
            msg, identifier = build_message(entry, readable_date, current_time)
            if msg:
                send_message(msg, project_name)
                logging.info(f"已发送 {identifier} 的生日提醒")

if __name__ == "__main__":
    main()