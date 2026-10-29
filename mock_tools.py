from fastapi import FastAPI,Query

app = FastAPI()
# 接收 GET 请求，通过查询参数取得房间编号
@app.get("/tools/shelf_query")
def shelf_query(room:str):
    return {
        "room":room,
        "status":"模拟：电脑网络连接异常"
    }

# 查询服务日志，返回固定的模拟数据
@app.get("/tools/log_query")
def log_query(service:str):
    return {
        "service":service,
        "log":"模拟：出现设备通信超时记录。"
    }
@app.get("/tools/resource_query")
#不传 db 时使用默认值，传了就使用客户端提供的值。
def resource_query(db:str=Query("cnki")):
    return {
        "db":db,
        "concurrent":128,
        "limit":120,
        "status":"已满"
    }
@app.get("/tools/kb_query")
def kb_query(q:str =Query("借阅卡办理")):
    return {
        "q":q,
        "result": "模拟：补办借阅卡需要携带学生证和一张近期证件照片。"
    }