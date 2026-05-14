"""
docx → Markdown 转换模块
优先使用 pypandoc，Pandoc 不可用时回退到 mammoth + markdownify
"""

import pypandoc
import mammoth
from markdownify import markdownify as md


def _has_pandoc() -> bool:
    """检测 Pandoc 是否可用"""
    try:
        pypandoc.get_pandoc_version()
        return True
    except OSError:
        return False


def convert_docx_to_md(file) -> str:
    """
    将 docx 文件内容转换为 Markdown 文本

    参数：
        file: Streamlit UploadedFile 对象或文件路径（str/bytes）

    返回：
        str: 转换后的 Markdown 字符串

    异常：
        ValueError: 输入文件无效时抛出
        Exception: 转换过程发生错误时抛出
    """
    # 归一化输入：Streamlit UploadedFile → bytes
    if hasattr(file, "read"):
        file_bytes = file.read()
    elif isinstance(file, bytes):
        file_bytes = file
    elif isinstance(file, str):
        with open(file, "rb") as f:
            file_bytes = f.read()
    else:
        raise ValueError("不支持的文件输入类型，请传入文件对象、bytes 或文件路径")

    # 方案一：优先使用 Pandoc
    if _has_pandoc():
        try:
            result = pypandoc.convert_text(
                file_bytes,
                "markdown",
                format="docx",
                extra_args=["--wrap=none"]
            )
            return result.strip()

        except Exception as pandoc_err:
            # Pandoc 转换失败时记录但仍尝试回退
            print(f"[警告] Pandoc 转换失败：{pandoc_err}，尝试回退方案")

    # 方案二：回退到 mammoth + markdownify
    try:
        html_result = mammoth.convert_to_html(file_bytes)
        html_content = html_result.value

        # 将 HTML 转换为 Markdown
        md_result = md(html_content, heading_style="ATX")

        if not md_result or not md_result.strip():
            raise Exception("回退方案转换结果为空")

        return md_result.strip()

    except Exception as fallback_err:
        raise Exception(
            f"docx 转 Markdown 失败：{str(fallback_err)}。"
            "请确认文件有效且 Pandoc 已正确安装。"
        )
