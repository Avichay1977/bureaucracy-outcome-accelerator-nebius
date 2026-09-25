let sessionId=null, caseId=null, seq=1;
async function rpc(method, params={}){
  const headers={'Content-Type':'application/json','Accept':'application/json, text/event-stream','MCP-Protocol-Version':'2025-11-25'};
  if(sessionId) headers['Mcp-Session-Id']=sessionId;
  const res=await fetch('/mcp',{method:'POST',headers,body:JSON.stringify({jsonrpc:'2.0',id:seq++,method,params})});
  if(method==='initialize') sessionId=res.headers.get('Mcp-Session-Id');
  const body=await res.json(); if(body.error) throw new Error(body.error.message); return body.result;
}
async function init(){if(sessionId)return; await rpc('initialize',{protocolVersion:'2025-11-25',capabilities:{},clientInfo:{name:'nebius-nvidia-demo',version:'1.0'}});}
function show(c){
  caseId=c.case_id; const r=document.getElementById('result'); r.classList.remove('hidden');
  const provider=c.reasoning_provider?'<div class="k">Reasoning</div><div class="v">'+c.reasoning_provider+(c.reasoning_model?' · '+c.reasoning_model:'')+'</div>':'';
  r.innerHTML='<span class="status">'+c.status+'</span>'+provider+'<div class="k">Current blocker</div><div class="v">'+c.blocker+'</div><div class="k">Who controls it</div><div class="v">'+c.controller+'</div><div class="k">Smallest safe next action</div><div class="v">'+c.next_action+'</div><div class="k">Verification rule</div><div class="v">'+c.verify+'</div>';
  document.getElementById('follow').classList.remove('hidden');
}document.getElementById('run').onclick=async()=>{try{await init(); const goal=document.getElementById('goal').value; const facts=[document.getElementById('facts').value]; const res=await rpc('tools/call',{name:'break_bureaucracy',arguments:{goal,known_facts:facts,constraints:['Do not contact the user by phone','Use the smallest safe next action']}});show(res.structuredContent);}catch(e){alert(e.message)}};
async function record(v){try{const res=await rpc('tools/call',{name:'record_outcome',arguments:{case_id:caseId,outcome:document.getElementById('outcome').value,verified:v}});show(res.structuredContent);}catch(e){alert(e.message)}}
document.getElementById('notVerified').onclick=()=>record(false);
document.getElementById('verified').onclick=()=>record(true);