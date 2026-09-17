const $ = (id) => document.getElementById(id);
let session = null, config = {ready:false, criteria:[]}, busy = false;
const escapeHtml = (text) => String(text).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const notes = {
  definition:'Temperature điều chỉnh phân bố xác suất khi lấy mẫu token tiếp theo. “Độ sáng tạo” là cách nói trực quan, chưa mô tả đủ cơ chế.',
  low:'Temperature thấp ưu tiên token có xác suất cao, thường làm kết quả ổn định hơn. Điều này không bảo đảm nội dung đúng hoặc đầu ra luôn giống hệt.',
  high:'Temperature cao làm phân bố bớt tập trung: token ít có khả năng hơn có thêm cơ hội được chọn, tạo đầu ra đa dạng hơn.',
  usage:'Ví dụ áp dụng do nhóm biên soạn: trích xuất cần nhất quán có thể dùng thấp; nghĩ nhiều ý tưởng quảng cáo có thể dùng cao. Vẫn cần kiểm tra độ đúng.',
  sampling:'Top-k khoanh k token có xác suất cao nhất. Top-p khoanh tập token theo xác suất cộng dồn. Temperature điều chỉnh phân bố xác suất dùng để lấy mẫu.'
};
async function api(path, body) {
  const response = await fetch(path, body === undefined ? {} : {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Không thể kết nối. Hãy thử lại.');
  return data;
}
function showError(error) {$('error').textContent=error.message; $('error').hidden=false;}
function clearError() {$('error').hidden=true;}
function setBusy(value) {
  busy=value; $('send').disabled=value || !config.ready || !session || session.status!=='active';
  $('new-session').disabled=value; $('answer').disabled=value || (session && session.status!=='active');
  $('thinking').hidden=!value;
}
function render() {
  if (!session) return;
  $('messages').innerHTML=session.messages.map(m=>`<div class="message ${m.role}"><div class="message-label">${m.role==='user'?'Bạn · người dạy':'Mầm · học trò AI'}</div><div class="bubble">${escapeHtml(m.text)}</div></div>`).join('');
  $('messages').scrollTop=$('messages').scrollHeight;
  const count=session.checks.filter(c=>c.status==='met').length;
  $('progress-count').textContent=`${count}/5`;
  $('progress-fill').style.width=`${count*20}%`;
  $('probes').textContent=`${session.probes} / 3`;
  $('checklist').innerHTML=config.criteria.map((c,i)=>{const met=session.checks.some(x=>x.id===c.id&&x.status==='met');return `<div class="check ${met?'met':''}"><span class="check-icon">${met?'✓':i+1}</span><span>${escapeHtml(c.label)}</span></div>`;}).join('');
  const ended=session.status!=='active';
  $('composer').hidden=ended; $('result').hidden=!ended;
  if (ended) {
    $('result').innerHTML=`<div class="eyebrow">NHÌN LẠI PHIÊN DẠY</div><h2>${session.status==='completed'?'Bạn đã dạy được Mầm!':'Một vài điều để hiểu sâu hơn.'}</h2><p class="muted">${count}/5 điểm đã giải thích được · ${session.turn} lượt giải thích · ${session.probes} câu hỏi gợi mở</p>`+config.criteria.map(c=>{
      const check=session.checks.find(x=>x.id===c.id), met=check?.status==='met';
      const label=met?(session.initial.includes(c.id)?'Tự giải thích đúng ngay':'Bổ sung sau gợi mở'):(check?.status==='incorrect'?'Cần sửa cách hiểu':'Chưa giải thích đủ');
      return `<div class="result-row"><strong>${escapeHtml(c.label)}</strong><span class="status-label ${met?'':'review-label'}">${label}</span><p>${check?.evidence?'Lời của bạn: “'+escapeHtml(check.evidence)+'”':'Chưa có bằng chứng giải thích đủ tiêu chí này.'}</p>${!met?`<details><summary>Xem lại ${escapeHtml(c.source)}</summary><p>${escapeHtml(notes[c.id])}</p><small>Tóm lược/diễn giải của nhóm từ transcript-04-clean.md, không phải trích nguyên văn.</small></details>`:''}</div>`;
    }).join('')+'<button id="export" class="button secondary">↓ Tải log phiên học (JSON)</button>';
    $('export').onclick=()=>{const url=URL.createObjectURL(new Blob([JSON.stringify(session,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download=`teachback-${session.id}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
  }
  setBusy(false);
}
async function start() {
  clearError(); setBusy(true);
  try {session=await api('/api/sessions',{}); localStorage.setItem('teachback-session',session.id); $('answer').value=''; updateCounter(); render();}catch(e){showError(e);}finally{setBusy(false);}
}
function updateCounter() {$('counter').firstChild.textContent=`${$('answer').value.length.toLocaleString('vi-VN')} / 6.000 `;}
$('new-session').onclick=start;
$('answer').addEventListener('input',updateCounter);
$('answer').addEventListener('keydown',e=>{if(e.key==='Enter'&&(e.ctrlKey||e.metaKey)){e.preventDefault();$('composer').requestSubmit();}});
$('composer').onsubmit=async e=>{
  e.preventDefault(); if(busy||!session||!config.ready||!$('answer').value.trim())return;
  clearError();setBusy(true);
  try {session=await api(`/api/sessions/${session.id}/turns`,{text:$('answer').value,expected_turn:session.turn});$('answer').value='';updateCounter();render();if(session.status!=='active')$('result').scrollIntoView({behavior:'smooth',block:'start'});}
  catch(error){showError(error);}finally{setBusy(false);if(session.status==='active')$('answer').focus();}
};
async function loadDashboard() {
  try {const d=await api('/api/dashboard');$('dashboard-content').innerHTML=`<div class="stats"><div class="stat"><strong>${d.total}</strong><span>Phiên đã bắt đầu</span></div><div class="stat"><strong>${d.finished}</strong><span>Phiên đã kết thúc</span></div><div class="stat"><strong>${d.completed}</strong><span>Đã dạy được · đủ 5 điểm</span></div></div><div class="about-card"><h2>Chỗ nào cần được gợi mở nhiều hơn?</h2>${d.finished?'<p class="muted">“Sau gợi mở” gồm mọi điểm được bổ sung sau lượt đầu, kể cả điểm không được hỏi trực tiếp.</p>':'<p class="muted">Chưa có phiên kết thúc. Hoàn thành một phiên dạy lại để xem dữ liệu ở đây.</p>'}<div class="table-wrap"><table><thead><tr><th>Tiêu chí</th><th>Hiểu ngay</th><th>Sau gợi mở</th><th>Còn hổng</th></tr></thead><tbody>${d.criteria.map(c=>`<tr><td>${escapeHtml(c.label)}</td><td>${c.initial}</td><td>${c.prompted}</td><td>${c.gap}</td></tr>`).join('')}</tbody></table></div></div>`;}catch(e){showError(e);}
}
document.querySelectorAll('[data-page]').forEach(button=>button.onclick=()=>{document.querySelectorAll('.page').forEach(p=>p.hidden=p.id!==button.dataset.page);document.querySelectorAll('.nav').forEach(n=>n.classList.toggle('active',n===button));$('breadcrumb').textContent=button.querySelector('span').textContent;clearError();if(button.dataset.page==='dashboard')loadDashboard();});
$('refresh').onclick=loadDashboard;
(async()=>{try{config=await api('/api/config');$('setup').hidden=config.ready;const id=localStorage.getItem('teachback-session');if(id){try{session=await api(`/api/sessions/${encodeURIComponent(id)}`);}catch{localStorage.removeItem('teachback-session');}}if(session)render();else await start();}catch(e){showError(e);setBusy(false);}})();
