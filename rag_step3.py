import faiss
from rag_step2 import emb,chunks,index
from serve_model import generate

def rag_answer(question,top_k=3):
    que=emb.encode([question])
    # 问题向量归一化
    faiss.normalize_L2(que)
    score,ids=index.search(que,top_k)
    print("socre:",score)
    print("编号：",ids)
    scores=[round(float(s),4)for s in score[0]]
    # 按样题设置相似度阈值
    threshold = 0.5
    best_score=score[0][0]
    print("Best:",best_score)
    if best_score<threshold:
        return {
            "answer":"未检索出相关内容",
            "scores":scores
        }
    #因为只提交了一个问题，而 ids 的每一行对应一个问题
    contexts=[chunks[i]["text"]for i in ids[0]]
    # 用空行连接，组成一个资料字符串
    context="\n\n".join(contexts)
    print(context)
    # 将回答要求、资料和问题整理成聊天消息
    messages = [
        {
            "role": "system",
            "content": (
                "你是图书馆政策问答助手。"
                "请只根据提供的资料回答问题，保留问题所需的全部信息。"
                "资料没有答案时，回答：资料中没有相关信息。"
            )
        },
        {
            "role": "user",
            "content": f"资料：\n{context}\n\n问题：{question}"
        }
    ]
    answer=generate(messages)
    return {
        "answer":answer,
        "scores":scores
    }

# 直接运行本文件时执行；被其他文件导入时跳过测试
if __name__ == "__main__":
    result = rag_answer("借阅卡补办需要什么材料？")
    print(result["answer"])
