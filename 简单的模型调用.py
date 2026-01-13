import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

load_dotenv()

# 初始化模型
model = ChatOpenAI(
    model="deepseek-ai/DeepSeek-V3.2",
    api_key=os.getenv("OPENAILD_API_KEY"),
    base_url=os.getenv("OPENAILD_BASE_URL"),
    temperature=0.7,
)

messages = [
    SystemMessage(content="你是一个办公小助手"),
]

print("输入exit结束")

while True:
    input3 = input("user:")
    if input3 == "exit":
        break
    # 添加用户消息到历史
    messages.append(HumanMessage(content=input3))
    response_chunks = []
    print("AI: ", end="")
    try:
        for chunk in model.stream(messages):
            content = chunk.content
            print(content, end="", flush=True)
            response_chunks.append(content)
        print("\n")
        full_response = "".join(response_chunks)
        messages.append(AIMessage(content=full_response))
    except Exception as e:
        print(f"\n发生错误: {e}")
        messages.pop()