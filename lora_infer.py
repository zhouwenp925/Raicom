import torch
from transformers import AutoModelForCausalLM,AutoTokenizer
from peft import PeftModel
#模型所在目录
MODEL_PATH="./models/Qwen3-0.6B"
# 之前训练并保存的 LoRA 所在目录
LORE_PATH="./submission/m1/finetune"
# 加载原模型的结构和权重
base_model=AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.float32
)
# 在原模型上加载已经训练好的 LoRA
model=PeftModel.from_pretrained(
    base_model,
    LORE_PATH,
    # 本次用于推理，冻结适配器参数
    is_trainable=False
)
# 加载原来的分词器
tokenizer=AutoTokenizer.from_pretrained(
    MODEL_PATH
)
# 关闭 Dropout 等训练时的行为
model.eval()
print("原模型和 LoRA 加载成功！")

# 查看当前有多少参数允许参与训练
model.print_trainable_parameters()
def generate(question):
    # 将对话整理成模型要求的提示词
    prompt=tokenizer.apply_chat_template(
        question,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False
    )
    # 提示词转换成张量；模板已经包含特殊标记
    inputs=tokenizer(
        prompt,
        return_tensors="pt",
        add_special_tokens=False
    )
    # 不记录用于反向传播的计算过程，减少推理内存开销
    with torch.no_grad():
        outputs=model.generate(
            **inputs,
            max_new_tokens=256,
            do_sample=False
        )
    # 切掉输入部分，只解码新生成的内容
    input_length=inputs["input_ids"].shape[1]
    answer_tokens=outputs[0][input_length:]
    return tokenizer.decode(
        answer_tokens,
        skip_special_tokens=True
    )
if __name__=="__main__":
    messages=[
        {"role":"user","content":"借阅卡补办需要什么材料？"}
    ]
    # 在这个代码块里，临时停用 LoRA
    with model.disable_adapter():
        before=generate(messages)
    # 离开上面的代码块后，LoRA 自动恢复启用
    after=generate(messages)
    print("原模型回答：")
    print(before)

    print("\n加载 LoRA 后的回答：")
    print(after)