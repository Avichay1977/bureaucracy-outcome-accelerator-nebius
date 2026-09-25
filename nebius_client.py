import json
import os
from urllib import request, error

DEFAULT_BASE_URL = "https://api.tokenfactory.nebius.com/v1"
DEFAULT_MODEL = "nvidia/nemotron-3-super-120b-a12b"

SYSTEM_PROMPT = """You are the reasoning engine inside Bureaucracy Outcome Accelerator.
Work backward from a real-world bureaucratic goal to the earliest unresolved decision dependency.
Return JSON only with these keys: blocker, controller, next_action, evidence_needed, verify, fallback.
evidence_needed must be an array of short strings.
Choose exactly one smallest safe next action. Never claim an external action was performed."""

def _extract_json(text):
    text = (text or "").strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return json.loads(text)

def reason_with_nebius(goal, facts=None, constraints=None, timeout=45):
    api_key = os.environ.get("NEBIUS_API_KEY", "").strip()
    if not api_key:
        return None
    base_url = os.environ.get("NEBIUS_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    model = os.environ.get("NEBIUS_MODEL", DEFAULT_MODEL)
    payload = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps({
                "goal": goal,
                "known_facts": facts or [],
                "constraints": constraints or []
            }, ensure_ascii=False)}
        ]
    }
    req = request.Request(
        base_url + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json"
        },
        method="POST"
    )
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        content = data["choices"][0]["message"]["content"]
        result = _extract_json(content)
        required = {"blocker", "controller", "next_action", "evidence_needed", "verify", "fallback"}
        if not required.issubset(result):
            raise ValueError("Nebius response is missing required fields")
        if not isinstance(result["evidence_needed"], list):
            raise ValueError("evidence_needed must be a list")
        result["reasoning_provider"] = "Nebius Token Factory"
        result["reasoning_model"] = model
        return result
    except (error.URLError, TimeoutError, KeyError, ValueError, json.JSONDecodeError) as exc:
        raise RuntimeError("Nebius reasoning call failed: " + str(exc)) from exc