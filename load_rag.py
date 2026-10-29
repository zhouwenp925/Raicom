import json
import faiss
from sentence_transformers import SentenceTransformer

emb=SentenceTransformer("/home/zwp/data/AI/models/bge-small-zh-v1.5")

save_dir="submission/m2/rag"

index=faiss.read_index(f'{save_dir}/policy.index')
# 读取对应的原文和来源
with open(f"{save_dir}/chunks.json","r",encoding="utf-8")as f:
    chunks=json.load(f)

# 检查恢复后的向量数量与切块数量
assert index.ntotal==len(chunks)

print("加载的向量数量：", index.ntotal)
print("加载的切块数量：", len(chunks))