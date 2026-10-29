from openai import OpenAI
def generate(question):
    client=OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama"  
        )
    response=client.chat.completions.create(
        model="qwen3:0.6b",
        messages=[
        {
            "role":"system","content":"你叫08,你是一位天才聊天员"
        },
        {
            "role":"user","content":question
        }
        ]
    )
    return response.choices[0].message.content
question="你好"
print(generate(question))