import pathlib
import tempfile
from tools import is_unsafe, read_file, edit_file, list_file, run_bash_command, run_existing_bash_script
from unittest.mock import patch

def test_is_unsafe():
    assert is_unsafe("rm -rf/") is True
    assert is_unsafe("rm -rf /") is True
    assert is_unsafe("ls -la") is False
    assert is_unsafe("sudo apt install") is True
    assert is_unsafe("echo hello") is False

def test_list_file():
    with tempfile.TemporaryDirectory() as temp_directory:
        path = pathlib.Path(temp_directory)
        result = list_file(path)
        with tempfile.NamedTemporaryFile(dir=path) as temp_file:
            new_result = list_file(path)
            assert len(new_result["files"]) == 1
            assert new_result["files"][0]["filename"] == pathlib.Path(temp_file.name).name

        assert result["path"] == str(path)
             

def test_read_file():
    with tempfile.NamedTemporaryFile() as temp_file:
        temp_file.write(b"Hello World, how you doing?")
        temp_file.flush()
        result = read_file(temp_file.name)
        assert result["content"] =="Hello World, how you doing?"
        assert result["file_path"] == temp_file.name
    file = "path/to/nothing.txt"
    result = read_file(file)
    assert "No such file or directory" in result['error']


def test_edit_file():
    with tempfile.NamedTemporaryFile() as temp_file:
        temp_file.write(b"Hello World, Whats up?")
        temp_file.flush()
        old_str = "World"
        new_str = "Harsh"
        result = edit_file(temp_file.name,old_str,new_str)
        assert result['path'] == temp_file.name
        assert result['action'] == "edited"

        read_result = read_file(temp_file.name)
        assert read_result["content"] == "Hello Harsh, Whats up?"

        old_str = ''
        result_new = edit_file(temp_file.name,old_str,new_str)
        assert result_new['path'] == temp_file.name
        assert result_new['action'] == "created_file"

        missing_str = 'Bananas'
        result_not_found = edit_file(temp_file.name,missing_str,"Apples")
        assert result_not_found["action"] == "old_str not found"

        read_final = read_file(temp_file.name)
        assert missing_str not in read_final["content"]

        # Test Empty Path
        result_empty = edit_file("", "old", "new")
        assert result_empty["action"] == "error"
        assert "Is a directory" in result_empty["error"]


@patch("builtins.input",return_value="n")
def test_unsafe_bash_command_unconfirmed(mock_input):
    with tempfile.NamedTemporaryFile() as temp_file:
        result = run_bash_command(f"rm -rf {temp_file.name}")
        assert result["success"] is False
        assert result["error"] == "Cancelled by user"

@patch("tools.subprocess.run")
@patch("builtins.input",return_value="y")
def test_unsafe_bash_command_confirmed(mock_input,mock_subprocess):
    mock_subprocess.return_value.stdout = "Fake output"
    mock_subprocess.return_value.stderr = ""
    mock_subprocess.return_value.returncode = 0
    with tempfile.NamedTemporaryFile() as temp_file:
        result = run_bash_command(f"rm -rf {temp_file.name}")
        assert result["success"] is True
        mock_subprocess.assert_called_once()

