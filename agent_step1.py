import json
import requests
import os
from text1 import generate
from plan_schema import WorkPlan
# 工具
TOOLS={
    "shelf_query":"http://127.0.0.1:9500/tools/shelf_query",
    "log_query":"http://127.0.0.1:9500/tools/log_query",
    "kb_query": "http://127.0.0.1:9500/tools/kb_query",
    "resource_query":"http://127.0.0.1:9500/tools/resource_query"
}
# 模拟一条工单，信息先由我们提供
ticket = {
        "ticket_id": "T2006",
        "text": "查询电子资源当前并发是否已满。",
        "db": "cnki"
}
def planner(ticket):
    messages=[
        {
            "role":"system",
            "content": """
你是图书馆工单调度员，根据工单生成工具调用计划。
只输出合法 JSON，不要输出解释或 Markdown 代码块。

可用工具：
1. shelf_query：查询设备状态，参数 room。
2. log_query：查询服务日志，参数 service。
3. kb_query：查询借阅政策，参数 q。
4. resource_query：查询电子资源并发状态，参数 db。

本次练习的规划规则：
- 查询电子资源并发、访问人数或是否已满：调用 resource_query。
- 设备故障或报修：先调用 shelf_query，再调用 log_query。
- 查询借阅政策：调用 kb_query。
- 其他问题：steps 返回空列表。

参数规则：
- ticket_id、room、service、db 使用当前工单提供的值。
- kb_query 的 q 使用工单的 text。
- resource_query 未提供 db 时，可以使用空参数 {}，由工具采用默认值。

返回对象必须包含 ticket_id、intent、steps。
本课约定：报修的 intent 为 repair，咨询为 consult，其他为 other。
steps 中每项必须包含 tool 和 args，工具名只能来自上述列表。

格式示例：
{"ticket_id":"T2006","intent":"consult","steps":[{"tool":"resource_query","args":{"db":"cnki"}}]}
请根据当前工单填写实际内容。
"""
        },
        {
            "role":"user",
            "content":json.dumps(ticket,ensure_ascii=False)
        }
    ]
    text=generate(messages,max_new_tokens=256)
    print("原始计划：")
    print(text)

    # 将模型生成的 JSON 字符串解析成 Python 字典
    data=json.loads(text)
    # 根据 WorkPlan 检查字段、类型和工具名称
    # model_validate() 按模型定义验证数据
    checked=WorkPlan.model_validate(data)
    # model_dump() 把校验后的对象转换成字典，里面的嵌套对象也会一起转换
    # 校验后的对象 → 普通字典，供原来的 executor 使用
    return checked.model_dump()
def executor(plan):
    # 保存每一步的执行记录
    logs=[]
    for step in plan["steps"]:
        name=step["tool"]
        args=step["args"]
        # 实际调用工具，取得结果
        result=call_tool(name,args)
        # 记录：调用什么工具、传了什么参数、得到什么结果
        logs.append(
            {
                "tool":name,
                "args":args,
                "result":result
            }
        )
    return logs
# 创建日志目录，已经存在时不报错
os.makedirs("submission/m3",exist_ok=True)
def call_tool(name,args):
    # params 将参数放入 URL 查询字符串
    response = requests.get(
        TOOLS[name],
        params=args,
        timeout=5
    )
    # HTTP 请求失败时抛出异常
    response.raise_for_status()
    # 将工具返回的 JSON 转成 Python 对象
    result=response.json()
    # 整理一条调用记录
    record={
        "tool":name,
        "args":args,
        "result":result
    }
    # a 表示追加写入，保留之前的记录
    with open(
        "submission/m3/agent_run_log.jsonl",
        "a",
        encoding="utf-8"
    )as f:
        # 每条记录转换成 JSON 字符串，再加一个换行符
        line=json.dumps(record,ensure_ascii=False)+"\n"
        f.write(line)
    return result
# 根据工单和工具执行记录，生成建议草稿
def executor_summarize(ticket,logs):
    messages = [
        {
            "role":"system",
            "content":(
                    "你是图书馆运维助手，请根据工单和工具结果给出简洁处理建议。"
                    "保留工具结果中的模拟说明。"
                    "工具只查询了状态，不要声称已经完成维修。"
            )
        },
        {
            "role":"user",
            "content":json.dumps(
                {"ticket":ticket,"logs":logs},
                ensure_ascii=False
            )
        }
    ]
    return generate(messages,max_new_tokens=128)
# 最小质检：检查有没有有效的文字输出
def qa_check(draft):
    if not isinstance(draft,str)or not draft.strip():
        return "未能生成有效处理建议，请联系管理员核查。"
    return draft.strip()

if __name__=="__main__":
    plan=planner(ticket)
    print("解析后的类型：", type(plan))
    print("选中的工具：", [s["tool"] for s in plan["steps"]])
    # 将 Python 字典转成 JSON 字符串，便于查看
    # indent=2表示：输出JSON时，每一层缩进两个空格
    #print(json.dumps(plan,ensure_ascii=False,indent=2))
    logs=executor(plan)
    # 依据执行记录生成建议草稿
    draft=executor_summarize(ticket,logs)
    # 检查草稿，取得最终回复
    final=qa_check(draft)
    print("工具执行记录：")
    # ensure_ascii=False生成 JSON 字符串时，直接显示中文
    print(json.dumps(logs,ensure_ascii=False,indent=2))
    print("最终建议：")
    print(final)