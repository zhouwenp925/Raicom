import requests
from audit_step1 import write_audit
from route_step1 import route
from agent_step1 import(
    planner,
    executor,
    executor_summarize,
    qa_check
)
SENSITIVE = ["删除数据库", "关机", "重启服务器", "清除日志"]

def run_workflow(ticket):
    plan = planner(ticket)
    logs = executor(plan)
    draft = executor_summarize(ticket, logs)
    return qa_check(draft)

def repair_agent(ticket):
    return run_workflow(ticket)

# 咨询智能体：调用之前写好的 RAG 接口
def visitor_agent(ticket):
    question = ticket["text"]

    # 约定的资源查询关键词
    resource_keywords = ["电子资源", "并发", "知网", "万方", "cnki"]
    if any(k in question.lower() for k in resource_keywords):
        return run_workflow(ticket)
    
    response=requests.post(
        "http://127.0.0.1:8100/rag",
        json={"question":question},
        timeout=120
    )
    response.raise_for_status()
    return response.json()["answer"]

# 统一处理入口
def assistent(ticket):
    question=ticket["text"]
    # 先检查敏感指令
    if any(s in question for s in SENSITIVE):
        # 当前还没有用户身份信息，先记为匿名请求
        write_audit(
            user="anonymous",
            action="sensitive_block",
            result={"question":question,"blocked":True}
        )
        return {
            "reply":"请求涉及敏感操作，已拦截，请联系管理员。",
            "blocked":True
        }
    # 通过检查后，再进行路由
    name=route(question)
    if name=="repair_agent":
        reply=repair_agent(ticket)
    else:
        reply=visitor_agent(ticket)
    return {
        "agent":name,
        "reply":reply,
        "blocked":False
    }

if __name__ == "__main__":
    ticket = {
        "ticket_id": "T2003",
        "text": "借阅卡补办需要什么材料？",
        "room": "R305",
        "service": "rfid"
    }

    print(assistent(ticket))