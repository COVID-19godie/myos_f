import time

def analyze_text_with_ai(text):
    """
    模拟 AI 分析：输入描述，返回标签
    """
    # 真实场景：这里调用 LangChain 或 OpenAI API
    # response = openai.Completion.create(...)

    # 模拟耗时
    time.sleep(1) 

    # 简单的关键词提取逻辑
    tags = []
    if "物理" in text or "力" in text:
        tags.append("#物理")
    if "公式" in text:
        tags.append("#公式推导")
    if "考试" in text or "试卷" in text:
        tags.append("#期末复习")

    if not tags:
        tags.append("#AI推荐")

    return ",".join(tags)

# 保存结果到资源的函数（供视图调用）
def save_ai_results(resource, tags):
    resource.ai_tags = tags
    # 模拟向量数据（实际应该是数值数组的字符串表示）
    resource.embedding_text = f"vector_for_{tags.replace(',', '_')}"
    resource.save()
