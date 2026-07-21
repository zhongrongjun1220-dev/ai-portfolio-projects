# AI 智能助手演示项目

面向 AI 应用开发实习岗位的项目演示：基于 **FastAPI + ChatKit** 搭建可运行的多轮对话助手，并接入了兼容 OpenAI 接口的大模型，支持流式输出、工具调用、实体引用与前端实时交互。

## 项目定位

这是一个从 0 到 1 完成的 **AI 应用开发练习项目**，目标是把“会调用 API”扩展成“可交付的最小 AI 产品原型”。项目聚焦以下能力：

- 前后端分离的 AI 应用结构
- 服务端流式事件返回，前端实时渲染
- 工具调用与外部能力接入
- 可演示、可讲解、可继续扩展

## 技术栈

- **后端**：FastAPI、ChatKit Server、SQLite、Python Async
- **模型层**：OpenAI 兼容接口 / StepFun Responses API
- **前端**：原生 HTML + Fetch SSE 流式解析
- **能力扩展**：天气查询、数据分析、主题预览、实体上下文注入

## 功能演示

- 流式对话：用户发送消息后，助手逐字返回回答
- 工具调用：可根据问题触发天气、数据分析等能力
- 实体引用：输入中可引用业务实体，自动注入上下文
- 前端交互：发送、填入示例、复制请求体、实时输出、停止生成

## 环境要求

- Python >= 3.12
- 可访问 OpenAI 兼容接口地址
- 建议使用 `uv` 或 `pip` 安装依赖

## 快速启动

### 1. 克隆项目
```bash
git clone <your-repo-url>
cd ChatKit_Powered_Assistant
```

### 2. 配置环境
```bash
cp .env.example .env
```

在 `.env` 中填入你的 API Key 与模型地址：
```env
OPENAI_API_KEY=your_open_ai_key
OPENAI_BASE_URL=https://api.openai.com/v1
DEFAULT_MODEL=step-3.7-flash
```

### 3. 安装依赖
```bash
uv sync
# 或
pip install .
```

### 4. 启动服务
```bash
python main.py
```

打开浏览器访问：
```bash
http://localhost:8011/
```

## 项目结构

```text
ChatKit_Powered_Assistant/
├── app/
│   ├── agent.py          # Agent 配置与系统指令
│   ├── server.py         # ChatKit 服务端实现
│   ├── store.py          # SQLite 线程与消息存储
│   ├── tools.py          # 工具函数集合
│   ├── types.py          # 请求上下文定义
│   └── widgets.py        # 前端组件/能力封装
├── static/
│   └── index.html        # 演示前端
├── scripts/              # 本地调试和排查脚本
├── docs/
│   ├── assets/           # 截图和导出素材
│   └── logs/             # 本地运行日志
├── main.py               # FastAPI 入口
├── pyproject.toml        # 项目元数据和依赖
├── .env.example          # 环境变量示例
├── .gitignore            # 仓库忽略规则
└── README.md             # 项目说明
```

## 开发建议

- 本地调试时可使用 `scripts/` 下的脚本查看请求、响应和事件流。
- 前端流式交互相关说明可参考 `static/index.html` 的请求体结构和 SSE 解析逻辑。
- 面试讲稿建议围绕“请求封装、流式处理、异常回传、前端交互”组织。

## 面试可讲点

- **架构设计**：FastAPI 作为后端网关，ChatKit 负责线程/事件/工具编排，前端通过 SSE 实现流式交互
- **模型接入**：不局限单一厂商，抽象为 OpenAI 兼容客户端，方便切换模型
- **流式体验**：服务端事件驱动 + 前端增量渲染，降低首字等待感知
- **工具调用**：不只是聊天，还能接入外部能力并返回结构化结果
- **工程化**：环境变量管理、CORS、异常日志、本地持久化存储
- **可扩展性**：可继续加入用户认证、会话管理、前端路由、部署脚本

## 后续可扩展方向

- 增加用户注册 / 登录与会话隔离
- 增加对话历史列表、多轮上下文管理
- 接入更多工具：文档问答、网页检索、代码解释器
- 前端升级为 React / Vue 单页应用
- 增加 Docker 部署与 CI/CD
- 增加接口测试与性能监控

## 注意事项

- 本项目用于学习与面试展示，请勿直接上传真实密钥到公开仓库
- 若用于生产环境，建议增加限流、鉴权、日志脱敏与模型成本控制
- `.env`、`*.db`、`*.log` 等运行时文件已加入忽略规则，不要提交到仓库

## License

请在仓库中补充 LICENSE 文件后再公开发布。
