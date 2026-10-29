import hashlib # 生成问题的摘要，用作缓存键
import time #获取当前时间
# 导入现在写的 retrieve，起名为 rag_answer
# 这样原来的缓存函数内部代码可以继续使用
from retrieve_practice import retrieve as rag_answer

# 每个缓存键对应：(保存时间, 回答结果)
CACHE={}
CACHE_TTL=60
def cached_rag_answer(question):
    # 根据问题生成缓存键
    # 将问题转成字节，再生成字符串形式的 MD5 摘要
    key=hashlib.md5(question.encode("utf-8")).hexdigest()
    # 必须同时满足：缓存存在，并且尚未过期
    if key in CACHE and time.time()-CACHE[key][0]<CACHE_TTL:
        print("命中缓存")
        print("缓存结果类型：", type(CACHE[key][1]))
        response=CACHE[key][1].copy()
        #print(CACHE[key])
        # 标记：本次回答来自缓存，定义：给字典的某个键赋值时，如果这个键不存在，就会直接新增，不需要提前声明
        response["cache_hit"] = True
        return response
    # 没有有效缓存时，调用原来的 RAG 函数
    results=rag_answer(question)
    # 如果结果是字符串，就包装成字典
    if isinstance(results,str):
        results={"answers":results}
    # 保存
    CACHE[key]=(time.time(),results)
    print("写入缓存")
    print("缓存结果类型：", type(CACHE[key][1]))
    response=results.copy()
    response["cache_hit"] = False
    
    return response

if __name__ =="__main__":
    # 在同一个进程里连续问两次
    question = "借阅卡补办需要什么材料？"
    print(cached_rag_answer(question))
    print(cached_rag_answer(question))