from typing import Any,List,Dict
  
def mask_old_observations(conversation:list,keep_last_n:int=20):
    """Mask the content of older tool-response messages to reduce context size.

    Replaces the ``content`` of tool-role messages that fall outside the most
    recent *last_n_turns* tool responses with a short placeholder string,
    preserving the message structure so the conversation history stays valid
    for the LLM. Messages shorter than 300 characters are left untouched,
    and already-masked messages are skipped to avoid redundant work.

    Note:
        This function mutates *conversation* in place; it does not return a
        new list.

    Args:
        conversation (list): The full conversation history — a list of
            message dicts, each containing at least ``role`` and ``content``
            keys.  Only entries with ``role == "tool"`` are candidates for
            masking.
        last_n_turns (int, optional): The number of most-recent tool
            messages to keep unmasked.  Set to ``0`` or a negative value to
            mask *all* tool messages.  Defaults to ``20``.
    """
    tool_idx = [idx for idx,turn_message in enumerate(conversation) if turn_message["role"] == "tool"]
    if  keep_last_n<=0:
        required_slice = tool_idx
    else:
        required_slice = tool_idx[:-keep_last_n]
    for i in required_slice:
        tool_message = conversation[i]
        
        if tool_message.get("masked"):
            continue
        
        tool_message_length = len(tool_message["content"])
        tool_message_name= tool_message["name"]
        if tool_message_length > 300:
            tool_message["content"] = f"[observation masked | tool={tool_message_name} | {tool_message_length} chars hidden]"
            
            # flag to avoid idempotency
            tool_message["masked"] = True


def truncate_tool_output(content_str: str, tool_name: str) -> str:
    # 1. For reading files, allow a larger limit to prevent missing code
    if tool_name == "read_file":
        limit = 35_000
        if len(content_str) > limit:
            return content_str[:limit] + f"\n... [File content truncated: {len(content_str) - limit} characters omitted for context space] ..."
            
    # 2. For bash executions, keep a moderate limit but keep the END of the output
    # (since stack traces and summaries are usually at the bottom)
    elif tool_name in ["run_bash_command", "run_existing_bash_script"]:
        limit = 10_000
        if len(content_str) > limit:
            return f"... [First {len(content_str) - limit} characters truncated for context space] ...\n" + content_str[-limit:]

    # 3. For edits, the response is just a confirmation — keep it small
    elif tool_name == "edit_file":
        limit = 2_000
        if len(content_str) > limit:
            return content_str[:limit] + f"\n... [Truncated {len(content_str) - limit} characters] ..."

    # 4. For other tools (like listing files)
    else:
        limit = 5_000
        if len(content_str) > limit:
            return content_str[:limit] + f"\n... [Truncated {len(content_str) - limit} characters] ..."
            
    return content_str

def prune_conversation(conversation:List[Dict[str,Any]]):
    # needs to be implemented laterr
    pass
