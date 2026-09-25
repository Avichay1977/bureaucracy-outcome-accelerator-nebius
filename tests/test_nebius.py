import json
import os
import unittest
from unittest.mock import patch

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nebius_client

class FakeResponse:
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self):
        body = {"choices":[{"message":{"content":json.dumps({
            "blocker":"missing decision",
            "controller":"authority",
            "next_action":"ask for exact blocking condition",
            "evidence_needed":["official status"],
            "verify":"status advances",
            "fallback":"request named controller"
        })}}]}
        return json.dumps(body).encode("utf-8")

class NebiusClientTests(unittest.TestCase):
    def test_no_key_uses_no_remote_call(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(nebius_client.reason_with_nebius("goal"))

    def test_runtime_call_parses_nemotron_json(self):
        env={"NEBIUS_API_KEY":"test-key","NEBIUS_MODEL":"nvidia/nemotron-3-super-120b-a12b"}
        with patch.dict(os.environ, env, clear=True):
            with patch("nebius_client.request.urlopen", return_value=FakeResponse()) as mocked:
                result=nebius_client.reason_with_nebius("advance permit", ["case open"], [])
        self.assertEqual(result["reasoning_provider"], "Nebius Token Factory")
        self.assertEqual(result["controller"], "authority")
        req=mocked.call_args.args[0]
        payload=json.loads(req.data.decode("utf-8"))
        self.assertEqual(payload["model"], "nvidia/nemotron-3-super-120b-a12b")
        self.assertTrue(req.full_url.endswith("/chat/completions"))

if __name__ == "__main__":
    unittest.main()