const state={nodes:[],edges:[],route:[]};
const colors=['#3d9b66','#e7b73d','#3977bd','#858c89','#8ecf78'];
const labels=['School','Shop','Mall','HDB / Residential','Park / Open Area'];
const $=selector=>document.querySelector(selector);

async function api(url,options={}){const response=await fetch(url,{headers:{'Content-Type':'application/json'},...options});if(response.status===204)return null;const body=await response.json();if(!response.ok)throw new Error(body.error||'Request failed');return body}
function point(node){return{x:70+node.x*9,y:610-node.y*8}}
function render(){
  const svg=$('#map');svg.innerHTML='';const routeEdges=new Set(state.route.slice(1).map((n,i)=>[state.route[i],n].sort((a,b)=>a-b).join('-')));
  for(const edge of state.edges){const a=state.nodes.find(n=>n.id===edge.node_a),b=state.nodes.find(n=>n.id===edge.node_b);if(!a||!b)continue;const pa=point(a),pb=point(b),active=routeEdges.has([a.id,b.id].sort((x,y)=>x-y).join('-'));svg.insertAdjacentHTML('beforeend',`<line class="edge ${active?'active':''}" x1="${pa.x}" y1="${pa.y}" x2="${pb.x}" y2="${pb.y}"/><text class="edge-label" x="${(pa.x+pb.x)/2}" y="${(pa.y+pb.y)/2-5}">${edge.distance}</text>`)}
  for(const node of state.nodes){const p=point(node),active=state.route.includes(node.id);svg.insertAdjacentHTML('beforeend',`<circle class="node ${active?'active':''}" cx="${p.x}" cy="${p.y}" r="${node.type_id===2?18:14}" fill="${colors[node.type_id]}"/><text class="node-label" x="${p.x}" y="${p.y+34}">${node.id} · ${node.name.replaceAll('_',' ')}</text>`)}
}
function populate(){for(const id of ['start','end']){$('#'+id).innerHTML=state.nodes.map(n=>`<option value="${n.id}">${n.id} · ${n.name.replaceAll('_',' ')}</option>`).join('')}if(state.nodes.length>1)$('#end').value=state.nodes.at(-1).id}
async function refresh(){const data=await api('/api/map');state.nodes=data.nodes;state.edges=data.edges;populate();render();$('#editor').classList.toggle('hidden',!data.is_editor);$('#editor-toggle').textContent=data.is_editor?'Editor active':'Editor login'}
$('#find').addEventListener('click',async()=>{const result=$('#result');try{const data=await api(`/api/path?start=${$('#start').value}&end=${$('#end').value}`);state.route=data.path;result.className='result card';result.innerHTML=`<strong>Shortest route:</strong> ${data.path.join(' → ')} &nbsp; <strong>Total distance:</strong> ${data.total_distance}`;render()}catch(error){state.route=[];result.className='result card error';result.textContent=error.message;render()}});
$('#editor-toggle').addEventListener('click',()=>$('#login-dialog').showModal());$('#cancel-login').addEventListener('click',()=>$('#login-dialog').close());
$('#login-form').addEventListener('submit',async event=>{event.preventDefault();try{await api('/api/login',{method:'POST',body:JSON.stringify({password:new FormData(event.target).get('password')})});$('#login-error').textContent='';$('#login-dialog').close();event.target.reset();await refresh()}catch(error){$('#login-error').textContent=error.message}});
$('#logout').addEventListener('click',async()=>{await api('/api/logout',{method:'POST'});await refresh()});
async function saveForm(event,kind){event.preventDefault();const values=Object.fromEntries(new FormData(event.target));for(const key of Object.keys(values))if(key!=='name')values[key]=Number(values[key]);const exists=state[kind+'s'].some(item=>item.id===values.id);try{await api(`/api/${kind}s${exists?'/'+values.id:''}`,{method:exists?'PUT':'POST',body:JSON.stringify(values)});$('#editor-message').textContent=`${kind} saved successfully.`;await refresh()}catch(error){$('#editor-message').textContent=error.message}}
$('#node-form').addEventListener('submit',event=>saveForm(event,'node'));$('#edge-form').addEventListener('submit',event=>saveForm(event,'edge'));
document.querySelectorAll('[data-delete]').forEach(button=>button.addEventListener('click',async()=>{const kind=button.dataset.delete,form=$(`#${kind}-form`),id=new FormData(form).get('id');if(!id)return;try{await api(`/api/${kind}s/${id}`,{method:'DELETE'});form.reset();$('#editor-message').textContent=`${kind} deleted.`;await refresh()}catch(error){$('#editor-message').textContent=error.message}}));
$('#legend').innerHTML=labels.map((label,index)=>`<span class="legend-item"><i class="swatch" style="background:${colors[index]}"></i>${label}</span>`).join('');
refresh().catch(error=>{$('#result').textContent=error.message});
