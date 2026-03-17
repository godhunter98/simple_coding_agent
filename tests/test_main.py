import sys
import types
import unittest
from unittest import mock


class TestMain(unittest.TestCase):
    def test_main_calls_agent_loop(self):
        litellm_stub = types.ModuleType("litellm")
        litellm_stub.litellm = types.SimpleNamespace(completion=lambda **_kwargs: None)
        dotenv_stub = types.ModuleType("dotenv")
        dotenv_stub.load_dotenv = lambda: None
        sys.modules["litellm"] = litellm_stub
        sys.modules["dotenv"] = dotenv_stub

        sys.modules.pop("basic_coding_agent", None)
        sys.modules.pop("main", None)

        import main

        with mock.patch.object(main, "agent_loop") as mock_loop:
            main.main()
            mock_loop.assert_called_once()


if __name__ == "__main__":
    unittest.main()
