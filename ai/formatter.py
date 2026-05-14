"""
AI 智能排版模块
通过 OpenAI SDK 兼容模式调用 DeepSeek API 对文档内容进行排版优化
"""

from openai import OpenAI

# 排版风格对应的 Prompt 模板
_STYLE_PROMPTS = {
    "general": (
        "优化以下 Markdown 内容排版，要求："
        "标题分级合理，段落简洁清晰，列表整齐，去除多余空行，语句通顺。"
        "仅输出优化后的 Markdown，不添加任何说明。"
    ),
    "academic": (
        "优化以下 Markdown 内容排版，要求："
        "标题严格分级（# ## ###），正文段落首行缩进，"
        "引用使用 > blockquote，若缺少摘要和结论则补充提示占位符，"
        "符合学术写作规范。仅输出优化后的 Markdown，不添加任何说明。"
    ),
    "report": (
        "优化以下 Markdown 内容排版，要求："
        "添加目录结构（## 目录），段落简洁有力，"
        "重点内容加粗，图表位置添加说明标注，"
        "符合商业报告风格。仅输出优化后的 Markdown，不添加任何说明。"
    ),
}

# DeepSeek API 地址
_BASE_URL = "https://api.deepseek.com"

# 默认模型
_MODEL = "deepseek-chat"


def format_with_ai(text: str, style: str, api_key: str) -> str:
    """
    调用 DeepSeek API 对文本进行智能排版优化

    参数：
        text (str): 待优化的文本内容
        style (str): 排版风格，可选值：general / academic / report
        api_key (str): DeepSeek API Key

    返回：
        str: AI 优化后的文本

    异常：
        ValueError: 参数无效时抛出
        Exception: API 调用失败时抛出
    """
    # 参数校验
    if not text or not text.strip():
        raise ValueError("待排版文本不能为空")

    if not api_key or not api_key.strip():
        raise ValueError("API Key 不能为空")

    if style not in _STYLE_PROMPTS:
        raise ValueError(
            f"不支持的排版风格：{style}，可选值为：{', '.join(_STYLE_PROMPTS.keys())}"
        )

    try:
        # 初始化 DeepSeek 客户端（OpenAI SDK 兼容模式）
        client = OpenAI(
            api_key=api_key.strip(),
            base_url=_BASE_URL,
        )

        # 获取对应风格的 Prompt
        system_prompt = _STYLE_PROMPTS[style]

        # 调用 API
        response = client.chat.completions.create(
            model=_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            temperature=0.3,
        )

        # 提取返回内容
        result = response.choices[0].message.content

        if not result or not result.strip():
            raise Exception("AI 返回内容为空")

        return result.strip()

    except Exception as e:
        # 将异常统一包装后抛出
        error_msg = str(e)

        # 针对常见错误提供友好提示
        if "401" in error_msg or "Unauthorized" in error_msg or "authentication" in error_msg.lower():
            raise Exception("API Key 无效，请检查后重试")
        if "402" in error_msg or "insufficient" in error_msg.lower():
            raise Exception("API 余额不足，请充值后重试")
        if "429" in error_msg or "rate" in error_msg.lower():
            raise Exception("API 请求过于频繁，请稍后重试")
        if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
            raise Exception("API 请求超时，请检查网络后重试")

        raise Exception(f"AI 排版失败：{error_msg}")
