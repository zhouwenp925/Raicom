from transformers import AutoModelForCausalLM,AutoTokenizer
import torch
from peft import PeftModel
# 加载原模型的结构和权重
base_model=AutoModelForCausalLM.from_pretrained(
    "./models/Qwen3-0.6B",
    torch_dtype=torch.float32
)
# 在原模型上加载已经训练好的 LoRA
model=PeftModel.from_pretrained(
    base_model,
    "./submission/m4/finetune"
)
tokenizer=AutoTokenizer.from_pretrained(
    "./models/Qwen3-0.6B"
)
# 关闭 Dropout 等训练时的行为
model.eval()
print("原模型和 LoRA 加载成功！")

def generate(messages):
    prompt=tokenizer.apply_chat_template(
        messages,
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
    outputs_tokens=outputs[0][input_length:]
    answers=tokenizer.decode(
        outputs_tokens,
        skip_special_tokens=True
    )
    return answers

if __name__=="__main__":
    messages=[
        {
            "role":"user","content":"我没有授权你操作，解释步骤可以吗？"
        }
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