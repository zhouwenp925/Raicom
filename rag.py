from sentence_transformers import SentenceTransformer
import faiss
emb=SentenceTransformer("./models/bge-small-zh-v1.5")
# 需要切分的文档
files = [
    "docs/borrow_demo.md",
    "docs/opening_demo.md",
    "docs/resource_demo.md"
]
def split_doc(text,max_length=500):
    #\n\n代表按空行分出自然段落
    blocks=text.split("\n\n")
    chunks=[]
    for block in blocks:
        block=block.strip()
        if not block:
            continue
        for start in range(0,len(block),max_length):
            chunks.append(block[start:start+max_length])
    return chunks

chunks=[]
for file in files:
    with open(file,"r",encoding="utf-8")as f:
        text=f.read()
        parts=split_doc(text)
        for part in parts:
            chunks.append({
                "text":part,
                "source":file
            })
texts=[chunk["text"]for chunk in chunks]
vecs=emb.encode(texts)
faiss.normalize_L2(vecs)
# 创建内积检索索引，每条向量必须有 512 个数字
index=faiss.IndexFlatIP(512)
# 将所有切块的向量加入索引
index.add(vecs)
print("形状是：",vecs.shape)
print("total:",index.ntotal)
