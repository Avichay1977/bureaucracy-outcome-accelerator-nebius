let sessionId=null, caseId=null, caseState=null, seq=1;
const isLocalMcp = ["localhost","127.0.0.1"].includes(location.hostname);

async function rpc(method, params={}){
  const headers={'Content-Type':'application/json','Accept':'application/json, text/event-stream','MCP-Protocol-Version':'2025-11-25'};
  if(sessionId) headers['Mcp-Session-Id']=sessionId;
  const res=await fetch('/mcp',{method:'POST',headers,body:JSON.stringify({jsonrpc:'2.0',id:seq++,method,params})});
  if(method==='initialize') sessionId=res.headers.get('Mcp-Session-Id');
  const body=await res.json();
  if(body.error) throw new Error(body.error.message);
  return body.result;
}

async function init(){if(!isLocalMcp || sessionId)return; await rpc('initialize',{protocolVersion:'2025-11-25',capabilities:{},clientInfo:{name:'nebius-nvidia-demo',version:'1.0'}});}

async function publicAgent(payload){
  const res=await fetch('/api/agent',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
  const body=await res.json();
  if(!res.ok || body.error) throw new Error(body.error || ('HTTP '+res.status));
  return body;
}

function esc(value){
  return String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
}

function show(c){
  caseId=c.case_id;
  caseState=c;
  const r=document.getElementById('result');
  r.classList.remove('hidden');
  const provider=c.reasoning_provider?'<div class="k">Reasoning</div><div class="v">'+esc(c.reasoning_provider)+(c.reasoning_model?' · '+esc(c.reasoning_model):'')+'</div>':'';
  r.innerHTML='<span class="status">'+esc(c.status)+'</span>'+provider+
    '<div class="k">Current blocker</div><div class="v">'+esc(c.blocker)+'</div>'+
    '<div class="k">Who controls it</div><div class="v">'+esc(c.controller)+'</div>'+
    '<div class="k">Smallest safe next action</div><div class="v">'+esc(c.next_action)+'</div>'+
    '<div class="k">Verification rule</div><div class="v">'+esc(c.verify)+'</div>';
  document.getElementById('follow').classList.remove('hidden');
}

document.getElementById('run').onclick=async()=>{
  try{
    const goal=document.getElementById('goal').value;
    const facts=[document.getElementById('facts').value];
    const constraints=['Do not contact the user by phone','Use the smallest safe next action'];
    if(isLocalMcp){
      await init();
      const res=await rpc('tools/call',{name:'break_bureaucracy',arguments:{goal,known_facts:facts,constraints}});
      show(res.structuredContent);
    }else{
      show(await publicAgent({action:'break',goal,known_facts:facts,constraints}));
    }
  }catch(e){alert(e.message)}
};

async function record(v){
  try{
    const outcome=document.getElementById('outcome').value;
    if(isLocalMcp){
      const res=await rpc('tools/call',{name:'record_outcome',arguments:{case_id:caseId,outcome,verified:v}});
      show(res.structuredContent);
    }else{
      show(await publicAgent({action:'record',case:caseState,outcome,verified:v}));
    }
  }catch(e){alert(e.message)}
}
document.getElementById('notVerified').onclick=()=>record(false);
document.getElementById('verified').onclick=()=>record(true);
