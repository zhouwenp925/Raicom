from typing import Literal # Literal 限定字段只能取指定值
from pydantic import BaseModel
# 规定一个工具调用步骤的格式
class ToolStep(BaseModel):
    # 工具名只能是以下四个值之一
    tool:Literal[
        "shelf_query",
        "log_query",
        "kb_query",
        "resource_query"
    ]
    # 工具参数必须是字典，键和值都是字符串
    args:dict[str,str]

# 规定完整计划的格式
class WorkPlan(BaseModel):
    ticket_id:str
    intent:str
    # steps 必须是列表，每一项都符合 ToolStep 的格式
    steps:list[ToolStep]
