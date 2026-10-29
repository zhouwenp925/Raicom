import requests,time
# 向同一个接口连续发送两次相同的问题
for n in range(1,3):
    # 记录请求开始的时间
    start=time.perf_counter()
    response=requests.post(
        "http://127.0.0.1:8100/rag",
        json={"question":"借阅卡补办需要什么材料？"},
        timeout=120
    )
    # HTTP 请求失败时抛出异常
    response.raise_for_status()
    data=response.json()
    # 时间差单位为秒，乘 1000 转换成毫秒
    elapsed_ms=(time.perf_counter()-start)*1000
    print(f"\n第 {n} 次请求")
    print("缓存命中：", data["cache_hit"])
    print("耗时（毫秒）：", round(elapsed_ms, 2))
    print("回答：", data["answer"])
    