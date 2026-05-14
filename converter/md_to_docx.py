"""
Markdown → docx 转换模块
使用 pypandoc 调用 Pandoc 引擎完成转换
"""

import os
import pypandoc


def convert_md_to_docx(md_text: str, template_path: str = None) -> bytes:
    """
    将 Markdown 文本转换为 docx 格式的二进制数据

    参数：
        md_text (str): 待转换的 Markdown 文本内容
        template_path (str, optional): Pandoc reference.docx 模板路径

    返回：
        bytes: docx 文件的二进制数据，供下载使用

    异常：
        RuntimeError: Pandoc 未安装时抛出
        Exception: 转换过程发生错误时抛出
    """
    # 检查 Pandoc 是否可用
    try:
        pypandoc.get_pandoc_version()
    except OSError:
        raise RuntimeError(
            "未检测到 Pandoc，请先安装 Pandoc 后重试。\n"
            "Windows: 访问 https://pandoc.org/installing.html 下载安装包\n"
            "Mac: brew install pandoc\n"
            "Linux: sudo apt install pandoc"
        )

    try:
        # 构建额外参数（--from 和 --to 由 pypandoc 自动管理）
        extra_args = []

        # 若提供了模板文件且存在，则使用 reference-doc 参数
        if template_path and os.path.isfile(template_path):
            extra_args.extend(["--reference-doc", template_path])

        # 调用 pypandoc 进行转换
        docx_bytes = pypandoc.convert_text(
            md_text,
            "docx",
            format="markdown",
            extra_args=extra_args,
        )

        return docx_bytes

    except Exception as e:
        raise Exception(f"Markdown 转 docx 失败：{str(e)}")
