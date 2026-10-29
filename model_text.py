import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# 1. 加载分词器和模型
MODEL_PATH = "./models/Qwen3-0.6B"

print("正在加载分词器……")
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_PATH,
    local_files_only=True
)

print("正在加载模型……")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.float32,
    local_files_only=True
)

# 切换为推理模式
model.eval()

# 2. 准备用户消息
messages = [
    {"role": "user", "content": "你好，请用一句话介绍自己。"}
]

# 3. 将聊天记录整理为Qwen需要的文字格式
prompt = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True,
    enable_thinking=False
)

# 4. 将文字转换成模型需要的数字张量
inputs = tokenizer(prompt, return_tensors="pt")

# 5. 生成回答，不记录梯度
print("正在生成回答……")
with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=256,
        do_sample=False
    )

# 6. 切掉原输入，只保留新生成的token
input_length = inputs["input_ids"].shape[1]
answer_tokens = outputs[0][input_length:]

# 7. 将回答的token转换回文字
answer = tokenizer.decode(
    answer_tokens,
    skip_special_tokens=True
)

print("模型回答：")
print(answer)
