# 给出的报修关键词
REPAIR_KEYWORDS = ["报修", "故障", "空调", "门禁", "网络"]

def route(question):
    # 只要有一个关键词出现在问题中，就走报修流程
    if any(k in question for k in REPAIR_KEYWORDS):
        return "repair_agent"
    # 所有关键词都没有匹配，走咨询流程
    return "visitor_agent"

if __name__=="__main__":
    questions = [
        "R305 的空调停机了",
        "借阅卡补办需要什么材料？",
        "查询知网当前并发是否已满。"
    ]
    for question in questions:
        print(question,":",route(questions))