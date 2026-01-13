import http
import json
import os
import smtplib
import ssl
import urllib
from email.message import EmailMessage
from langgraph.prebuilt import create_react_agent #封装好的智能体
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage,SystemMessage,AIMessage #提示词等需要
from langchain_core.tools import tool #封装好的使用的工具模块
load_dotenv()
model = ChatOpenAI(
     model="deepseek-ai/DeepSeek-V3.2",
    api_key=os.getenv("OPENAILD_API_KEY"),
    base_url=os.getenv("OPENAILD_BASE_URL"),
    temperature=0.7,
)
@tool
def get_weather(city_name:str):
    """这是一个查询天气的工具，city_name这个参数其实就是城市名称，需要依据这个名称查询实时的与最近一段时间的天气"""
    print(f"--- 正在调用 [get_weather] 工具 查询城市: {city_name} ---")
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
            # 兼容单日字典和多日列表
            weather_data_list = []
            if isinstance(res, list):
                weather_data_list = res
            elif isinstance(res, dict) and 'list' in res:
                weather_data_list = res['list']
            else:
                weather_data_list = [res]  # 降级处理：如果是单日对象，放入列表
            parsed_results = []
            for day in weather_data_list:
                # 预报接口和实时接口字段名往往不同
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
def send_email(
        to: list[str],
        subject: str,
        body: str,
        cc: list[str] = [] #抄送的一个列表
) -> str:
    """通过邮件API（SMTP）发送一封电子邮件，需要格式正确的邮件地址"""
    print(f"--- 正在调用 [send_email] 工具 ---")
    smtp_server = os.getenv("SMTP_SERVER")
    my_email = os.getenv("MY_EMAIL")
    my_email_password = os.getenv("MY_EMAIL_PASSWORD")

    if not all([smtp_server, my_email, my_email_password]):
        return "错误：SMTP服务器、邮箱地址或授权码未在 .env 文件中配置。"

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = my_email
    msg['To'] = ", ".join(to)
    if cc:
        msg['Cc'] = ", ".join(cc)
    msg.set_content(body)

    context = ssl.create_default_context()
    try:
        print(f"正在连接到 {smtp_server}...")
        with smtplib.SMTP_SSL(smtp_server, 465, context=context) as server:
            server.login(my_email, my_email_password)  #邮件操作
            print("登录成功，正在发送邮件...")
            server.send_message(msg)  #发送操作
            print("--- 邮件发送成功 ---")

        # 只要上面没有抛出“真正的”异常，就返回成功
        return f"邮件已成功发送到 {', '.join(to)} - 主题：{subject}"

    except Exception as e:
        # 检查这是否是那个“邮件已发送但连接断开”的特定错误
        if e.args == (-1, b'\x00\x00\x00'):
            print(f"--- 邮件已发送，但服务器返回了一个无效的关闭连接错误 {e}。我们将此视为成功。 ---")
            # 即使有这个错误，邮件也已发送，所以我们返回成功，防止代理重试！
            return f"邮件已成功发送到 {', '.join(to)} - 主题：{subject}"
        # 如果是其他真实错误（比如密码错误），则报告失败
        print(f"邮件发送失败: {e}")
        return f"邮件发送失败: {e}"

tools=[get_weather, send_email]
agent=create_react_agent(
    model=model,
    tools=tools,
)
system_instruction = (
      "你是一个智能助手。你拥有查询天气的工具 'get_weather'。也有发送邮件的工具'send_email'"
    "如果用户询问天气，你必须调用该工具，不要编造答案，也不要拒绝调用。"
    "如果用户也有让你发邮件的要求，你也要依据要求去发，不要拒绝调用。"
    "注意：现在 get_weather 工具可以返回未来几天的天气预报。如果用户询问特定日期的天气，请从返回的列表中筛选。"
)
messages = [
    SystemMessage(system_instruction),
]
while True:
    input3=input("user:")
    if input3 == "exit":
        break
    messages.append(HumanMessage(input3))
    response_content=[]
    final_response = ""
    events = agent.stream({"messages": messages}, stream_mode="values")
    for event in events:
        last_msg = event["messages"][-1]
        if isinstance(last_msg, AIMessage) and last_msg.content:
            final_response = last_msg.content
    print(f"\nAI: {final_response}")
    messages.append(AIMessage(content=final_response))
