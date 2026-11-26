function openAddModal(){
  const modal=document.getElementById('taskModal');
  document.getElementById('modalTitle').textContent='Thêm công việc mới';
  document.getElementById('taskForm').action='/task';
  document.getElementById('taskForm').reset();
  document.getElementById('taskStatus').value='Chưa bắt đầu';
  document.getElementById('saveBtn').textContent='Lưu công việc ✿';
  modal.classList.add('show');
  setTimeout(()=>document.getElementById('taskTitle').focus(),100);
}
function openEditModal(task){
  document.getElementById('modalTitle').textContent='Chỉnh sửa công việc';
  document.getElementById('taskForm').action='/task/'+task.id+'/edit';
  document.getElementById('taskTitle').value=task.title||'';
  document.getElementById('taskDescription').value=task.description||'';
  document.getElementById('taskCategory').value=task.category||'Cá nhân';
  document.getElementById('taskPriority').value=task.priority||'Trung bình';
  document.getElementById('taskStatus').value=task.status||'Chưa bắt đầu';
  document.getElementById('taskDue').value=task.due_date||'';
  document.getElementById('taskImportant').checked=!!task.important;
  document.getElementById('saveBtn').textContent='Lưu thay đổi ✿';
  document.getElementById('taskModal').classList.add('show');
}
function closeModal(){document.getElementById('taskModal').classList.remove('show')}
function backdropClose(e){if(e.target.id==='taskModal')closeModal()}
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeModal()});

async function setStatus(id,status){
  const body=new URLSearchParams({status});
  const res=await fetch(`/task/${id}/status`,{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body});
  if(res.ok) location.reload(); else alert('Không thể cập nhật trạng thái.');
}
function cycleStatus(id,current){
  const next=current==='Chưa bắt đầu'?'Đang thực hiện':current==='Đang thực hiện'?'Hoàn thành':'Chưa bắt đầu';
  setStatus(id,next);
}
async function toggleImportant(id,button){
  const res=await fetch(`/task/${id}/important`,{method:'POST'});
  if(res.ok){const data=await res.json();button.textContent=data.important?'★':'☆';button.classList.toggle('starred',!!data.important)}
}
