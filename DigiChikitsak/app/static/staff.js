const $ = s => document.querySelector(s);
const escapeHtml = s => String(s ?? "").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
let searchTimer;
$("#themeBtn").addEventListener("click",()=>{document.body.classList.toggle("dark");localStorage.setItem("dc-theme",document.body.classList.contains("dark")?"dark":"light");});
if(localStorage.getItem("dc-theme")==="dark")document.body.classList.add("dark");

async function loadStats(){
  const d=await fetch("/api/stats").then(r=>r.json());
  $("#statsGrid").innerHTML=[
    ["REGISTERED PATIENTS",d.patients,"All-time profiles"],
    ["ASSESSMENTS",d.assessments,"Saved check-ins"],
    ["CHECK-INS TODAY",d.today,"Local server date"],
    ["FLAGGED CHECK-INS",d.flagged_assessments,"Safety rules triggered"]
  ].map(([a,b,c])=>`<div class="stat-card"><small>${a}</small><strong>${b}</strong><span>${c}</span></div>`).join("");
}
async function loadPatients(q=""){
  const rows=await fetch("/api/patients?q="+encodeURIComponent(q)).then(r=>r.json());
  $("#patientRows").innerHTML=rows.length?rows.map(p=>`<tr><td><div class="patient-name"><span class="patient-avatar">${escapeHtml(p.name.split(/\s+/).map(x=>x[0]).slice(0,2).join("").toUpperCase())}</span>${escapeHtml(p.name)}</div></td><td><span class="id-code">${escapeHtml(p.patient_id)}</span></td><td>${p.age} / ${escapeHtml(p.gender)}</td><td>${p.assessment_count}</td><td>${p.last_visit?escapeHtml(p.last_visit):"—"}</td><td><button class="view-btn" data-id="${escapeHtml(p.patient_id)}">View record ↗</button></td></tr>`).join(""):`<tr><td colspan="6" class="table-empty">No patient records yet. Create a check-in from the patient kiosk.</td></tr>`;
  $("#directoryMessage").textContent=`Showing ${rows.length} patient record(s). Data is stored in local SQLite.`;
}
async function loadModel(){
  const m=await fetch("/api/model-card").then(r=>r.json());
  $("#modelCard").innerHTML=`<div class="model-fact"><small>TRAINING RECORDS</small><strong>${m.rows??"—"}</strong><span class="small-note">${escapeHtml(m.dataset??"Model not trained")}</span></div><div class="model-fact"><small>LABEL CLASSES</small><strong>${m.classes??"—"}</strong><span class="small-note">${escapeHtml(m.model??"")}</span></div><div class="model-limitations"><b>Important limitations</b><ul>${(m.limitations||["No model card found."]).map(x=>`<li>${escapeHtml(x)}</li>`).join("")}</ul></div>`;
}
$("#searchInput").addEventListener("input",e=>{clearTimeout(searchTimer);searchTimer=setTimeout(()=>loadPatients(e.target.value),220);});
$("#patientRows").addEventListener("click",async e=>{
  const btn=e.target.closest("[data-id]");if(!btn)return;
  const p=await fetch("/api/patients/"+encodeURIComponent(btn.dataset.id)).then(r=>r.json());
  $("#modalContent").innerHTML=`<div class="eyebrow">PATIENT RECORD</div><h2>${escapeHtml(p.name)}</h2><p>${escapeHtml(p.patient_id)} · ${p.age} years · ${escapeHtml(p.gender)} · Registered ${escapeHtml(p.created_at)}</p><div class="modal-visit"><h4>Profile details</h4><p>Mobile: ${escapeHtml(p.mobile||"Not provided")}<br>Assessment count: ${p.assessments.length}</p></div>${p.assessments.length?p.assessments.map(a=>`<div class="modal-visit"><h4>Check-in #${a.id} · ${escapeHtml(a.created_at)}</h4><p>Symptoms: ${escapeHtml(a.symptoms.join(", ")||"None selected")}<br>Vitals: Temp ${a.vitals.temperature_c}°C · SpO₂ ${a.vitals.spo2}% · BP ${a.vitals.systolic_bp}/${a.vitals.diastolic_bp}<br>BMI: ${a.vitals.bmi}<br>Model matches: ${escapeHtml((a.result.matches||[]).map(m=>m.condition+" ("+m.score+"%)").join(", ")||"Unavailable")}<br>Recommendation: ${escapeHtml(a.result.recommendation)}</p></div>`).join(""):`<div class="modal-visit"><p>No check-ins recorded yet.</p></div>`}`;
  $("#patientModal").classList.remove("hidden");
});
$("#closeModal").addEventListener("click",()=>$("#patientModal").classList.add("hidden"));
$("#patientModal").addEventListener("click",e=>{if(e.target.id==="patientModal")$("#patientModal").classList.add("hidden");});
Promise.all([loadStats(),loadPatients(),loadModel()]).catch(err=>{$("#patientRows").innerHTML=`<tr><td colspan="6" class="table-empty">Could not load data. Is the API running? ${escapeHtml(err.message)}</td></tr>`;});
