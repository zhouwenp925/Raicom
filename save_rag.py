import json,faiss,os
# 导入已经建立好的索引，以及对应的原文切块
from rag_step2 import chunks,index
# 创建保存目录
save_dir="submission/m2/rag"
# 创建目录；已经存在时不报错
os.makedirs(save_dir, exist_ok=True)
# 保存前检查：向量条数必须等于切块数量
assert index.ntotal==len(chunks)
# 保存 FAISS 索引，文件名按题目使用 policy.index
faiss.write_index(index,f'{save_dir}/policy.index')
# 将文字和来源保存成 JSON
with open(f'{save_dir}/chunks.json',"w",encoding="utf-8")as f:
    json.dump(chunks,f,ensure_ascii=False,indent=2)

print("索引和切块已保存")