from fastapi import FastAPI
from pydantic import BaseModel
# 用于明确设置返回的 JSON 内容和 HTTP 状态码
from fastapi.responses import JSONResponse
from cache_step1 import cached_rag_answer,CACHE
from rag_step3 import rag_answer
from text1 import generate
# 规定客户端必须提交字符串类型的 question
class RagRequest(BaseModel):
    question:str
    # 客户端不提供时，默认使用缓存
    use_cache: bool = True

# 明确声明：这两个字段必填，类型为字符串
class ChatRequest(BaseModel):
    session_id:str
    text:str
class SummarizeRequest(BaseModel):
    text:str
app=FastAPI()
# 保存各个会话的历史，放在函数外，供后续请求继续使用
HISTORY={}
# 最多保留 4 条历史消息，即最近两轮完整对话
MAX_HISTORY_MESSAGES=4

# POST 用于提交内容，让服务按接口定义处理。聊天和摘要都适合采用 POST
@app.post("/chat")
async def chat(req:ChatRequest):
    # 读取客户端发送的 JSON
    # 取得会话编号和本次问题
    sid=req.session_id
    text=req.text
    # 已有这个会话：取得原来的列表
    # 没有这个会话：创建并保存一个空列表
    """
    if sid not in HISTORY:
    HISTORY[sid] = []
    history = HISTORY[sid]
    """
    #HISTORY	字典，保存所有会话的历史
    #history	列表，表示当前会话的历史
    history=HISTORY.setdefault(sid,[])
    # 保存本次用户问题
    history.append({"role":"user","content":text})
    # 将历史和本次问题一起交给模型
    # 加上助手的身份说明，再传入对话历史
    messages = [
        {
            "role": "system",
            "content": "你是聊天助手。请根据对话历史回答，注意区分用户和助手的身份。不要把用户的东西认为是你自己的"
        }
    ] + history

    # 默认是正常回复
    fallback=False
    try:
        answer=generate(messages)
    
    except Exception as error:
        # 调用出错时，记录错误并准备降级回复
        print("模型出现错误",error)
        answer="系统繁忙，请稍后重试，或致电图书馆总服务台6600。"
        fallback=True

    history.append({"role":"assistant","content":answer})
    HISTORY[sid]=history[-MAX_HISTORY_MESSAGES:]
    print("历史消息数：", len(HISTORY[sid]))
    # 按样题格式返回结果
    return JSONResponse(
        content={
            "session_id":sid,
            "reply":answer,
            "fallback":fallback
        },
        status_code=200
    )
@app.post("/summarize")
async def summarize(req:SummarizeRequest):
    que=req.text
    messages=[
        {"role":"system","content":"请生成100字以内摘要,一定要比用户给的信息要简洁"},
        {"role":"user","content":que}
    ]
    summary = generate(messages, max_new_tokens=128)
    if len(summary)>128:
        summary=summary[:128]
    # 返回摘要，以及最终摘要的字符数
    return JSONResponse(
        {
            "summary":summary,
            "chars":len(summary)
        }
    )
@app.post("/rag")
def rag(req:RagRequest):
    if req.use_cache:
        # 开启缓存：先检查有没有保存过回答
        result=cached_rag_answer(req.question)
    else:
        # 关闭缓存：每次都重新检索、生成回答
        result=rag_answer(req.question)
        # 本次没有使用缓存
        result["cache_hit"]=False
    return result
@app.post("/cache/clear")
def clear_cache():
    # 清空服务进程中保存的全部缓存
    CACHE.clear()
    return {"cleared":True}