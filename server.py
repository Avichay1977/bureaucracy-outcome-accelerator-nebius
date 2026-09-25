#!/usr/bin/env python3
import argparse
import json
import re
import secrets
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from nebius_client import reason_with_nebius

PROTOCOL_VERSION = "2025-11-25"
SERVER_INFO = {"name": "bureaucracy-outcome-accelerator", "version": "0.4.0-nebius"}
SESSIONS = {}

TOOLS = [
    {
        "name": "break_bureaucracy",
        "description": "Turn a bureaucratic goal into the smallest safe next action and a verification rule.",
        "inputSchema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "goal": {"type": "string", "minLength": 3},
                "known_facts": {"type": "array", "items": {"type": "string"}},
                "constraints": {"type": "array", "items": {"type": "string"}},
                "case_id": {"type": "string"}
            },
            "required": ["goal"]
        }
    },
    {
        "name": "record_outcome",
        "description": "Record what happened after the last action and reroute the case if the outcome is not verified.",
        "inputSchema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "case_id": {"type": "string"},
                "outcome": {"type": "string"},
                "verified": {"type": "boolean"}
            },
            "required": ["case_id", "outcome", "verified"]
        }
    },
    {
        "name": "case_status",
        "description": "Return the current compact state for a case.",
        "inputSchema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {"case_id": {"type": "string"}},
            "required": ["case_id"]
        }
    }
]

