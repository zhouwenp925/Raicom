from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# 导入你已经写好的模型生成函数
# 如果文件名不同，修改这里
from lora_verify import generate

app = FastAPI()


# 规定前端提交的数据格式
class ChatRequest(BaseModel):
    session_id: str  # 用来区分不同会话
    message: str

# 所有会话的历史
HISTORY = {}

# 每轮包括 user、assistant 两条消息
# 最多保存最近2轮完整对话
MAX_HISTORY_MESSAGES = 4

# 浏览器访问根路径，返回聊天页面
@app.get("/", response_class=HTMLResponse)
def index():
    return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>客服</title>
</head>
<body style="max-width:600px; margin:60px auto;">

    <input id="question" placeholder="请输入问题" style="width:75%;">
    <button id="send" onclick="chat()">发送</button>

    <pre id="answer" style="white-space:pre-wrap;"></pre>

    <script>
        // 页面打开时生成一次，本页面后续请求一直使用这个编号
        const sessionId = crypto.randomUUID();
        async function chat() {
            const input = document.getElementById("question");
            const button = document.getElementById("send");
            const output = document.getElementById("answer");
            const message = input.value.trim();

            if (!message) return;

            button.disabled = true;
            output.textContent = "正在回答……";

            try {
                const response = await fetch("/chat", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({
                        session_id: sessionId,
                        message: message
                    })
                });

                if (!response.ok) throw new Error("服务器处理失败");

                const data = await response.json();
                output.textContent = data.answer;
            } catch (error) {
                output.textContent = "请求失败：" + error.message;
            } finally {
                button.disabled = false;
            }
        }
    </script>
</body>
</html>
"""


# 接收问题，调用已经加载 LoRA 的模型
@app.post("/chat")
def chat(req: ChatRequest):
    sid = req.session_id
    # 取出当前会话的历史；新会话暂时使用空列表
    history=HISTORY.get(sid,[])
    history.append({"role": "user", "content": req.message})
    messages = [
    {
        "role": "system",
        "content": (
            "你是客服。请针对用户当前的话回答。"
            "用户问候或介绍自己时，自然回应，不主动讲订单政策。"
            "用户咨询商城业务时，再回答相关问题。"
            "不要编造订单状态，也不要声称已完成任何操作。"
        )
        }
    ]+history
    answer = generate(messages)
    history.append({"role": "assistant", "content": answer})
    HISTORY[sid]=history[-MAX_HISTORY_MESSAGES:]
    return {"answer": answer}