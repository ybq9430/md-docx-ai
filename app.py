"""
MD/Docx 智能互转排版系统 - 主入口
基于 Streamlit 的 Web 界面，提供 Markdown 与 docx 双向转换及 AI 智能排版功能
"""

import os
import streamlit as st
import markdown2

from converter.md_to_docx import convert_md_to_docx
from converter.docx_to_md import convert_docx_to_md
from ai.formatter import format_with_ai


# ==================== 页面配置 ====================
st.set_page_config(
    page_title="MD/Docx 智能互转排版系统",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================== 常量 ====================
SUPPORTED_EXTENSIONS = ["md", "docx"]
MAX_FILE_SIZE_MB = 10
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")


# ==================== 辅助函数 ====================
def _check_pandoc_available() -> bool:
    """检测 Pandoc 是否已安装"""
    import pypandoc
    try:
        pypandoc.get_pandoc_version()
        return True
    except OSError:
        return False


def _read_uploaded_file(uploaded_file) -> str:
    """读取上传文件内容，返回文本字符串"""
    if uploaded_file is None:
        return ""
    try:
        content = uploaded_file.read().decode("utf-8")
        uploaded_file.seek(0)  # 重置文件指针
        return content
    except UnicodeDecodeError:
        # docx 是二进制格式，不能直接 decode
        return ""


def _render_markdown_preview(md_text: str):
    """将 Markdown 渲染为 HTML 预览"""
    if md_text:
        html = markdown2.markdown(
            md_text,
            extras=["tables", "fenced-code-blocks", "code-friendly", "header-ids"]
        )
        st.markdown(html, unsafe_allow_html=True)


def _get_template_path() -> str:
    """获取 reference.docx 模板路径（若存在）"""
    template_path = os.path.join(TEMPLATE_DIR, "reference.docx")
    return template_path if os.path.isfile(template_path) else None


# ==================== 初始化 session_state ====================
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "last_result_md" not in st.session_state:
    st.session_state.last_result_md = ""
if "last_result_docx" not in st.session_state:
    st.session_state.last_result_docx = None
if "last_result_type" not in st.session_state:
    st.session_state.last_result_type = ""  # "md" 或 "docx"
if "api_verified" not in st.session_state:
    st.session_state.api_verified = False


# ==================== 侧边栏 ====================
with st.sidebar:
    st.title("⚙️ 设置")

    # ---- API Key 区域 ----
    st.subheader("🔑 DeepSeek API Key")
    api_key_input = st.text_input(
        "输入您的 API Key",
        type="password",
        value=st.session_state.api_key,
        placeholder="sk-xxxxxxxxxxxxxxxx",
        help="您的 Key 仅保存在当前会话中，刷新页面后清空，不会记录到日志或磁盘。",
        label_visibility="collapsed",
    )
    # 自动同步到 session
    if api_key_input != st.session_state.api_key:
        st.session_state.api_key = api_key_input
        st.session_state.api_verified = False  # Key 变更后需重新验证

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔌 测试连接", use_container_width=True):
            if not st.session_state.api_key.strip():
                st.error("请先输入 API Key")
            else:
                with st.spinner("正在测试连接..."):
                    try:
                        from ai.formatter import format_with_ai
                        format_with_ai("测试", "general", st.session_state.api_key)
                        st.session_state.api_verified = True
                        st.success("✅ 连接成功！API Key 有效")
                    except Exception as e:
                        st.session_state.api_verified = False
                        st.error(f"❌ 连接失败：{str(e)[:200]}")

    with col2:
        if st.session_state.api_verified:
            st.markdown("🟢 已验证")
        else:
            st.markdown("⚪ 未验证")

    st.divider()

    # ---- 排版风格 ----
    st.subheader("🎨 排版风格")
    style = st.radio(
        "选择排版风格",
        options=["general", "academic", "report"],
        format_func=lambda x: {"general": "通用", "academic": "学术", "report": "报告"}[x],
        label_visibility="collapsed",
    )

    st.divider()

    # ---- Pandoc 状态 ----
    st.subheader("📦 系统状态")
    pandoc_ok = _check_pandoc_available()
    if pandoc_ok:
        st.success("✅ Pandoc 已就绪")
    else:
        st.error("❌ Pandoc 未安装")
        st.caption("请访问 https://pandoc.org/installing.html 安装")

    st.caption(f"支持的格式：{', '.join(SUPPORTED_EXTENSIONS)} | 单文件上限：{MAX_FILE_SIZE_MB}MB")


# ==================== 主内容区 ====================
st.title("📄 MD↔Docx 智能互转排版系统")
st.caption("上传文件或粘贴内容，一键转换格式，AI 辅助排版优化")

# ---- 输入区域 ----
col_upload, col_text = st.columns([1, 1])

with col_upload:
    st.subheader("📁 文件上传")
    uploaded_file = st.file_uploader(
        f"支持 .md / .docx（最大 {MAX_FILE_SIZE_MB}MB）",
        type=SUPPORTED_EXTENSIONS,
        help="上传 .md 或 .docx 文件",
        label_visibility="collapsed",
    )

with col_text:
    st.subheader("📝 文本粘贴")
    text_input = st.text_area(
        "粘贴 Markdown 文本（文件上传优先）",
        height=200,
        placeholder="在此粘贴 Markdown 内容...\n文件上传后将以文件内容为准",
        label_visibility="collapsed",
    )

# ---- 转换选项 ----
st.divider()
col_dir, col_ai, col_btn = st.columns([1, 1, 1])

with col_dir:
    direction = st.radio(
        "🔄 转换方向",
        options=["md_to_docx", "docx_to_md"],
        format_func=lambda x: "MD → Docx" if x == "md_to_docx" else "Docx → MD",
        horizontal=True,
    )

with col_ai:
    use_ai = st.checkbox(
        "🤖 AI 优化排版",
        value=False,
        help="勾选后将调用 DeepSeek API 对内容进行智能排版优化",
        disabled=not st.session_state.api_key.strip(),
    )
    if not st.session_state.api_key.strip():
        st.caption("⚠️ 请先填写 API Key 以启用 AI 排版")

with col_btn:
    st.write("")  # 占位对齐
    convert_clicked = st.button(
        "🚀 开始转换",
        type="primary",
        use_container_width=True,
    )

st.divider()

# ---- 核心转换逻辑 ----
if convert_clicked:
    # Step 1: 获取输入内容
    content = None

    if uploaded_file is not None:
        # 检查文件大小
        file_size_mb = uploaded_file.size / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            st.error(f"文件大小 {file_size_mb:.1f}MB 超过上限 {MAX_FILE_SIZE_MB}MB，请压缩后重试")
            st.stop()

        # 根据扩展名判断文件类型
        file_ext = uploaded_file.name.rsplit(".", 1)[-1].lower() if "." in uploaded_file.name else ""

        if file_ext == "md":
            content = _read_uploaded_file(uploaded_file)
            if not content.strip():
                st.error("上传的 Markdown 文件内容为空")
                st.stop()
        elif file_ext == "docx":
            content = uploaded_file  # 传递文件对象给 docx 转换器
        else:
            st.error(f"不支持的文件格式：.{file_ext}，仅支持 {', '.join(SUPPORTED_EXTENSIONS)}")
            st.stop()

    elif text_input.strip():
        content = text_input.strip()
    else:
        st.error("请上传文件或粘贴文本内容")
        st.stop()

    # Step 2: 执行转换
    with st.spinner("正在处理..."):
        final_md = ""
        final_docx = None
        final_type = ""

        try:
            if direction == "md_to_docx":
                # 确保 content 是文本字符串
                if not isinstance(content, str):
                    st.error("MD → Docx 需要 Markdown 文本输入，请上传 .md 文件或粘贴内容")
                    st.stop()

                working_md = content

                # AI 优化（若启用）
                if use_ai:
                    with st.spinner("AI 正在优化排版..."):
                        try:
                            working_md = format_with_ai(
                                working_md, style, st.session_state.api_key
                            )
                            st.success("✅ AI 排版完成")
                        except Exception as ai_err:
                            st.warning(f"⚠️ AI 排版失败，将使用原始内容继续转换：{str(ai_err)[:200]}")

                # MD → Docx
                final_docx = convert_md_to_docx(
                    working_md, _get_template_path()
                )
                final_md = working_md
                final_type = "docx"

            else:  # docx_to_md
                # content 应该是文件对象（UploadedFile）或文件路径
                if isinstance(content, str):
                    st.error("Docx → MD 需要上传 .docx 文件")
                    st.stop()

                working_md = convert_docx_to_md(content)

                # AI 优化（若启用）
                if use_ai:
                    with st.spinner("AI 正在优化排版..."):
                        try:
                            working_md = format_with_ai(
                                working_md, style, st.session_state.api_key
                            )
                            st.success("✅ AI 排版完成")
                        except Exception as ai_err:
                            st.warning(f"⚠️ AI 排版失败，将使用原始内容继续：{str(ai_err)[:200]}")

                final_md = working_md
                final_type = "md"

            # 保存结果到 session_state
            st.session_state.last_result_md = final_md
            st.session_state.last_result_docx = final_docx
            st.session_state.last_result_type = final_type

            st.success(f"🎉 转换成功！")

        except RuntimeError as e:
            st.error(str(e))
            st.info("💡 提示：请确保已安装 Pandoc。\n"
                     "Windows: https://pandoc.org/installing.html\n"
                     "Mac: brew install pandoc\n"
                     "Linux: sudo apt install pandoc")
            st.stop()
        except Exception as e:
            st.error(f"❌ 转换失败：{str(e)[:500]}")
            st.stop()

# ---- 结果展示与下载 ----
if st.session_state.last_result_type:
    st.divider()
    st.subheader("📋 转换结果")

    tab_preview, tab_raw = st.tabs(["🔍 渲染预览", "📝 Markdown 源码"])

    with tab_preview:
        if st.session_state.last_result_md:
            _render_markdown_preview(st.session_state.last_result_md)
        else:
            st.info("当前结果为 docx 格式，请下载后使用 Word 打开预览")

    with tab_raw:
        if st.session_state.last_result_md:
            st.code(st.session_state.last_result_md, language="markdown")
        else:
            st.info("当前结果为 docx 格式，无 Markdown 源码")

    # 下载按钮
    st.divider()
    if st.session_state.last_result_type == "docx" and st.session_state.last_result_docx:
        st.download_button(
            label="⬇️ 下载 docx 文件",
            data=st.session_state.last_result_docx,
            file_name="output.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            type="primary",
        )
    elif st.session_state.last_result_type == "md" and st.session_state.last_result_md:
        st.download_button(
            label="⬇️ 下载 Markdown 文件",
            data=st.session_state.last_result_md.encode("utf-8"),
            file_name="output.md",
            mime="text/markdown",
            type="primary",
        )


# ==================== 页脚 ====================
st.divider()
st.caption("MD/Docx 智能互转排版系统 v1.0 | 使用 Pandoc + DeepSeek API 驱动")
