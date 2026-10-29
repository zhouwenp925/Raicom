import faiss,torch
from transformers import AutoModelForCausalLM,AutoTokenizer
from sentence_transformers import SentenceTransformer
from rag import chunks,index
model=AutoModelForCausalLM.from_pretrained(
    "./models/Qwen3-0.6B",
    torch_dtype=torch.float32
)
tokenizer=AutoTokenizer.from_pretrained("./models/Qwen3-0.6B")
emb=SentenceTransformer("./models/bge-small-zh-v1.5")
def generate(messages,max_new_tokens=256):
    #把发来的信息进行整理
    prompt=tokenizer.apply_chat_template(
        messages,#提示词
        tokenize=False,
        add_generate_prompt=True,
        enable_thinking=False
    )
    #转向量
    inputs=tokenizer(prompt,return_tensors="pt")
    inputs_length=inputs["input_ids"].shape[1]
    #print(inputs)
    #下面缩进的代码执行时，不记录用于反向传播的计算过程
    with torch.no_grad():
        outs=model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False
        )
    #print(outs[0][inputs_length:])
    answer_tokens=outs[0][inputs_length:]
    answer=tokenizer.decode(
        answer_tokens,
        skip_special_tokens=True
    )
    print(answer)
def rag(question,top_k=3):
    #将问题转向量
    que=emb.encode([question])
    faiss.normalize_L2(que) #归一化
    score,ids=index.search(que,top_k)
    print("socre:",score)
    print("编号：",ids)
    best_score=score[0][0]
    if best_score<0.5:
        return {
            "answer":"没有检索到相关知识"
        }
    text=[chunks[i]["text"]for i in ids[0]]
    messages=[
        {
            "role":"system",
            "content":"你是一名图书管理员，只能根据信息来回答问题。"
        },
        {
            "role":"user",
            "content":f"问题:{question},资料:{text}"
        }
    ]
    answer=generate(messages)
    return answer


question="我想看电子资源，但是不知道咋看"
print(rag(question))