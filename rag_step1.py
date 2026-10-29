# 需要切分的文档
files = [
    "docs/borrow_demo.md",
    "docs/opening_demo.md",
    "docs/resource_demo.md"
]
# text 是文档内容，max_len 默认是每块最多 500 个字符
def split_doc(text,max_len=500):
    # 两个换行符表示空行，按空行分出自然段落
    blocks=text.split("\n\n")
    chunks=[]
    for block in blocks:
        #去除前后空白
        block=block.strip()
        #去除空
        if not block:
            continue
        for start in range(0,len(block),max_len):
            chunks.append(block[start:start+max_len])
    return chunks

chunks=[]

for filename in files:
    with open(filename,"r",encoding="utf-8")as f:
        text=f.read()
        parts=split_doc(text)
        for part in parts:
            chunks.append({
                "text":part,
                "source":filename
            })

for part in chunks:
    print(part)