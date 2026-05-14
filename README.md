# MD/Docx 智能互转排版系统

基于 Web 的文档智能互转工具，支持 Markdown 与 Word（docx）双向转换，并接入 DeepSeek API 对转换结果进行 AI 排版优化。

## 功能特性

- **双向互转**：Markdown ↔ docx 格式转换，保留标题、列表、表格、代码块等结构
- **AI 智能排版**：调用 DeepSeek API 优化文档排版，支持通用/学术/报告三种风格
- **在线预览**：Markdown 渲染实时预览，检查转换效果
- **一键下载**：转换成功后直接下载 .md 或 .docx 文件
- **安全可靠**：API Key 仅保存在会话中，不记日志、不落磁盘

## 环境依赖

### Python 包安装

```bash
pip install -r requirements.txt
```

### Pandoc 安装（必须）

Pandoc 是本项目的核心转换引擎，需单独安装：

| 操作系统 | 安装方式 |
|---------|---------|
| **Windows** | 访问 https://pandoc.org/installing.html 下载安装包，按向导完成安装 |
| **macOS** | `brew install pandoc` |
| **Linux** | `sudo apt install pandoc`（Debian/Ubuntu）或 `sudo dnf install pandoc`（Fedora） |

安装后可在终端执行 `pandoc --version` 验证安装是否成功。

## 快速启动

```bash
cd md-docx-ai
pip install -r requirements.txt
streamlit run app.py
```

浏览器访问 `http://localhost:8501` 即可使用。

## 使用说明

1. **配置 API Key**：在侧边栏输入 DeepSeek API Key，点击"测试连接"验证有效性
2. **输入文档**：上传 .md / .docx 文件，或直接在文本框粘贴 Markdown 内容
3. **选择方向**：选择转换方向（MD → Docx 或 Docx → MD）
4. **AI 排版**（可选）：勾选"AI 优化排版"，选择排版风格（通用/学术/报告）
5. **转换下载**：点击"开始转换"，预览结果后下载文件

## 项目结构

```
md-docx-ai/
├── app.py                 # Streamlit 主页面
├── converter/
│   ├── __init__.py
│   ├── md_to_docx.py      # Markdown → docx 转换
│   └── docx_to_md.py      # docx → Markdown 转换
├── ai/
│   ├── __init__.py
│   └── formatter.py       # DeepSeek API 排版调用
├── templates/             # Pandoc 模板目录（可放入 reference.docx）
├── requirements.txt
└── README.md
```

## 注意事项

- **API Key 安全**：Key 仅保存在浏览器 Session 中，刷新页面后清空，不会持久化存储或写入日志
- **Pandoc 依赖**：若 Pandoc 未安装，系统将在侧边栏给出提示，docx 转 md 会尝试 mammoth 回退方案
- **文件大小**：单个上传文件不超过 10MB，超出请先拆分或压缩
- **AI 排版**：AI 排版依赖 DeepSeek API 可用性，若调用失败会自动回退为直接转换，不影响核心功能
- **网络要求**：AI 排版功能需要能够访问 `api.deepseek.com`
- **浏览器兼容**：推荐 Chrome 90+、Edge 90+、Firefox 88+ 版本

## 技术栈

- **前端框架**：Streamlit
- **格式转换**：Pandoc（pypandoc）、mammoth、markdownify、python-docx
- **AI 接口**：DeepSeek API（OpenAI SDK 兼容模式）
- **Markdown 渲染**：markdown2
