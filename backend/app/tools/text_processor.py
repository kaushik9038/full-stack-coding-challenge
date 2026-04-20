"""Simple text tool for uppercase, lowercase, and word count."""

import re


def looks_like_text_task(lower_task: str) -> bool:
    text_words = ["uppercase", "upper case", "lowercase", "lower case", "word count", "count words"]
    return any(word in lower_task for word in text_words)


def handle_text_task(task_text: str) -> str:
    lower_task = task_text.lower()
    text = pull_out_text(task_text)

    if "uppercase" in lower_task or "upper case" in lower_task:
        return text.upper()

    if "lowercase" in lower_task or "lower case" in lower_task:
        return text.lower()

    words = re.findall(r"\b\w+\b", text)
    return f"Word count: {len(words)}"


def pull_out_text(task_text: str) -> str:
    quoted_text = re.findall(r'"([^"]+)"|\'([^\']+)\'', task_text)
    if quoted_text:
        first_match = quoted_text[0]
        return first_match[0] or first_match[1]

    simple_commands = [
        "uppercase",
        "upper case",
        "lowercase",
        "lower case",
        "word count",
        "count words",
        "count words in",
    ]

    cleaned = task_text
    for command in simple_commands:
        cleaned = re.sub(command, "", cleaned, flags=re.IGNORECASE)

    cleaned = cleaned.strip(" :.-")
    if cleaned:
        return cleaned

    return task_text
