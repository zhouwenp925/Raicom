import json
import os
from datetime import datetime

def read_audit():
    path="submission/m3/audit_log.jsonl"
    # 文件尚未创建时，返回空列表
    if not os.path.exists(path):
        return []
    records=[]
    with open(path,"r",encoding="utf-8")as f:
        for line in f:
            # 跳过空行
            if line.strip():
                # 每行是一个 JSON 字符串，解析成字典
                records.append(json.loads(line))
    return records
def write_audit(user,action,result):
    # 创建存放日志的目录
    os.makedirs("submission/m3",exist_ok=True)
    record={
        "timestamp":datetime.now().isoformat(), # 发生时间
        "user":user, # 操作者
        "action":action, # 操作名称
        "result":result # 处理结果
    }
    with open("submission/m3/audit_log.jsonl","a",encoding="utf-8")as f:
        f.write(json.dumps(record,ensure_ascii=False)+"\n")
