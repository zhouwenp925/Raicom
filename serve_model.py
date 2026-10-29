import torch
from transformers import AutoModelForCausalLM,AutoTokenizer
from fastapi import FastAPI
from pydantic import BaseModel
model=AutoModelForCausalLM.from_pretrained(
    "./models/Qwen3-0.6B",
    torch_dtype=torch.float32
)
tokenizer=AutoTokenizer.from_pretrained("./models/Qwen3-0.6B")

def generate(messages,max_new_tokens=256):
    #把发来的信息进行整理
    prompt=tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False
    )
    #转向量
    inputs=tokenizer(prompt,return_tensors="pt")
    inputs_length=inputs["input_ids"].shape[1]
    #下面缩进的代码执行时，不记录用于反向传播的计算过程
    with torch.no_grad():
        outs=model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False   #关闭随机采样
        )
    
    # 离开代码块，恢复进入前的梯度设置
    answer_tokens=outs[0][inputs_length:]
    # 将编号转换成文字
    answer=tokenizer.decode(
        answer_tokens,
        skip_special_tokens=True
    )
    return answer
app=FastAPI()
# 声明请求体：客户端必须提供 messages
class ModelRequest(BaseModel):
    messages:list[dict[str,str]]

@app.post("/v1/chat/completions")
def chat(req:ModelRequest):
    # 调用本进程中的模型生成函数
    answer=generate(req.messages)
    # 约定返回格式，客户端按这个结构读取回答
    return {
        "choices":[
            {
                "message":{
                    "role": "assistant",
                    "content": answer
                }
            }
        ]
    }
