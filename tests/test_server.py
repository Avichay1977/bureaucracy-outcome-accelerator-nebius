import json, os, subprocess, sys, time, unittest
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ROOT=os.path.dirname(os.path.dirname(__file__))
PORT=8877
BASE=f"http://127.0.0.1:{PORT}"

def req(method,path,body=None,headers=None):
    data=None if body is None else json.dumps(body).encode()
    h={"Content-Type":"application/json","Accept":"application/json, text/event-stream",**(headers or {})}
    r=Request(BASE+path,data=data,headers=h,method=method)
    try:
        with urlopen(r,timeout=3) as x:
            raw=x.read(); return x.status, dict(x.headers), json.loads(raw or b"{}")
    except HTTPError as e:
        raw=e.read(); return e.code,dict(e.headers),json.loads(raw or b"{}")

class MCPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=subprocess.Popen([sys.executable,os.path.join(ROOT,"server.py"),"--port",str(PORT)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        for _ in range(40):
            try:
                if req("GET","/health")[0]==200:return
            except Exception: pass
            time.sleep(.1)
        raise RuntimeError("server did not start")
    @classmethod
    def tearDownClass(cls): cls.p.terminate(); cls.p.wait(timeout=3)
    def initialize(self):
        s,h,b=req("POST","/mcp",{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"test","version":"1"}}})
        return h.get("Mcp-Session-Id"),b
    def test_01_health(self): self.assertEqual(req("GET","/health")[0],200)
    def test_02_get_mcp_rejected(self): self.assertEqual(req("GET","/mcp")[0],405)
    def test_03_initialize(self):
        sid,b=self.initialize(); self.assertTrue(sid); self.assertEqual(b["result"]["protocolVersion"],"2025-11-25")
    def test_04_tools_list(self):
        sid,_=self.initialize(); s,h,b=req("POST","/mcp",{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}},{"Mcp-Session-Id":sid,"MCP-Protocol-Version":"2025-11-25"}); self.assertEqual(len(b["result"]["tools"]),4)
    def test_05_missing_session(self):
        s,h,b=req("POST","/mcp",{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}); self.assertEqual(s,400)
    def test_06_wrong_version(self):
        sid,_=self.initialize(); s,h,b=req("POST","/mcp",{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}},{"Mcp-Session-Id":sid,"MCP-Protocol-Version":"1999-01-01"}); self.assertEqual(s,400)
    def test_07_origin_block(self):
        s,h,b=req("POST","/mcp",{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}},{"Origin":"https://evil.example"}); self.assertEqual(s,403)
    def test_08_break_case(self):
        sid,_=self.initialize(); s,h,b=req("POST","/mcp",{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"break_bureaucracy","arguments":{"goal":"Add one more waste bin","known_facts":["official agreed"]}}},{"Mcp-Session-Id":sid,"MCP-Protocol-Version":"2025-11-25"}); c=b["result"]["structuredContent"]; self.assertEqual(c["status"],"WAITING_APPROVAL"); self.assertIn("physically",c["verify"])
    def test_09_stateful_reroute(self):
        sid,_=self.initialize()
        _,_,b=req("POST","/mcp",{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"break_bureaucracy","arguments":{"goal":"Add waste bin","case_id":"demo"}}},{"Mcp-Session-Id":sid,"MCP-Protocol-Version":"2025-11-25"})
        c=b["result"]["structuredContent"]
        self.assertEqual(req("POST","/approve",{"session_id":sid,"case_id":"demo","fingerprint":c["action_fingerprint"]})[0],200)
        req("POST","/mcp",{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"resume_case","arguments":{"case_id":"demo"}}},{"Mcp-Session-Id":sid,"MCP-Protocol-Version":"2025-11-25"})
        _,_,b=req("POST","/mcp",{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"record_outcome","arguments":{"case_id":"demo","outcome":"not placed","verified":False}}},{"Mcp-Session-Id":sid,"MCP-Protocol-Version":"2025-11-25"})
        self.assertEqual(b["result"]["structuredContent"]["status"],"WAITING_APPROVAL")
    def test_10_verified(self):
        sid,_=self.initialize()
        _,_,b=req("POST","/mcp",{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"break_bureaucracy","arguments":{"goal":"Get permit","case_id":"p"}}},{"Mcp-Session-Id":sid,"MCP-Protocol-Version":"2025-11-25"})
        c=b["result"]["structuredContent"]
        self.assertEqual(req("POST","/approve",{"session_id":sid,"case_id":"p","fingerprint":c["action_fingerprint"]})[0],200)
        req("POST","/mcp",{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"resume_case","arguments":{"case_id":"p"}}},{"Mcp-Session-Id":sid,"MCP-Protocol-Version":"2025-11-25"})
        _,_,b=req("POST","/mcp",{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"record_outcome","arguments":{"case_id":"p","outcome":"permit issued","verified":True}}},{"Mcp-Session-Id":sid,"MCP-Protocol-Version":"2025-11-25"})
        self.assertEqual(b["result"]["structuredContent"]["status"],"VERIFIED_OUTCOME")
    def test_11_delete_session(self):
        sid,_=self.initialize(); self.assertEqual(req("DELETE","/mcp",headers={"Mcp-Session-Id":sid})[0],200)

    def test_12_resume_without_approval_blocked(self):
        sid,_=self.initialize()
        req("POST","/mcp",{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"break_bureaucracy","arguments":{"goal":"Get permit","case_id":"no-approval"}}},{"Mcp-Session-Id":sid,"MCP-Protocol-Version":"2025-11-25"})
        _,_,b=req("POST","/mcp",{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"resume_case","arguments":{"case_id":"no-approval"}}},{"Mcp-Session-Id":sid,"MCP-Protocol-Version":"2025-11-25"})
        self.assertIn("valid external human approval required",b["error"]["message"])

    def test_13_wrong_fingerprint_blocked(self):
        sid,_=self.initialize()
        req("POST","/mcp",{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"break_bureaucracy","arguments":{"goal":"Get permit","case_id":"bad-fp"}}},{"Mcp-Session-Id":sid,"MCP-Protocol-Version":"2025-11-25"})
        status,_,body=req("POST","/approve",{"session_id":sid,"case_id":"bad-fp","fingerprint":"wrong"})
        self.assertEqual(status,409)
        self.assertFalse(body["approved"])

    def test_14_valid_approval_resumes_exact_action(self):
        sid,_=self.initialize()
        _,_,b=req("POST","/mcp",{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"break_bureaucracy","arguments":{"goal":"Get permit","case_id":"resume-exact"}}},{"Mcp-Session-Id":sid,"MCP-Protocol-Version":"2025-11-25"})
        c=b["result"]["structuredContent"]
        original_action=c["next_action"]
        self.assertEqual(req("POST","/approve",{"session_id":sid,"case_id":"resume-exact","fingerprint":c["action_fingerprint"]})[0],200)
        _,_,b=req("POST","/mcp",{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"resume_case","arguments":{"case_id":"resume-exact"}}},{"Mcp-Session-Id":sid,"MCP-Protocol-Version":"2025-11-25"})
        resumed=b["result"]["structuredContent"]
        self.assertEqual(resumed["status"],"AWAITING_VERIFICATION")
        self.assertEqual(resumed["next_action"],original_action)

    def test_15_verified_after_gate_is_terminal(self):
        sid,_=self.initialize()
        _,_,b=req("POST","/mcp",{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"break_bureaucracy","arguments":{"goal":"Get permit","case_id":"terminal"}}},{"Mcp-Session-Id":sid,"MCP-Protocol-Version":"2025-11-25"})
        c=b["result"]["structuredContent"]
        req("POST","/approve",{"session_id":sid,"case_id":"terminal","fingerprint":c["action_fingerprint"]})
        req("POST","/mcp",{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"resume_case","arguments":{"case_id":"terminal"}}},{"Mcp-Session-Id":sid,"MCP-Protocol-Version":"2025-11-25"})
        _,_,b=req("POST","/mcp",{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"record_outcome","arguments":{"case_id":"terminal","outcome":"permit issued","verified":True}}},{"Mcp-Session-Id":sid,"MCP-Protocol-Version":"2025-11-25"})
        c=b["result"]["structuredContent"]
        self.assertEqual(c["status"],"VERIFIED_OUTCOME")
        self.assertEqual(c["gate_state"],"COMPLETED")

    def test_16_outcome_before_approval_blocked(self):
        sid,_=self.initialize()
        req("POST","/mcp",{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"break_bureaucracy","arguments":{"goal":"Get permit","case_id":"skip-gate"}}},{"Mcp-Session-Id":sid,"MCP-Protocol-Version":"2025-11-25"})
        _,_,b=req("POST","/mcp",{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"record_outcome","arguments":{"case_id":"skip-gate","outcome":"pretend done","verified":True}}},{"Mcp-Session-Id":sid,"MCP-Protocol-Version":"2025-11-25"})
        self.assertIn("approval and resume are required",b["error"]["message"])

if __name__=='__main__': unittest.main(verbosity=2)