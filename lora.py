from transformers import AutoTokenizer
import json,random
tokenizer=AutoTokenizer.from_pretrained("./models/Qwen3-0.6B")

def to_sample(record):
    messages=[]
    for turn in record["turns"]:
        # 加入用户问题
        messages.append({
            "role":"user",
            "content":turn["q"]
        }
        )
        # 加入回答
        messages.append({
            "role":"assistant",
            "content":turn["a"]
        })
    return {"messages":messages}

def to_encode(record):
    tokens=tokenizer.apply_chat_template(
        record["messages"],
        tokenize=True,
        add_generation_prompt=False,
        enable_thinking=False,
        return_dict=True
    )
    tokens["labels"]=tokens["input_ids"].copy()
    return tokens
#打开文件提取内容
with open("./docs/customer_dialogues_curated_1500.json","r",encoding="utf-8")as f:
    #将json转换成python
    data=json.load(f)

# 先打乱完整会话，再划分
# 固定种子，让重复运行时划分结果一致
random.Random(42).shuffle(data)
n_train=int(0.9*len(data))
train_data=data[:n_train]
val_data=data[n_train:]
train_sample=[to_sample(r)for r in train_data]
val_sample=[to_sample(r)for r in val_data]
train_tokens=[to_encode(r)for r in train_sample]
val_tokens=[to_encode(r)for r in val_sample]
# print(len(train_tokens))