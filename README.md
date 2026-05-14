<p align="center">
  <h1 align="center">📄 MD/Docx 智能互转排版系统</h1>
  <p align="center">
    基于 Pandoc + DeepSeek API 的文档格式互转与 AI 智能排版工具
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Streamlit-1.x-FF4B4B?logo=streamlit" alt="Streamlit">
  <img src="https://img.shields.io/badge/AI-DeepSeek-536DFE" alt="DeepSeek">
  <img src="https://img.shields.io/badge/Engine-Pandoc-7B4A0B" alt="Pandoc">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
</p>

---

## ✨ 功能特性

| 特性 | 说明 |
|------|------|
| 🔄 **双向互转** | Markdown ↔ docx，保留标题、列表、表格、代码块等格式 |
| 🤖 **AI 排版** | 接入 DeepSeek API，自动优化文档结构与排版 |
| 🎨 **三种风格** | 通用 / 学术 / 报告，满足不同场景需求 |
| 👁️ **在线预览** | Markdown 渲染实时预览，所见即所得 |
| ⬇️ **一键下载** | 转换成功后直接下载 .md 或 .docx 文件 |
| 🔒 **安全可靠** | API Key 仅存会话，不落盘、不写日志 |

---

## 🚀 快速开始

### 1. 安装 Pandoc（必须）

| 操作系统 | 命令 |
|---------|------|
| **Windows** | 访问 [pandoc.org/installing.html](https://pandoc.org/installing.html) 下载安装包 |
| **macOS** | `brew install pandoc` |
| **Linux (Debian/Ubuntu)** | `sudo apt install pandoc` |
| **Linux (Fedora)** | `sudo dnf install pandoc` |

验证安装：`pandoc --version`

### 2. 安装 Python 依赖

```bash
git clone https://github.com/ybq9430/md-docx-ai.git
cd md-docx-ai
pip install -r requirements.txt
```

### 3. 启动应用

```bash
streamlit run app.py
```

浏览器访问 **http://localhost:8501** 即可使用。

---

## 📖 使用指南

1. **🔑 配置 API Key** — 侧边栏输入 [DeepSeek API Key](https://platform.deepseek.com/)，点击「测试连接」验证
2. **📂 上传文档** — 上传 .md 或 .docx 文件，也可直接粘贴 Markdown 文本
3. **🔄 选择方向** — MD → Docx 或 Docx → MD
4. **🤖 AI 排版**（可选）— 勾选后选择排版风格（通用 / 学术 / 报告）
5. **⬇️ 下载结果** — 点击「开始转换」，预览满意后下载文件

---

## 🧱 项目结构

```
md-docx-ai/
├── app.py                 # Streamlit Web 主页面
├── converter/
│   ├── __init__.py
│   ├── md_to_docx.py      # Markdown → docx（pypandoc）
│   └── docx_to_md.py      # docx → Markdown（Pandoc / mammoth 回退）
├── ai/
│   ├── __init__.py
│   └── formatter.py       # DeepSeek API 排版（三套 Prompt）
├── templates/             # 放置 reference.docx 模板
├── requirements.txt       # Python 依赖清单
└── README.md
```

---

## 🛠️ 技术栈

| 组件 | 技术 | 用途 |
|------|------|------|
| Web 框架 | [Streamlit](https://streamlit.io) | 构建交互式 UI |
| 转换引擎 | [Pandoc](https://pandoc.org) | MD ↔ docx 核心转换 |
| Pandoc 绑定 | pypandoc | Python 调用 Pandoc |
| Word 解析 | mammoth | docx → HTML（回退方案） |
| HTML 转 MD | markdownify | HTML → Markdown |
| MD 渲染 | markdown2 | 页面内 Markdown 预览 |
| AI 接口 | [DeepSeek API](https://api-docs.deepseek.com/) | 智能排版优化（OpenAI 兼容模式） |

---

## 🎯 AI 排版策略

三种内置 Prompt，分别优化不同类型的文档：

| 风格 | 适用场景 | 优化重点 |
|------|---------|---------|
| **通用** | 博客、日常文档 | 标题分级、段落清晰、去除冗余空行 |
| **学术** | 论文、研究报告 | 标题严格分级、blockquote 引用、摘要/结论 |
| **报告** | 工作汇报、方案 | 自动生成目录、重点加粗、图表标注 |

---

## ⚠️ 注意事项

- **Pandoc** 是核心依赖，必须预先安装
- **DeepSeek API Key** 需要自行前往 [platform.deepseek.com](https://platform.deepseek.com) 申请
- API Key 仅存在浏览器 Session 中，刷新页面即清空，不持久化
- 单个文件大小上限 **10MB**
- AI 排版失败会自动回退为直接转换，不影响核心功能
- 推荐使用 Chrome 90+ / Edge 90+ / Firefox 88+

---

## 📋 依赖清单

```
streamlit
openai
pypandoc
python-docx
mammoth
markdownify
markdown2
```

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request。

---

## 📄 许可证

MIT License — 详见 [LICENSE](LICENSE) 文件。
