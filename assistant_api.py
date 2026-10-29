from fastapi import FastAPI,Request,HTTPException
from pydantic import BaseModel
from assistant_step1 import assistent
from audit_step1 import write_audit, read_audit
app=FastAPI()
class AssistentRequest(BaseModel):
    ticket_id:str
    text:str
    room:str
    service:str
    db: str = "cnki"  # 客户端不提供时，采用默认值
class AdminActionRequest(BaseModel):
    action:str

@app.post("/assistant")
def handle_assistant(req: AssistentRequest):
    # 将校验后的请求对象转换成 Python 字典
    ticket=req.model_dump()
    result=assistent(ticket)
    # FastAPI 将结果字典转换成 JSON 返回
    return result
@app.post("/admin/action")
def admin_action(req:AdminActionRequest,request:Request):
    action=req.action
    # 从请求头读取角色；没有提供时，默认为普通用户
    role=request.headers.get("X-User-Role","user")
    # 本次练习用 X-User 提供演示用户标识
    user=request.headers.get("X-User","anonymous")
    # 高权限操作要求管理员角色
    if action in ["restart","close_ticket"] and role !="admin":
        write_audit(user,action,{"allowed":False})
        raise HTTPException(status_code=403,detail="权限不足")
    result={
        "action":action,
        "allowed":True,
        "simulated":True
    }
    write_audit(user,action,result)
    return result
@app.get("/audit")
def get_audit(request:Request):
    role=request.headers.get("X-User-Role","user")
    if role!="admin":
        raise HTTPException(status_code=403,detail="权限不足")
    records=read_audit()
    return{
        "count":len(records),
        "records":records
    }
