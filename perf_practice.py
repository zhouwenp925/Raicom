import time,json,requests

N=3
question="借阅卡补办需要什么材料？"
def measure(use_cache):
    duration=[]
    hits=[]
    for _ in range(N):
        start=time.perf_counter()
        response=requests.post(
            "http://127.0.0.1:8100/rag",
            json={"question":question,"use_cache":use_cache},
            timeout=120
        )
        response.raise_for_status()
        data=response.json()
        # 如果降级服务
        if data["fallback"]:
            #raise：抛出异常。RuntimeError：异常类型。
            raise RuntimeError("出现降级回复，请恢复模型服务后重测")
        duration.append((time.perf_counter()-start)*1000)
        hits.append(data["cache_hit"])
    average=sum(duration)/len(duration)
    return round(average,3),hits

# 第一组：每次都绕过缓存
off_ms, off_hits = measure(False)

# 第二组开始前，只清空一次缓存
response = requests.post(
    "http://127.0.0.1:8100/cache/clear",
    timeout=10
)
response.raise_for_status()

# 第二组：允许使用缓存
on_ms, on_hits = measure(True)
result = {
    "avg_ms_off": off_ms,
    "avg_ms_on": on_ms,
    "n": N,
    "off_cache_hits": off_hits,
    "on_cache_hits": on_hits
}
print(json.dumps(result, ensure_ascii=False, indent=2))