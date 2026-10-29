import torch
# Trainer：负责训练和验证
# DataCollatorForSeq2Seq：将多条样本整理成一批
from transformers import AutoModelForCausalLM,Trainer,DataCollatorForSeq2Seq
from peft import LoraConfig,get_peft_model
# TrainingArguments 用来集中保存训练设置
from transformers import TrainingArguments
#从其它文件导入
from clean_data import tokenizer,train_tokens,val_tokens
# Dataset：管理训练样本,保存样本，支持按编号取样
from datasets import Dataset

# 1. 加载已经下载好的模型
model=AutoModelForCausalLM.from_pretrained(
    "./models/Qwen3-0.6B",
    torch_dtype=torch.float32
)
# 2. 定义 LoRA 配置：规定新增参数的规模和位置
lora_cfg=LoraConfig(
    # 任务是根据前面的内容预测后面的 token
    task_type="CAUSAL_LM",
    # 低秩矩阵的秩，控制新增参数的规模
    r=8,
    # 控制 LoRA 权重改动的缩放
    lora_alpha=16,
    # 在模型中这些名字对应的层上加入 LoRA
    target_modules=["q_proj","k_proj","v_proj","o_proj"],
    # 训练时的 Dropout 比例
    lora_dropout=0.05
)
# 3. 按配置给模型加入 LoRA，并设置哪些参数参与训练
model=get_peft_model(model,lora_cfg)
# 4. 查看可训练参数数量和占比
model.print_trainable_parameters()

training_args=TrainingArguments(
    # 训练时保存检查点等文件的目录
    output_dir="submission/m1/finetune",
    # 将整个训练集学习一遍
    num_train_epochs=1,
    # 每个设备一次处理 2 条训练样本
    per_device_train_batch_size=2,
    # 学习率：控制参数更新的步幅
    learning_rate=2e-4,
    # 每完成 10 个参数更新步骤，记录一次训练日志
    logging_steps=10,
    # 指定使用 CPU 训练
    use_cpu=True
)
print("训练参数准备完成")
# print("训练样本数：", len(train_tokens))
# print("验证样本数：", len(val_tokens))
# print("样本字段：", list(train_tokens[0].keys()))
# from_list() 接收你现有的“字典组成的列表”。这里没有重新分词，只是换成数据集对象
train_dataset=Dataset.from_list(train_tokens)
val_dataset=Dataset.from_list(val_tokens)

# 创建批次整理器,补齐一批样本的长度，并转换成张量
data_collator=DataCollatorForSeq2Seq(
    # 使用分词器中规定的补齐编号
    tokenizer=tokenizer,
    # labels 中补齐的位置不参与损失计算
    label_pad_token_id=-100,
    # 将整理后的数据转换成 PyTorch 张量
    return_tensors="pt"
)
# 创建训练器
# 本地练习：关闭外部实验记录平台
training_args.report_to=[]
# 明确告诉训练器：训练目标字段叫 labels
training_args.label_names=["labels"]
trainer=Trainer(
    model=model,# 已经加入 LoRA 的模型
    args=training_args,# 配置好的训练参数
    train_dataset=train_dataset,# 用于更新参数的训练集
    eval_dataset=val_dataset,# 用于检查效果的验证集
    data_collator=data_collator,# 每批数据的整理方式
    processing_class=tokenizer # 使用的分词器，保存时一并保存
)
# 先检查训练前的表现，不更新参数
before=trainer.evaluate()
print("训练前的损失：",before["eval_loss"])
# 真正开始训练：计算损失、反向传播、更新 LoRA 参数
trainer.train()
# 再使用同一份验证集检查训练后的表现
after=trainer.evaluate()
print("训练后的损失：",after["eval_loss"])
# 保存训练后的 LoRA 结果和分词器
trainer.save_model(training_args.output_dir)
print("训练结果已经保存到：",training_args.output_dir)