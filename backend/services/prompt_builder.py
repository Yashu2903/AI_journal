def build_prompt(
    *,
    history: list[dict],
    memories: list[str]
) -> list[dict]:

    system_message = {
        "role": "system",
        "content": (
            "You are an AI assistant with access to past memories.\n"
            "When memories are provided, you MUST use them to answer.\n"
            "If memories are relevant, refer to them naturally.\n"
            "If not, answer normally.\n"
        )
    }

    memory_block = {
        "role": "system",
        "content": "PAST MEMORIES:\n" + "\n".join(f"- {m}" for m in memories)
    } if memories else None

    messages = [system_message]

    if memory_block:
        messages.append(memory_block)

    messages.extend(history)

    return messages
