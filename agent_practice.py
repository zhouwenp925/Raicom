import json,requests,os
# 文件顶部导入自己定义的校验类
from plan_schema import WorkPlan
TOOLS={
    # 查询房间设备状态
    "shelf_query": "http://127.0.0.1:9500/tools/shelf_query",
    # 查询服务日志
    "log_query": "http://127.0.0.1:9500/tools/log_query",
    "kb_query": "http://127.0.0.1:9500/tools/kb_query",
    "resource_query":"http://127.0.0.1:9500/tools/resource_query"
}
def call_tool(name,args):
    response=requests.get(
        TOOLS[name],
        params=args,
        timeout=5
    )
    response.raise_for_status()
    result=response.json()
    # 整理本次成功调用的记录
    record = {
        "tool": name,
        "args": args,
        "result": result
    }
    # 创建日志目录；已存在时不报错
    os.makedirs("submission/m3", exist_ok=True)
    with open("submission/m3/agent_run_log.jsonl","a",encoding="utf-8")as f:
        line=json.dumps(record,ensure_ascii=False)+"\n"
        f.write(line)
    return result

def excutor(plan):
    logs=[]
    for step in plan["steps"]:
        name=step["tool"]
        arg=step["args"]
        result=call_tool(name,arg)
        logs.append({
            "tool":name,
            "args":arg,
            "result":result
        })
    return logs
# feedback 用来接收上一次的错误说明，首次调用时为空
def planner(ticket,feedback=""):
    messages=[{
        "role":"system",
        "content": """
你是图书馆工单调度员，根据工单生成工具调用计划。
只输出合法 JSON，不要输出解释或 Markdown 代码块。

可用工具及参数：
1. shelf_query：查询设备状态，参数 room。
2. log_query：查询服务日志，参数 service。
3. kb_query：查询借阅政策，参数 q。
4. resource_query：查询电子资源并发状态，参数 db。

规划规则：
- 设备故障或报修：先调用 shelf_query，再调用 log_query。
- 借阅、借阅卡办理或补办政策：调用 kb_query。
- 电子资源并发、访问人数、是否已满：调用 resource_query。
- 其他问题：steps 返回空列表。

参数规则：
- ticket_id、room、service、db 使用当前工单提供的值。
- kb_query 的 q 使用工单的 text。
- resource_query 未提供 db 时，args 使用 {}，由工具采用默认值。
- 不要编造工单中没有提供的房间或服务代号。

输出必须包含 ticket_id、intent、steps。
本练习约定：报修 intent 为 repair，咨询为 consult，其他为 other。
steps 中每项必须包含 tool 和 args。

借阅政策示例：
{"ticket_id":"T2002","intent":"consult","steps":[{"tool":"kb_query","args":{"q":"借阅卡补办需要什么材料？"}}]}

电子资源示例：
{"ticket_id":"T2003","intent":"consult","steps":[{"tool":"resource_query","args":{"db":"cnki"}}]}

请根据当前工单填写实际内容。
"""
    },
    {
        "role":"user",
        "content":json.dumps(ticket,ensure_ascii=False)
    }]
    response=requests.post(
        "http://127.0.0.1:8700/v1/chat/completions",
        json={"messages":messages},
        timeout=120
    )
    response.raise_for_status()
    data=response.json()
    text=json.loads(data["choices"][0]["message"]["content"])
    # 检查
    checked=WorkPlan.model_validate(text)
    # 将 JSON 文字解析成 Python 字典
    return checked.model_dump()
# 检查建议草稿，返回最终回复
def executor_summarize(ticket,logs):
    messages = [
        {
            "role": "system",
            "content": (
                "你是图书馆运维助手。"
                "请根据工单和工具查询结果，给出简短处理建议。"
                "保留结果中的模拟说明。"
                "工具只查询了状态，不要声称已经完成维修。"
            )
        },
        {
            "role": "user",
            # 将工单和执行记录整理成文字，供模型阅读
            "content": json.dumps(
                {"ticket": ticket, "logs": logs},
                ensure_ascii=False
            )
        }
    ]
    # 向之前写好的模型服务提交对话
    response=requests.post(
        "http://127.0.0.1:8700/v1/chat/completions",
        json={"messages":messages},
        timeout=120
    )
    response.raise_for_status()
    data=response.json()
    return data["choices"][0]["message"]["content"]

# 检查建议草稿，返回最终回复
def qa_check(draft):
    if not isinstance(draft,str) or not draft.strip():
        return "未能生成有效处理建议，请联系管理员核查。"
    return draft.strip()
# 直接运行本文件时才执行测试，导入时不执行
if __name__ == "__main__":
    tickets = [
        {
            "ticket_id": "T2002",
            "text": "借阅卡补办需要什么材料？"
        },
        {
            "ticket_id": "T2003",
            "text": "查询知网当前并发是否已满。",
            "db": "cnki"
        }
    ]
    for ticket in tickets:
        print("\n当前工单：", ticket["text"])

        # 生成并校验计划
        plan = planner(ticket)
        print("计划：", json.dumps(plan, ensure_ascii=False))

        # 执行工具，并按之前的代码写入调用日志
        logs = excutor(plan)
        print("执行记录：", json.dumps(logs, ensure_ascii=False))

        # 生成建议，再进行基础质检
        draft = executor_summarize(ticket, logs)
        final = qa_check(draft)
        print("最终回复：", final)