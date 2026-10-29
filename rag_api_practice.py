from fastapi import FastAPI
from retrieve_practice import retrieve
from fastapi.responses import JSONResponse
from cache_step1 import cached_rag_answer,CACHE
from pydantic import BaseModel
# 规定客户端必须提交字符串类型的 question
class RagRequest(BaseModel):
    question:str
    # 不提供时，默认使用缓存
    use_cache: bool = True
app=FastAPI()
@app.post("/rag")
def rag(req:RagRequest):
    try:
        if req.use_cache:
            # 提取问题，执行检索和模型调用
            # 缓存命中：直接返回
            # 缓存未命中：执行检索，并请求模型
            result=cached_rag_answer(req.question)

        else:
            # 绕过缓存，直接执行 RAG
            result=retrieve(req.question)
            result["cache_hit"] = False
        # 将结果字典返回，FastAPI 自动转换成 JSON
        # 两个分支正常完成后，都标记为没有降级
        result["fallback"]=False
        return result
    except Exception as error:
        # 保留错误信息，方便在服务终端排查
        print("RAG出错:",error)
        # 出错时，向客户端返回友好的提示
        return JSONResponse(
            content={
                "answer":"系统繁忙,请稍后重试,或致电图书馆总服务台6600。",
                "cache_hit":False,
                "fallback":True,
                "scores":[],
                "ans":""
            },
            status_code=200
        )
    
@app.post("/cache/clear")
def cache_clear():
    # 清空原来的缓存字典
    CACHE.clear()
    return {"cleared": True}