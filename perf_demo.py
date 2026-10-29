import os,json,requests,time

BASE_URL="http://127.0.0.1:8100"
QUESTION="借阅卡补办需要什么材料？"
N=3
def measure(use_cache):
    times=[]      # 保存每次请求的耗时
    cache_hits=[]    # 保存每次请求的缓存命中情况
    
    for _ in range(N):
        start=time.perf_counter()
        response=requests.post(
            f"{BASE_URL}/rag",
            json={
                "question":QUESTION,
                "use_cache":use_cache
            },
            timeout=120
        )
        response.raise_for_status()
        data=response.json()
        # 将本次耗时转换成毫秒
        elapsed_ms=(time.perf_counter()-start)*1000
        times.append(elapsed_ms)
        cache_hits.append(data["cache_hit"])
    # 总耗时除以次数，得到平均耗时
    average=sum(times)/len(times)
    return round(average,2),cache_hits
# 第一组：关闭缓存，每次重新处理问题
avg_ms_off,off_hits=measure(False)
# 第二组开始前，清空缓存，保证第一次未命中
response=requests.post(f"{BASE_URL}/cache/clear",timeout=10)
response.raise_for_status()
# 第二组：开启缓存
avg_ms_on,on_hits=measure(True)
result={
    "avg_ms_off":avg_ms_off,
    "avg_ms_on":avg_ms_on,
    "n":N
}
print("关闭缓存组：", off_hits)
print("开启缓存组：", on_hits)
print(json.dumps(result, ensure_ascii=False, indent=2))
# 保存本次实际测量结果
os.makedirs("submission/m2",exist_ok=True)
with open(
    "submission/m2/perf_compare_demo.json",
    "w",
    encoding="utf-8"
)as f:
    json.dump(result,f,ensure_ascii=False,indent=2)
