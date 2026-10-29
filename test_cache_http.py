import requests
import time

# 先清空服务端缓存，保证第一次请求不会命中
response=requests.post(
        # 告诉访问地址
        "http://127.0.0.1:8100/cache/clear",
        timeout=10
    )
response.raise_for_status()
for i in range(2):
    #记录开始的时间
    start=time.perf_counter()
    response=requests.post(
        # 告诉访问地址
        "http://127.0.0.1:8100/rag",
        json={"question":"借阅卡补办需要什么材料？"},
        timeout=120
    )
    response.raise_for_status()
    data=response.json()
    elapsed_ms=(time.perf_counter()-start)*1000
    print("第", i + 1, "次")
    print("命中缓存：", data["cache_hit"])
    print("是否降级：", data["fallback"])
    print("耗时：", round(elapsed_ms, 2), "毫秒")
    print("回答：", data["answer"])
