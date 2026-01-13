🤖 从模型到智能体：AI Agent 核心讲义与实操指南

课程说明：本资料包含两部分内容：

核心讲义：理解智能体（Agent）的概念、原理与架构。

实操指南：教你如何配置 Python 环境并运行本次课程的代码。

第一部分：核心讲义 📖

1. 什么是智能体 (Agent)？

1.1 核心定义

智能体（Agent） 可以看作是“能够感知环境、进行思考、并采取行动来实现目标的数字生命体”。

用一个形象的进化史来比喻：

大模型 (LLM) = “活字典”（被关在小黑屋里的天才，懂得多但干不了活）。

智能体 (Agent) = “数字员工”（有手有脚、能独立干活的超级实习生）。

1.2 为什么要学习智能体？

我们已经可以调用模型了，为什么还要搞智能体？

普通模型调用 (Linear)：

流程是线性的：用户提问 -> 模型识别工具 -> 只有一次调用 -> 返回结果。

痛点：如果问题很复杂（例如：“先查明天天气，如果是雨天就发邮件提醒我”），你需要写大量的 if-else 硬代码来串联逻辑。

智能体 (Loop)：

是一个循环系统 (Loop)。

它具备自主规划能力：感知 -> 思考 -> 行动 -> 观察结果 -> 再思考 -> 再行动。

2. 智能体的四大基石 🧩

如果把智能体比作一个人，它由以下四个部分组成：

🧠 大脑 (LLM / Brain)

负责理解自然语言，进行逻辑推理，并决定下一步做什么。

🛠️ 工具 (Tools)

相当于四肢与眼睛。

大模型本身无法连接外部世界（断网），我们需要给它 API 接口（如查天气、发邮件），让它能真正“做事”。

📝 记忆 (Memory)

相当于工作日志。

大模型是“健忘”的，聊完一句转头就忘。必须给它一个存储空间（如 checkpointer），让它记得之前的步骤和用户的偏好。

📋 规划 (Planning)

相当于计划表。

面对复杂任务时（如“策划旅行”），不能蛮干。必须拆解步骤：先查天气 -> 再订票 -> 最后发通知。

3. 实战演练三步走 💻

Demo 1: 最简单的常规调用 (The Model)

对应代码文件：简单的模型调用.py

状态：被封印在对话框里。

能力：只能陪聊，无法联网，无法操作真实世界。

Demo 2: “黑盒子”智能体 (The Black Box)

对应代码文件：agent_with_tools.py (使用 create_react_agent)

特点：快速上手，官方封装。

原理：我们把工具扔给它，它自动决定怎么用。

缺点：我们不知道它内部具体怎么思考的，很难精细控制流程。

Demo 3: “白盒子”智能体 (The White Box)

对应代码文件：langgraph_whitebox.py (使用 LangGraph)

核心逻辑：我们要亲手拆解智能体的每一个动作。

LangGraph 的核心组件：

State (状态)：共享的“内存条”。每次运行前必须看，运行后必须更新。

Node (节点)：具体干活的模块（如：agent 节点负责思考，tools 节点负责执行）。

Edge (边)：连接模块的线条，也是逻辑判断函数（如：tools_condition 判断是继续调用工具还是结束）。

白盒子运行流程图：

graph TD
    Start --> 读State
    读State --> |Agent节点| 思考(Call Model)
    思考(Call Model) --> 更State
    更State --> 判断{是否需要工具?}
    判断 -- 是 --> |Tools节点| 执行工具
    执行工具 --> 更State2[更新State]
    更State2 --> 读State
    判断 -- 否 --> 结束任务回复


4. 学习路径与资源 📚

不要试图一口气吃成胖子，建议按照官方推荐顺序学习：

LangChain：先看 QuickStart，了解 Prompt、Model 等基础组件。

LangGraph：重点！ 理解图、节点、边的概念，跑通快速开始项目。

DeepAgent：高度封装的框架，原理都在前面。

推荐资源：

B站搬运：LangGraph 智能体实战

YouTube搬运：基础概念补充

第二部分：环境配置与实操指南 🛠️

为了顺利运行课程中的代码，请按照以下步骤配置你的 Python 环境。

📁 文件清单

你收到的压缩包里应该包含：

简单的模型调用.py

agent_with_tools.py

langgraph_whitebox.py

requirements.txt (依赖包列表)

.env.example (配置文件模板)

🚀 第一步：准备 Python 环境

方式 A：使用 PyCharm (推荐)

打开 PyCharm，点击 File -> Open，选择代码所在的文件夹。

PyCharm 可能会提示你创建虚拟环境，点击 OK 或 Create。

如果没有提示，点击右下角解释器设置 -> Add Interpreter -> Local Interpreter -> Virtualenv Environment。

方式 B：使用 Anaconda / Miniconda

打开终端，运行：

conda create -n ai_agent python=3.10
conda activate ai_agent


📦 第二步：安装依赖包

在终端（Terminal）中，确保进入了代码文件夹，运行以下命令：

pip install -r requirements.txt


如果下载慢，使用清华源加速：

pip install -r requirements.txt -i [https://pypi.tuna.tsinghua.edu.cn/simple](https://pypi.tuna.tsinghua.edu.cn/simple)


🔑 第三步：配置 API Key (非常重要！)

打开 .env。

填入你的 Key：去轨迹流动申请一个API-KEY

# 大模型配置 (以 DeepSeek 为例)
OPENAILD_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
OPENAILD_BASE_URL="https://api.siliconflow.cn/v1"

# 天行数据 API (查天气)
# 注册: [https://www.tianapi.com/](https://www.tianapi.com/)
tianjuapi_key=你的天行数据Key

# 邮箱配置 (发邮件)
SMTP_SERVER=smtp.qq.com
MY_EMAIL=你的邮箱@qq.com
MY_EMAIL_PASSWORD=你的邮箱授权码

特别提示：申请完天行的密钥以后不是就完事了，必须在天行数据的数据管理->我的计次接口申请接口->找到天气预报然后申请接口->
回到我的计次接口必须有天气预报才可以

特别提示：如何获取邮箱授权码？
MY_EMAIL_PASSWORD 不是你的 QQ 登录密码！请按以下步骤获取：

登录 QQ邮箱网页版。

点击顶部 【设置】 -> 【账号】。

找到 【POP3/IMAP/SMTP...服务】，开启 POP3/SMTP服务。

按照提示发短信验证，获取一串 16位字符，这就是授权码。

▶️ 第四步：运行测试

直接运行文件就可以


如果看到 "AI: 你好..."，说明配置成功！接下来可以尝试运行另外两个智能体文件了。

❓ 常见问题 Q&A

Q: 报错 ModuleNotFoundError: No module named 'langgraph'?
A: 依赖没装好，请重新运行 pip install -r requirements.txt。

Q: 发邮件报错 535 Login Fail?
A: 邮箱密码填错了，请检查是否填的是 SMTP 授权码，且没有多余空格。

Q: 查询天气出错?
A: 密钥不对或者没有申请接口
