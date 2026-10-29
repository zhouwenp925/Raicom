import os,json
# 使用之前划分出来的验证样本
from clean_data import val_samples
# 使用刚才加载了 LoRA 的模型和生成函数
from lora_infer import model, generate
results=[]
for sample in val_samples:
    # 最后一条是参考回答，单独取出来用于对照
    reference=sample["messages"][-1]["content"]
    # 其余消息作为输入，不能把待验证的答案也传给模型
    messages=sample["messages"][:-1]
    # 临时停用 LoRA，取得原模型回答
    with model.disable_adapter():
        base_answers=generate(messages)
    # 恢复使用 LoRA，取得微调后的回答
    lora_answers=generate(messages)
    # 保存这一条样本的对比结果
    record = {
        "question": messages[-1]["content"],
        "reference": reference,
        "base_answer": base_answers,
        "lora_answer": lora_answers
    }
    results.append(record)
    # 在终端查看
    print(json.dumps(record,ensure_ascii=False,indent=2))
# 保存全部对比结果
os.makedirs("submission/m1",exist_ok=True)
with open(
    "submission/m1/lora_compare_demo.json",
    "w",
    encoding="utf-8"
)as f:
    json.dump(results,f,ensure_ascii=False,indent=2)
print("验证样本数：", len(results))
print("对比结果已保存")