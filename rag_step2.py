from sentence_transformers import SentenceTransformer
import faiss
# 导入上一步整理好的切块
from rag_step1 import chunks
emb=SentenceTransformer(
    "/home/zwp/data/AI/models/bge-small-zh-v1.5"
)

# 从每个字典中取出文字，组成字符串列表
texts=[chunk["text"]for chunk in chunks]
vecs=emb.encode(texts)

#将每一个向量归一化，直接修改vecs
faiss.normalize_L2(vecs)
# 创建内积检索索引，每条向量必须有 512 个数字
index=faiss.IndexFlatIP(512)
# 将所有切块的向量加入索引
index.add(vecs)

print("形状是：",vecs.shape)
print("索引中的向量数量：", index.ntotal)