"""
MD/Docx 智能互转排版系统 - 主入口
基于 Streamlit 的 Web 界面，提供 Markdown 与 docx 双向转换及 AI 智能排版功能
支持：MD→Docx、Docx→MD、上传 DOCX 自动 AI 排版输出 DOCX
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
    """读取上传的 .md 文件内容，返回文本字符串"""
    if uploaded_file is None:
        return ""
    try:
        content = uploaded_file.read().decode("utf-8")
        uploaded_file.seek(0)
        return content
    except UnicodeDecodeError:
        return ""


def _read_docx_as_text(uploaded_file) -> str:
    """
    读取上传的 .docx 文件，提取纯文本内容。
    优先使用 Pandoc，回退 mammoth。
    """
    file_bytes = uploaded_file.read()
    uploaded_file.seek(0)

    try:
        import pypandoc
        pypandoc.get_pandoc_version()
        result = pypandoc.convert_text(file_bytes, "markdown", format="docx", extra_args=["--wrap=none"])
        return result.strip()
    except Exception:
        pass

    try:
        import mammoth
        from markdownify import markdownify as md
        html = mammoth.convert_to_html(file_bytes).value
        result = md(html, heading_style="ATX")
        return result.strip()
    except Exception:
        raise RuntimeError("无法读取 docx 文件内容，请确认文件有效且 Pandoc 已安装")


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
    if api_key_input != st.session_state.api_key:
        st.session_state.api_key = api_key_input
        st.session_state.api_verified = False

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

# ---- 模式选择 ----
st.subheader("📌 选择工作模式")
tab_md_docx, tab_docx_auto = st.tabs([
    "🔄 MD ↔ Docx 互转",
    "🤖 DOCX 自动 AI 排版",
])

# ==================== Tab 1: MD ↔ Docx 互转 ====================
with tab_md_docx:
    col_upload, col_text = st.columns([1, 1])

    with col_upload:
        st.subheader("📁 文件上传")
        uploaded_file_1 = st.file_uploader(
            f"支持 .md / .docx（最大 {MAX_FILE_SIZE_MB}MB）",
            type=SUPPORTED_EXTENSIONS,
            help="上传 .md 或 .docx 文件",
            label_visibility="collapsed",
            key="upload_1",
        )

    with col_text:
        st.subheader("📝 文本粘贴")
        text_input_1 = st.text_area(
            "粘贴 Markdown 文本（文件上传优先）",
            height=200,
            placeholder="在此粘贴 Markdown 内容...\n文件上传后将以文件内容为准",
            label_visibility="collapsed",
            key="text_1",
        )

    st.divider()
    col_dir, col_ai, col_btn = st.columns([1, 1, 1])

    with col_dir:
        direction = st.radio(
            "🔄 转换方向",
            options=["md_to_docx", "docx_to_md"],
            format_func=lambda x: "MD → Docx" if x == "md_to_docx" else "Docx → MD",
            horizontal=True,
            key="direction_1",
        )

    with col_ai:
        use_ai_1 = st.checkbox(
            "🤖 AI 优化排版",
            value=False,
            help="勾选后将调用 DeepSeek API 对内容进行智能排版优化",
            disabled=not st.session_state.api_key.strip(),
            key="ai_1",
        )
        if not st.session_state.api_key.strip():
            st.caption("⚠️ 请先填写 API Key 以启用 AI 排版")

    with col_btn:
        st.write("")
        convert_clicked_1 = st.button(
            "🚀 开始转换",
            type="primary",
            use_container_width=True,
            key="btn_1",
        )

    st.divider()

    # ---- 转换逻辑 ----
    if convert_clicked_1:
        content = None

        if uploaded_file_1 is not None:
            file_size_mb = uploaded_file_1.size / (1024 * 1024)
            if file_size_mb > MAX_FILE_SIZE_MB:
                st.error(f"文件大小 {file_size_mb:.1f}MB 超过上限 {MAX_FILE_SIZE_MB}MB，请压缩后重试")
                st.stop()

            file_ext = uploaded_file_1.name.rsplit(".", 1)[-1].lower() if "." in uploaded_file_1.name else ""

            if file_ext == "md":
                content = _read_uploaded_file(uploaded_file_1)
                if not content.strip():
                    st.error("上传的 Markdown 文件内容为空")
                    st.stop()
            elif file_ext == "docx":
                content = uploaded_file_1
            else:
                st.error(f"不支持的文件格式：.{file_ext}，仅支持 {', '.join(SUPPORTED_EXTENSIONS)}")
                st.stop()
        elif text_input_1.strip():
            content = text_input_1.strip()
        else:
            st.error("请上传文件或粘贴文本内容")
            st.stop()

        with st.spinner("正在处理..."):
            final_md = ""
            final_docx = None
            final_type = ""

            try:
                if direction == "md_to_docx":
                    if not isinstance(content, str):
                        st.error("MD → Docx 需要 Markdown 文本输入，请上传 .md 文件或粘贴内容")
                        st.stop()

                    working_md = content

                    if use_ai_1:
                        with st.spinner("AI 正在优化排版..."):
                            try:
                                working_md = format_with_ai(
                                    working_md, style, st.session_state.api_key
                                )
                                st.success("✅ AI 排版完成")
                            except Exception as ai_err:
                                st.warning(f"⚠️ AI 排版失败，将使用原始内容继续：{str(ai_err)[:200]}")

                    final_docx = convert_md_to_docx(
                        working_md, _get_template_path()
                    )
                    final_md = working_md
                    final_type = "docx"

                else:  # docx_to_md
                    if isinstance(content, str):
                        st.error("Docx → MD 需要上传 .docx 文件")
                        st.stop()

                    working_md = convert_docx_to_md(content)

                    if use_ai_1:
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

# ==================== Tab 2: DOCX 自动 AI 排版 ====================
with tab_docx_auto:
    st.markdown("**上传一份 Word 文档，AI 自动优化排版并生成格式规整的新 DOCX 文件。**")
    st.info("💡 流程：上传 DOCX → 提取文本 → AI 智能排版（含封面+分页符）→ 生成精美 DOCX")

    col_docx_up, col_docx_info = st.columns([1, 1])

    with col_docx_up:
        uploaded_docx = st.file_uploader(
            f"上传需要排版的 .docx 文件（最大 {MAX_FILE_SIZE_MB}MB）",
            type=["docx"],
            help="上传 Word 文档，AI 将自动优化排版",
            label_visibility="collapsed",
            key="upload_docx_auto",
        )

    with col_docx_info:
        if uploaded_docx is not None:
            file_size_mb = uploaded_docx.size / (1024 * 1024)
            st.metric("文件大小", f"{file_size_mb:.1f} MB")
            st.metric("文件名", uploaded_docx.name)

    # 排版风格选择
    docx_style = st.radio(
        "选择排版风格",
        options=["docx_format", "general", "academic", "report"],
        format_func=lambda x: {
            "docx_format": "📋 智能识别（推荐）— 自动识别封面信息，最佳分页",
            "general": "📝 通用 — 标题分级 + 分章分页",
            "academic": "🎓 学术 — 严格格式 + 摘要/结论 + 分页",
            "report": "📊 报告 — 目录 + 图表标注 + 分页",
        }[x],
        horizontal=False,
        key="docx_style",
    )

    auto_btn_clicked = st.button(
        "🤖 开始 AI 排版",
        type="primary",
        use_container_width=True,
        disabled=(uploaded_docx is None or not st.session_state.api_key.strip()),
        key="btn_docx_auto",
    )

    if not st.session_state.api_key.strip():
        st.caption("⚠️ 请先在侧边栏填写 DeepSeek API Key")
    if uploaded_docx is None:
        st.caption("⚠️ 请先上传需要排版的 .docx 文件")

    # ---- DOCX 自动排版逻辑 ----
    if auto_btn_clicked and uploaded_docx is not None:
        file_size_mb = uploaded_docx.size / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            st.error(f"文件大小 {file_size_mb:.1f}MB 超过上限 {MAX_FILE_SIZE_MB}MB，请压缩后重试")
            st.stop()

        try:
            # Step 1: 提取文本
            with st.spinner("📖 正在从 DOCX 提取文本内容..."):
                extracted_md = _read_docx_as_text(uploaded_docx)
                if not extracted_md.strip():
                    st.error("无法从该文档中提取文字内容，请确认文件有效")
                    st.stop()
                st.success(f"✅ 文本提取完成（{len(extracted_md)} 字符）")

            # Step 2: AI 排版
            with st.spinner(f"🤖 AI 正在优化排版（风格：{docx_style}）..."):
                try:
                    formatted_md = format_with_ai(
                        extracted_md, docx_style, st.session_state.api_key
                    )
                    st.success(f"✅ AI 排版完成（{len(formatted_md)} 字符）")
                except Exception as ai_err:
                    st.warning(f"⚠️ AI 排版失败：{str(ai_err)[:300]}")
                    st.info("将使用原始提取文本生成 DOCX")
                    formatted_md = extracted_md

            # Step 3: 生成 DOCX（含封面和分页符后处理）
            with st.spinner("📄 正在生成格式化的 DOCX 文件..."):
                final_docx = convert_md_to_docx(
                    formatted_md,
                    _get_template_path(),
                    enable_post_process=True,
                )
                st.success("✅ DOCX 生成完成")

            # 保存结果
            st.session_state.last_result_md = formatted_md
            st.session_state.last_result_docx = final_docx
            st.session_state.last_result_type = "docx"

        except RuntimeError as e:
            st.error(str(e))
            st.info("💡 提示：请确保已安装 Pandoc。\n"
                     "Windows: https://pandoc.org/installing.html\n"
                     "Mac: brew install pandoc\n"
                     "Linux: sudo apt install pandoc")
            st.stop()
        except Exception as e:
            st.error(f"❌ 处理失败：{str(e)[:500]}")
            st.stop()


# ==================== 结果展示与下载（两个 Tab 共享） ====================
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
st.caption("MD/Docx 智能互转排版系统 v1.1 | 使用 Pandoc + DeepSeek API 驱动 | 封面排版·分页·DOCX 自动排版")
