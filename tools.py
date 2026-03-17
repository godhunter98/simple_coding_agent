import subprocess
from typing import Dict, Any
from pathlib import Path

from ui import (
    TOOL_COLOR,
    INFO_COLOR,
    RESET_COLOR,
    TOOL_ICON,
    SUCCESS_COLOR,
    SUCCESS_ICON,
    ERROR_COLOR,
    ERROR_ICON,
    FILE_ICON,
    DIR_ICON,
)


def run_bash_command_tool(command: str) -> Dict[str, Any]:
    print(
        f"{TOOL_COLOR}{TOOL_ICON} Running bash command: {INFO_COLOR}{command}{RESET_COLOR}"
    )
    try:
        # Run the command and capture output
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, check=True
        )
        print(
            f"{SUCCESS_COLOR}{SUCCESS_ICON} Command executed successfully{RESET_COLOR}"
        )
        print(f"{INFO_COLOR}STDOUT:{RESET_COLOR} {result.stdout}")
        if result.stderr:
            print(f"{INFO_COLOR}STDERR:{RESET_COLOR} {result.stderr}")
        return {
            "command": command,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "success": True,
        }
    except subprocess.CalledProcessError as e:
        print(
            f"{ERROR_COLOR}{ERROR_ICON} Command failed with exit code {e.returncode}{RESET_COLOR}"
        )
        print(f"{INFO_COLOR}STDOUT:{RESET_COLOR} {e.stdout}")
        print(f"{INFO_COLOR}STDERR:{RESET_COLOR} {e.stderr}")
        return {
            "command": command,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "returncode": e.returncode,
            "success": False,
            "error": f"Command failed with exit code {e.returncode}",
        }


def run_existing_bash_script_tool(script_path: str) -> Dict[str, Any]:
    full_path = resolve_abs_path(script_path)
    print(
        f"{TOOL_COLOR}{TOOL_ICON} Running bash script: {INFO_COLOR}{script_path}{RESET_COLOR}"
    )
    try:
        # Run the script with bash
        result = subprocess.run(
            ["bash", str(full_path)], capture_output=True, text=True, check=True
        )
        print(
            f"{SUCCESS_COLOR}{SUCCESS_ICON} Script executed successfully{RESET_COLOR}"
        )
        print(f"{INFO_COLOR}STDOUT:{RESET_COLOR} {result.stdout}")
        if result.stderr:
            print(f"{INFO_COLOR}STDERR:{RESET_COLOR} {result.stderr}")
        return {
            "script_path": str(full_path),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "success": True,
        }
    except subprocess.CalledProcessError as e:
        print(
            f"{ERROR_COLOR}{ERROR_ICON} Script failed with exit code {e.returncode}{RESET_COLOR}"
        )
        print(f"{INFO_COLOR}STDOUT:{RESET_COLOR} {e.stdout}")
        print(f"{INFO_COLOR}STDERR:{RESET_COLOR} {e.stderr}")
        return {
            "script_path": str(full_path),
            "stdout": e.stdout,
            "stderr": e.stderr,
            "returncode": e.returncode,
            "success": False,
            "error": f"Script failed with exit code {e.returncode}",
        }


def resolve_abs_path(path_str: str) -> Path:
    path = Path(path_str).expanduser()
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    return path


def read_file_tool(filename: str) -> Dict[str, Any]:
    full_path = resolve_abs_path(filename)
    print(f"{TOOL_COLOR}{TOOL_ICON} Reading file: {INFO_COLOR}{filename}{RESET_COLOR}")
    try:
        with open(str(full_path), "r", encoding="utf-8") as f:
            content = f.read()
        return {"file_path": str(full_path), "content": content}
    except Exception as e:
        print(f"{ERROR_COLOR}{ERROR_ICON} Error reading file: {e}{RESET_COLOR}")
        return {"file_path": str(full_path), "content": "", "error": str(e)}


def list_file_tool(path: str) -> Dict[str, Any]:
    full_path = resolve_abs_path(path)
    print(
        f"{TOOL_COLOR}{TOOL_ICON} Listing directory: {INFO_COLOR}{full_path}{RESET_COLOR}"
    )
    all_files = []
    for item in full_path.iterdir():
        icon = FILE_ICON if item.is_file() else DIR_ICON
        all_files.append(
            {
                "icon": icon,
                "filename": item.name,
                "type": "file" if item.is_file() else "dir",
            }
        )
    return {"path": str(full_path), "files": all_files}


def edit_file_tool(path: str, old_str: str, new_str: str) -> Dict[str, Any]:
    full_path = resolve_abs_path(path)
    try:
        if old_str == "":
            print(
                f"{TOOL_COLOR}{TOOL_ICON} Creating file: {INFO_COLOR}{path}{RESET_COLOR}"
            )
            full_path.write_text(new_str, encoding="utf-8")
            print(
                f"{SUCCESS_COLOR}{SUCCESS_ICON} File created successfully{RESET_COLOR}"
            )
            return {"path": str(full_path), "action": "created_file"}

        original = full_path.read_text(encoding="utf-8")
        if original.find(old_str) == -1:
            print(
                f"{ERROR_COLOR}{ERROR_ICON} Text to replace not found in file{RESET_COLOR}"
            )
            return {"path": str(full_path), "action": "old_str not found"}

        print(f"{TOOL_COLOR}{TOOL_ICON} Editing file: {INFO_COLOR}{path}{RESET_COLOR}")
        edited = original.replace(old_str, new_str, 1)
        full_path.write_text(edited, encoding="utf-8")
        print(f"{SUCCESS_COLOR}{SUCCESS_ICON} File edited successfully{RESET_COLOR}")
        return {"path": str(full_path), "action": "edited"}
    except Exception as e:
        print(f"{ERROR_COLOR}{ERROR_ICON} Error editing file: {e}{RESET_COLOR}")
        return {"path": str(full_path), "action": "error", "error": str(e)}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Gets the full content of a file provided by the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "The name of the file to read.",
                    }
                },
                "required": ["filename"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_file",
            "description": "List all the files in a directory provided by the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path of the directory to list files from.",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Replaces the first instance of old_string in a file, with a new_string provided by the user",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path to the file to edit.",
                    },
                    "old_str": {
                        "type": "string",
                        "description": "The specific piece of string that you want to replace from the file.",
                    },
                    "new_str": {
                        "type": "string",
                        "description": "The new string that you want to replace the old string with.",
                    },
                },
                "required": ["path", "old_str", "new_str"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_bash_command",
            "description": "Executes a bash command in the shell and returns the output.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The bash command to execute.",
                    }
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_existing_bash_script",
            "description": "Runs an existing bash script file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "script_path": {
                        "type": "string",
                        "description": "The path to the bash script file to execute.",
                    }
                },
                "required": ["script_path"],
            },
        },
    },
]
