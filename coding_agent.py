import os
import warnings
import logging
from dotenv import load_dotenv
from typing import Any, Dict, List
from litellm import litellm
import json
from tools import (
    TOOLS,
    read_file_tool,
    list_file_tool,
    edit_file_tool,
    run_bash_command_tool,
    run_existing_bash_script_tool,
)
from prompts import SYSTEM_PROMPT
from animation import Spinner
from ui import (
    YOU_COLOR,
    ASSISTANT_COLOR,
    TOOL_COLOR,
    ERROR_COLOR,
    SUCCESS_COLOR,
    INFO_COLOR,
    RESET_COLOR,
    TOOL_ICON,
    SUCCESS_ICON,
    ERROR_ICON,
    THINKING_ICON,
)

# Disable pydantic warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
os.environ["LITELLM_IGNORE_PYDANTIC_WARNINGS"] = "1"

# Silence litellm logs
logging.getLogger("litellm").setLevel(logging.WARNING)
os.environ["LITELLM_LOG"] = "ERROR"


load_dotenv()

llm_config = {}


if os.environ.get("API_BASE"):
    llm_config["api_base"] = os.environ["API_BASE"]


tool_registry = {
    "read_file": read_file_tool,
    "list_file": list_file_tool,
    "edit_file": edit_file_tool,
    "run_bash_command": run_bash_command_tool,
    "run_existing_bash_script": run_existing_bash_script_tool,
}


def build_messages(conversation: List[Dict[str, str]]) -> List[Dict[str, str]]:
    messages: List[Dict[str, str]] = []
    for msg in conversation:
        if msg["role"] == "system":
            messages.append({"role": "system", "content": msg["content"]})
        else:
            messages.append(msg)
    return messages


def print_error(context: str, message: str) -> None:
    print(f"{ERROR_COLOR}{ERROR_ICON} {context}: {message}{RESET_COLOR}")


def llm_completions(conversation: List[Dict[str, str]], model: str, api_key: str):
    messages = build_messages(conversation)
    if model and api_key is not None:
        kwargs = {
            "model": model,
            "api_key": api_key,
            "messages": messages,
            "max_tokens": 2000,
            "temperature": 0.1,
            "tools": TOOLS,
        }

        # Allow overriding the LLM base URL without changing call sites.
        if llm_config.get("api_base"):
            kwargs["api_base"] = llm_config["api_base"]
        try:
            response = litellm.completion(**kwargs)
            return response
        except Exception as e:
            error_msg = f"LLM call failed: {str(e)}"
            print_error("LLM error", error_msg)
            print(
                f"{INFO_COLOR}Make sure you have set up your API keys in the .env file{RESET_COLOR}"
            )
            print(f"{INFO_COLOR}Current model: {model}{RESET_COLOR}")
            return f"I encountered an error: {error_msg}. Please check your API key configuration."
    else:
        error_msg = "Missing environment variable: MODEL or API_KEY"
        print_error("Configuration error", error_msg)
        print(
            f"{INFO_COLOR}Please set MODEL and API_KEY in your .env file{RESET_COLOR}"
        )
        return f"I encountered an error: {error_msg}. Please check your .env file configuration."


def run_tool_call(
    tool_call, conversation: List[Dict[str, Any]], index: int
) -> None:
    tool_name = tool_call.function.name
    try:
        # Tool arguments arrive as JSON strings in the model response.
        tool_args = json.loads(tool_call.function.arguments)
        args_display = ", ".join(f"{k}={v}" for k, v in tool_args.items())
        print(f"  {index}. {TOOL_ICON} {tool_name}({args_display})")

        tool = tool_registry.get(tool_name)
        if not tool:
            error_msg = f"Unknown tool: {tool_name}"
            print_error("Tool error", error_msg)
            conversation.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps({"error": error_msg}),
                }
            )
            return

        try:
            resp = tool(**tool_args)
            conversation.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(resp),
                }
            )
        except Exception as e:
            error_msg = f"Tool execution failed: {str(e)}"
            print_error("Tool error", error_msg)
            conversation.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps({"error": error_msg}),
                }
            )

    except json.JSONDecodeError:
        print("The model sent back a broken JSON string!")

def handle_assistant_message(assistant_message, conversation: List[Dict[str, Any]]) -> None:
    content = getattr(assistant_message, "content", "") or ""
    tool_calls = getattr(assistant_message, "tool_calls", None) or []

    if content.strip():
        print(f"{ASSISTANT_COLOR}Assistant:{RESET_COLOR} {content}")

    if not tool_calls:
        conversation.append({"role": "assistant", "content": content})
        return 

    # Preserve the model's assistant message before executing any tool calls.
    conversation.append(
        {
            "role": "assistant",
            "content": content,
            "tool_calls": tool_calls,  # type: ignore
        }
    )

    print(
        f"{TOOL_COLOR}🔄 Executing {len(tool_calls)} tool{'s' if len(tool_calls) > 1 else ''}...{RESET_COLOR}"
    )

    for index, tool_call in enumerate(tool_calls, 1):
        run_tool_call(tool_call, conversation, index)


def agent_loop(model: str, api_key: str):
    print(
        f"{SUCCESS_COLOR}{SUCCESS_ICON} Spinning up agent...{RESET_COLOR}"
    )
    print(f"{INFO_COLOR}Type 'exit' or press Ctrl+C to quit.{RESET_COLOR}\n")

    conversation = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    while True:
        try:
            user_input = input(f"\n{YOU_COLOR}You:{RESET_COLOR} ")
        except (KeyboardInterrupt, EOFError):
            print(f"\n{INFO_COLOR}Goodbye! 👋{RESET_COLOR}")
            break

        if not user_input.strip():
            continue

        if user_input.lower() in ["exit", "quit"]:
            print(f"\n{INFO_COLOR}Goodbye! 👋{RESET_COLOR}")
            break

        conversation.append({"role": "user", "content": user_input.strip()})

        spinner = Spinner()
        spinner.start()

        while True:
            response = llm_completions(conversation, model, api_key)
            spinner.stop()
            if isinstance(response, str):
                print(f"{ASSISTANT_COLOR}Assistant:{RESET_COLOR} {response}")
                break

            # to understand what is going on here, go and read the liteLLM response json format.
            try:
                if hasattr(response, "choices") and response.choices:  # type: ignore
                    # Only the first choice is used for this CLI loop.
                    assistant_message = response.choices[0].message  # type: ignore
                    # The response is being generated by the assistant, depending on whether there are tool calls or not.
                    handle_assistant_message(assistant_message,conversation)
                    if not assistant_message.tool_calls:
                        break
                    spinner.start()
                    continue                                     

                else:
                    # Fallback for unexpected response format
                    content = str(response)
                    print(f"{ASSISTANT_COLOR}Assistant:{RESET_COLOR} {content}")
                    conversation.append({"role": "assistant", "content": content})
                    break

            except Exception as e:
                print(
                    f"{ERROR_COLOR}{ERROR_ICON} Error processing response: {e}{RESET_COLOR}"
                )
                print(
                    f"{ASSISTANT_COLOR}Assistant:{RESET_COLOR} I encountered an error processing the response."
                )
                break


if __name__ == "__main__":
    agent_loop(model=os.getenv("MODEL",""),api_key=os.getenv("API_KEY",""))
