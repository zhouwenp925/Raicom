# requests 用来向已经运行的服务发送 HTTP 请求
import requests
while True:
    # 读取键盘输入，得到字符串
    text = input("请输入问题（输入 q 退出）：")
    if text=="q":
        break
    # 向 app.py 的 POST /chat 接口提交数据
    response=requests.post(
        "http://127.0.0.1:8100/chat",
        json={
            "session_id":"cli",
            "text":text
        }
    )
    data=response.json()
    # 读取服务器返回的 reply 字段
    print("助手：",data["reply"])
    print("完整HTTP响应:",response.status_code)
    print(data)