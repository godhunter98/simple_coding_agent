from unittest import result
import tempfile
from tools import is_unsafe, read_file, edit_file

def test_is_unsafe():
    assert is_unsafe("rm -rf/") is True
    assert is_unsafe("rm -rf /") is True
    assert is_unsafe("ls -la") is False
    assert is_unsafe("sudo apt install") is True
    assert is_unsafe("echo hello") is False

def test_read_file():
    import tempfile, pathlib, os  # noqa: E401
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