def compact_case_id(goal: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", goal.lower()).strip("-")[:28]
    return slug or secrets.token_hex(4)

def classify_heuristic(goal: str, facts):
    text = (goal + " " + " ".join(facts)).lower()
    if any(k in text for k in ["bin", "waste", "trash", "garbage", "פח", "אשפה"]):
        return {
            "blocker": "A concrete service decision has not yet been converted into a verified physical outcome.",
            "controller": "Municipal waste / sanitation operations",
            "next_action": "Ask the responsible operations contact to confirm the exact placement date and location for the additional bin.",
            "evidence_needed": ["Named responsible contact", "Placement date or work order", "Exact location"],
            "verify": "Confirm the bin is physically present at the agreed location; an agreement alone is not success.",
            "fallback": "If no placement date is provided, request the work-order/reference number and escalate only that unresolved dependency."
        }
    if any(k in text for k in ["benefit", "allowance", "social security", "קצבה", "ביטוח לאומי", "זכאות"]):
        return {
            "blocker": "Eligibility cannot be acted on until the missing decision or document requirement is identified.",
            "controller": "Benefits authority / case officer",
            "next_action": "Request the current case status and the single missing item preventing a decision.",
            "evidence_needed": ["Case/reference number", "Current official status", "Exact missing document or decision"],
            "verify": "Verify that the authority marks the missing requirement as received or the case advances to a decision stage.",
            "fallback": "If the answer is generic, ask for the exact unresolved requirement and the department currently holding the case."
        }
    if any(k in text for k in ["permit", "license", "approval", "היתר", "רישיון", "אישור"]):
        return {
            "blocker": "The active prerequisite gate is not yet identified or evidenced as complete.",
            "controller": "Approving authority / permit reviewer",
            "next_action": "Ask which prerequisite currently prevents the application from advancing and request the official status of that prerequisite.",
            "evidence_needed": ["Application/reference number", "Named prerequisite", "Official status or decision"],
            "verify": "Verify the prerequisite is explicitly marked complete and the case advances to the next stage.",
            "fallback": "If several prerequisites are listed, resolve the earliest blocking gate first rather than working all of them in parallel."
        }
    return {
        "blocker": "The next decision dependency is not yet explicit.",
        "controller": "The person or institution that controls the next required decision",
        "next_action": "Ask for the exact condition that must become true for the case to advance, and who controls that condition.",
        "evidence_needed": ["Current official status", "Next required condition", "Responsible controller"],
        "verify": "Verify the condition changed in the source system or through an official confirmation.",
        "fallback": "If the response does not name a condition, ask for the current blocking requirement rather than requesting a general status update."
    }


def classify(goal: str, facts, constraints=None):
    try:
        result = reason_with_nebius(goal, facts, constraints or [])
        if result:
            return result
    except RuntimeError as exc:
        failure = str(exc)
    else:
        failure = None
    result = classify_heuristic(goal, facts)
    result["reasoning_provider"] = "local heuristic fallback"
    if failure:
        result["reasoning_error"] = failure
    return result

def call_tool(session_id, name, args):
    session = SESSIONS.setdefault(session_id, {"cases": {}})
    if name == "break_bureaucracy":
        goal = str(args.get("goal", "")).strip()
        if len(goal) < 3:
            raise ValueError("goal must contain at least 3 characters")
        facts = args.get("known_facts") or []
        constraints = args.get("constraints") or []
        case_id = (args.get("case_id") or compact_case_id(goal))[:64]
        plan = classify(goal, facts, constraints)
        case = {
            "case_id": case_id,
            "goal": goal,
            "known_facts": facts,
            "constraints": constraints,
            "status": "ACTION_NOW",
            **plan,
            "last_outcome": None,
            "verified": False
        }
        session["cases"][case_id] = case
        return case
    if name == "record_outcome":
        cid = args.get("case_id")
        if cid not in session["cases"]:
            raise ValueError("unknown case_id")
        case = session["cases"][cid]
        case["last_outcome"] = args.get("outcome", "")
        case["verified"] = bool(args.get("verified"))
        if case["verified"]:
            case["status"] = "VERIFIED_OUTCOME"
            case["next_action"] = "No further action. Preserve the proof of outcome."
        else:
            case["status"] = "REROUTE"
            case["next_action"] = case["fallback"]
        return case
    if name == "case_status":
        cid = args.get("case_id")
        if cid not in session["cases"]:
            raise ValueError("unknown case_id")
        return session["cases"][cid]
    raise ValueError("unknown tool")

class Handler(BaseHTTPRequestHandler):
    server_version = "BureaucracyMCP/0.3"

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args))

    def _origin_allowed(self):
        origin = self.headers.get("Origin")
        if not origin:
            return True
        try:
            host = urlparse(origin).hostname
        except Exception:
            return False
        return host in {"localhost", "127.0.0.1", "::1"}

    def _send_json(self, status, obj, extra_headers=None):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", self.headers.get("Origin", "http://localhost"))
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept, Mcp-Session-Id, MCP-Protocol-Version")
        self.send_header("Access-Control-Expose-Headers", "Mcp-Session-Id, MCP-Protocol-Version")
        self.send_header("MCP-Protocol-Version", PROTOCOL_VERSION)
        for k, v in (extra_headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", self.headers.get("Origin", "http://localhost"))
        self.send_header("Access-Control-Allow-Methods", "POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept, Mcp-Session-Id, MCP-Protocol-Version")
        self.end_headers()

    def do_GET(self):
        if self.path == "/health":
            return self._send_json(200, {"ok": True, "protocolVersion": PROTOCOL_VERSION})
        if self.path == "/":
            self.path = "/web/index.html"
        if self.path.startswith("/web/"):
            import os
            path = self.path.split("?",1)[0]
            rel = path[len("/web/"):]
            root = os.path.join(os.path.dirname(__file__), "web")
            target = os.path.abspath(os.path.join(root, rel))
            if not target.startswith(os.path.abspath(root)) or not os.path.isfile(target):
                return self.send_error(404)
            ctype = "text/html; charset=utf-8" if target.endswith(".html") else "text/plain; charset=utf-8"
            if target.endswith(".css"): ctype = "text/css; charset=utf-8"
            if target.endswith(".js"): ctype = "application/javascript; charset=utf-8"
            data = open(target,"rb").read()
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers(); self.wfile.write(data); return
        if self.path == "/mcp":
            return self._send_json(405, {"error": "GET is not used by this MCP server; use POST for JSON-RPC."})
        self.send_error(404)

    def do_DELETE(self):
        if self.path != "/mcp": return self.send_error(404)
        sid = self.headers.get("Mcp-Session-Id")
        if sid and sid in SESSIONS:
            del SESSIONS[sid]
            return self._send_json(200, {"closed": True})
        return self._send_json(404, {"closed": False, "error": "unknown session"})

    def do_POST(self):
        if self.path != "/mcp": return self.send_error(404)
        if not self._origin_allowed():
            return self._send_json(403, {"error": "Origin not allowed"})
        ctype = self.headers.get("Content-Type", "")
        if "application/json" not in ctype:
            return self._send_json(415, {"error": "Content-Type must be application/json"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            return self._send_json(400, {"jsonrpc":"2.0","id":None,"error":{"code":-32700,"message":"Parse error"}})
        if not isinstance(data, dict) or data.get("jsonrpc") != "2.0":
            return self._send_json(400, {"jsonrpc":"2.0","id":data.get("id") if isinstance(data,dict) else None,"error":{"code":-32600,"message":"Invalid Request"}})
        rid = data.get("id")
        method = data.get("method")
        params = data.get("params") or {}
        if method == "notifications/initialized":
            self.send_response(202); self.end_headers(); return
        if method == "initialize":
            sid = secrets.token_urlsafe(18)
            SESSIONS[sid] = {"cases": {}}
            result = {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": SERVER_INFO
            }
            return self._send_json(200, {"jsonrpc":"2.0","id":rid,"result":result}, {"Mcp-Session-Id": sid})
        sid = self.headers.get("Mcp-Session-Id")
        if not sid or sid not in SESSIONS:
            return self._send_json(400, {"jsonrpc":"2.0","id":rid,"error":{"code":-32001,"message":"Missing or invalid Mcp-Session-Id"}})
        client_version = self.headers.get("MCP-Protocol-Version")
        if client_version and client_version != PROTOCOL_VERSION:
            return self._send_json(400, {"jsonrpc":"2.0","id":rid,"error":{"code":-32002,"message":"Unsupported MCP-Protocol-Version"}})
        try:
            if method == "tools/list":
                result = {"tools": TOOLS}
            elif method == "tools/call":
                name = params.get("name")
                args = params.get("arguments") or {}
                payload = call_tool(sid, name, args)
                result = {"content": [{"type":"text","text":json.dumps(payload, ensure_ascii=False, indent=2)}], "structuredContent": payload, "isError": False}
            elif method == "ping":
                result = {}
            else:
                return self._send_json(200, {"jsonrpc":"2.0","id":rid,"error":{"code":-32601,"message":"Method not found"}})
            return self._send_json(200, {"jsonrpc":"2.0","id":rid,"result":result})
        except ValueError as e:
            return self._send_json(200, {"jsonrpc":"2.0","id":rid,"error":{"code":-32602,"message":str(e)}})
        except Exception as e:
            return self._send_json(200, {"jsonrpc":"2.0","id":rid,"error":{"code":-32603,"message":"Internal error"}})

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8765)
    args = ap.parse_args()
    print(f"Bureaucracy Outcome Accelerator MCP {PROTOCOL_VERSION} on http://{args.host}:{args.port}")
    ThreadingHTTPServer((args.host,args.port), Handler).serve_forever()

if __name__ == "__main__":
    main()