import json
from transformers import AutoTokenizer
# 加载分词器
tokenizer=AutoTokenizer.from_pretrained(
    "./models/Qwen3-0.6B"
)
def encode_sample(record):
    tokens=tokenizer.apply_chat_template(
        record["messages"],
        enable_thinking=False,
        tokenize=True,
        return_dict=True,
        add_generation_prompt=False
    )
    # 新增训练目标字段,用于比较
    # input_ids根据这些输入进行预测
    # labels用这些目标检查预测结果，计算训练误差.然后利用反向传播更新参数
    tokens["labels"]=tokens["input_ids"].copy()
    return tokens

with open("consultation_logs_demo.json","r",encoding="utf-8")as f:
    # 将 JSON 数组转换成 Python 列表
    data=json.load(f)
titile="test_"

vaild=[
    r for r in data
    if not r["session_id"].startswith(titile)# 判断会话编号是否以测试前缀开头
    and all(t["a"].strip() for t in r["turns"]) 
]
#print(type(vaild))
#print(vaild[0])
n_train=int(len(vaild)*0.9)
# 前9条作为训练集，剩余1条作为验证集
train_data=vaild[:n_train]
val_data=vaild[n_train:]
# 将一条会话记录转换成一个训练样本
def to_sample(record):
    messages=[]
    # 按顺序处理这条会话中的每轮问答
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
# 分别转换训练集和验证集中的每条记录
train_samples=[to_sample(r)for r in train_data]
val_samples=[to_sample(r)for r in val_data]
# 查看第一条转换结果
#print(train_samples[0])

train_tokens=[encode_sample(r)for r in train_samples]
val_tokens=[encode_sample(r)for r in val_samples]
# print("训练样本数：", len(train_tokens))
# print("验证样本数：", len(val_tokens))
# print(val_tokens)
# print(train_tokens[0])