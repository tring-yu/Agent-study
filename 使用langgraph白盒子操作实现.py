import http
import json
import os
import smtplib
import ssl
import urllib
from email.message import EmailMessage
from typing import Annotated,Literal,TypedDict
#langgraph手动构建的核心组件
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode,tools_condition
from langgraph.checkpoint.memory import MemorySaver
#langchain的相关包
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage,SystemMessage,AIMessage,BaseMessage
from langchain_core.tools import tool
load_dotenv()
model=ChatOpenAI(
    model="deepseek-ai/DeepSeek-V3.2",
    api_key=os.getenv("OPENAILD_API_KEY"),
    base_url=os.getenv("OPENAILD_BASE_URL"),
    temperature=0.7,
)
#定义工具
@tool
def get_weather(city_name: str):
    """这是一个查询天气的工具，city_name这个参数其实就是城市名称，需要依据这个名称查询实时的天气"""
    print(f"--- [Node: Tools] 正在调用 get_weather 查询城市: {city_name} ---")

    conn = http.client.HTTPSConnection('apis.tianapi.com')
    api_key = os.getenv("tianjuapi_key")
    if not api_key:
        return "错误：未在 .env 中配置 tianjuapi_key"

    params = urllib.parse.urlencode({'key': api_key, 'city': city_name, 'type': '7'})
    headers = {'Content-type': 'application/x-www-form-urlencoded'}

    try:
        conn.request('POST', '/tianqi/index', params, headers)
        tianapi = conn.getresponse()
        result = tianapi.read()
        data = result.decode('utf-8')
        dict_data = json.loads(data)

        if dict_data.get("code") == 200:
            res = dict_data["result"]
            weather_data_list = []
            if isinstance(res, list):
                weather_data_list = res
            elif isinstance(res, dict) and 'list' in res:
                weather_data_list = res['list']
            else:
                weather_data_list = [res]
            parsed_results = []
            for day in weather_data_list:
                parsed_results.append({
                    "日期": day.get("date", "未知"),
                    "天气": day.get("weather", day.get("tips", "未知")),
                    "温度": f"{day.get('lowest', '')}~{day.get('highest', '')}",
                    "风向": day.get("wind", "未知"),
                    "风力": day.get("windsc", day.get("sc", "未知")),
                })
            return parsed_results
        else:
            return f"查询失败: {dict_data.get('msg', '未知错误')}"
    except Exception as e:
        return f"接口调用出错: {e}"
@tool
def send_email(to: list[str], subject: str, body: str, cc: list[str] = []) -> str:
    """通过邮件API（SMTP）发送一封电子邮件，需要格式正确的邮件地址"""
    print(f"--- [Node: Tools] 正在调用 send_email ---")

    smtp_server = os.getenv("SMTP_SERVER")
    my_email = os.getenv("MY_EMAIL")
    my_email_password = os.getenv("MY_EMAIL_PASSWORD")

    if not all([smtp_server, my_email, my_email_password]):
        return "错误：环境配置缺失"

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = my_email
    msg['To'] = ", ".join(to)
    if cc: msg['Cc'] = ", ".join(cc)
    msg.set_content(body)

    context = ssl.create_default_context()
    try:
        print(f"正在连接到 {smtp_server}...")
        with smtplib.SMTP_SSL(smtp_server, 465, context=context) as server:
            server.login(my_email, my_email_password)
            server.send_message(msg)
            print("--- 邮件发送成功 ---")
        return f"邮件已成功发送到 {', '.join(to)} - 主题：{subject}"
    except Exception as e:
        if e.args == (-1, b'\x00\x00\x00'):
            return f"邮件已成功发送到 {', '.join(to)} - 主题：{subject}"
        return f"邮件发送失败: {e}"
tools=[get_weather, send_email]
#这个就是我们说的state
class AgentState(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]
#定义节点
def call_model(state: AgentState):
    print("模型正在思考")
    messages=state["messages"]
    model_with_tools=model.bind_tools(tools)
    response=model_with_tools.invoke(messages)
    return {"messages": [response]}
tool_node=ToolNode(tools) #这一步至关重要，讲两个工具包装成一个节点
#定义图
workflow=StateGraph(AgentState)
workflow.add_node("agent",call_model)
workflow.add_node("tools",tool_node)
workflow.add_edge(START,"agent")
workflow.add_conditional_edges("agent",tools_condition)
workflow.add_edge("tools","agent")
checkpointer=MemorySaver
app=workflow.compile(checkpointer=checkpointer)
#运行主循环
system_instruction = (
    "你是一个智能助手。你拥有查询天气的工具 'get_weather' 和发送邮件的工具 'send_email'。"
    "如果用户询问天气，你必须调用该工具。"
    "注意：get_weather 工具可以返回未来几天的天气预报。如果用户询问特定日期的天气，请从返回的列表中筛选。"
)
thread_id = "demo_thread_1"
config = {"configurable": {"thread_id": thread_id}}
is_first_turn = True
while True:
    try:
        user_input = input("User: ")
    except EOFError:
        break
    if user_input.lower() in ["exit", "quit"]:
        break

    # 准备输入消息
    input_messages = [HumanMessage(content=user_input)]

    # 第一轮，把 SystemPrompt 带上
    # 之后 Checkpointer 会记住它，不需要重复发
    if is_first_turn:
        input_messages.insert(0, SystemMessage(content=system_instruction))
        is_first_turn = False
    print("AI thinking...", end="", flush=True)
    # checkpointer 会自动读取历史，把 input_messages 追加上去
    events = app.stream(
        {"messages": input_messages},
        config=config,
        stream_mode="values"
    )
    final_response = ""
    for event in events:
        last_msg = event["messages"][-1]
        if isinstance(last_msg, AIMessage) and last_msg.content:
            final_response = last_msg.content
    print(f"\nAI: {final_response}")
