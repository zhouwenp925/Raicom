import faiss
import requests
from load_rag import chunks,index,emb

def generate(messages):
    # 将对话发送给独立运行的模型服务
    response=requests.post(
        # 告诉 requests：去访问这个模型接口
        "http://127.0.0.1:8700/v1/chat/completions",
        # 要发送的数据，会自动转换成 JSON
        json={"messages":messages},
        timeout=120
    )
    # HTTP 返回 4xx、5xx 时抛出异常
    response.raise_for_status()
    # 将响应 JSON 转换成 Python 字典
    data = response.json()
    # 按服务端刚才定义的返回结构，取出回答
    return data["choices"][0]["message"]["content"]

def retrieve(question,top_k=3):
    #先把问题给向量化
    que=emb.encode([question])
    #向量归一化
    faiss.normalize_L2(que)
    #将问题向量和库里的比对搜索
    scores,ids=index.search(que,top_k)
    # NumPy 数组转换成普通列表，方便返回 JSON
    scores_list=scores[0].tolist()
    #设置相关度
    threshold=0.5
    if threshold>scores[0][0]:
        return {
            "answer":"未检索出相关内容",
            "scores_list":scores_list
        }
    contexts=[chunks[i]["text"]for i in ids[0]]
    # 各部分拼接起来
    context="\n\n".join(contexts)
    # 将问题，资料，回答要求给LLM
    messages=[{
        "role":"system",
        "content":"""
你是图书馆政策问答助手。
请只根据提供的资料回答问题，保留问题所需的全部信息。
但是必须由你从资料里总结提取答案
如果没有时，回答：资料中没有相关信息。
"""
    },
    {
        "role":"user",
        "content":f"""
问题：{question}\n\n,资料:{context}
"""
    }
    ]
    answer=generate(messages)
    #ans=[]
    # # zip 将同一位置的分数和编号配成一对
    # for score, chunk_id in zip(scores[0], ids[0]):
    #     if score >= threshold:
    #         contexts.append(chunks[chunk_id]["text"])
    # if isinstance(ans,str):
    #     content={"content":ans}
    return {
        "answer":answer,
        "scores_list":scores_list,
        "ans":context
    }

if __name__ == "__main__":
    question="我的借阅卡丢了，我该怎么办？"
    print(retrieve(question))