const $ = (s, root=document) => root.querySelector(s);
const $$ = (s, root=document) => [...root.querySelectorAll(s)];
let patient = null;
let latestAssessment = null;

function setStep(step) {
  $$(".step").forEach(el => {
    const n = Number(el.dataset.step);
    el.classList.toggle("active", n === step);
    el.classList.toggle("complete", n < step);
  });
  $("#stepLabel").textContent = `STEP 0${step} / 03`;
}
function showPanel(id) {
  ["registerPanel","assessmentPanel","resultPanel"].forEach(x => $("#"+x).classList.toggle("hidden", x !== id));
  setStep(id === "registerPanel" ? 1 : id === "assessmentPanel" ? 2 : 3);
  window.scrollTo({top: $("#stepLabel").getBoundingClientRect().top + window.scrollY - 100, behavior:"smooth"});
}
function escapeHtml(s) { return String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }
function renderPatient(p) {
  $("#patientSummary").innerHTML = `<div class="profile-data"><div class="profile-id">${escapeHtml(p.patient_id)}</div><b>${escapeHtml(p.name)}</b><small>${p.age} years · ${escapeHtml(p.gender)}</small><small>Registered ${new Date(p.created_at.replace(" ","T")+"Z").toLocaleDateString()}</small></div>`;
  $("#patientGreeting").textContent = `Hi ${p.name.split(" ")[0]}, let's capture a structured snapshot.`;
}
$("#patientForm").addEventListener("submit", async e => {
  e.preventDefault();
  const form = new FormData(e.currentTarget);
  const payload = Object.fromEntries(form.entries());
  payload.age = Number(payload.age);
  if (!payload.mobile) payload.mobile = null;
  const btn = e.submitter; btn.disabled = true; btn.textContent = "Creating profile…";
  try {
    const response = await fetch("/api/patients", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Could not create profile");
    patient = data; renderPatient(patient); showPanel("assessmentPanel");
  } catch(err) { alert(err.message); }
  finally { btn.disabled = false; btn.innerHTML = 'Create patient profile <span>→</span>'; }
});
$("#backToPatient").addEventListener("click", () => showPanel("registerPanel"));
$("#assessmentForm").addEventListener("submit", async e => {
  e.preventDefault();
  if (!patient) return alert("Register a patient first.");
  const form = new FormData(e.currentTarget);
  const symptoms = form.getAll("symptom");
  const checked = new Set(symptoms);
  const payload = {
    patient_id: patient.patient_id, age: patient.age, gender: patient.gender, symptoms,
    duration_days:Number(form.get("duration_days")), temperature_c:Number(form.get("temperature_c")),
    spo2:Number(form.get("spo2")), systolic_bp:Number(form.get("systolic_bp")), diastolic_bp:Number(form.get("diastolic_bp")),
    weight_kg:Number(form.get("weight_kg")), height_cm:Number(form.get("height_cm")),
    blood_pressure_label:form.get("blood_pressure_label"), cholesterol_label:form.get("cholesterol_label"),
    fever:checked.has("Fever"), cough:checked.has("Cough"), fatigue:checked.has("Fatigue"),
    difficulty_breathing:checked.has("Difficulty breathing")
  };
  const btn = e.submitter; btn.disabled = true; btn.textContent = "Analyzing snapshot…";
  try {
    const response = await fetch("/api/assessments", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Could not save assessment");
    latestAssessment = data; renderResult(data); showPanel("resultPanel");
  } catch(err) { alert(err.message); }
  finally { btn.disabled = false; btn.innerHTML = 'Generate health snapshot <span>→</span>'; }
});
function renderResult(data) {
  const r = data.result, v = data.vitals;
  $("#resultMetrics").innerHTML = [
    ["TEMPERATURE", `${v.temperature_c}°C`, "Recorded reading"],
    ["OXYGEN", `${v.spo2}%`, "SpO₂ reading"],
    ["HEALTH SNAPSHOT", `${r.health_score}/100`, "Non-clinical score"]
  ].map(([a,b,c]) => `<div class="result-metric"><small>${a}</small><strong>${b}</strong><span>${c}</span></div>`).join("");
  $("#urgentFlags").innerHTML = (r.safety_flags || []).map(f => `<div class="safety-flag ${f.level==="warning"?"warning":""}"><b>${f.level==="critical"?"⚠ Urgent safety flag":"⚠ Caution"}</b>${escapeHtml(f.message)}</div>`).join("");
  const matches = r.matches || [];
  $("#predictions").innerHTML = matches.length ? matches.map(m => `<div class="prediction-row"><b>${escapeHtml(m.condition)}</b><div class="prediction-bar"><i style="width:${Math.max(2,Math.min(100,m.score))}%"></i></div><strong>${m.score}%</strong></div>`).join("") : `<p class="small-note">Model unavailable. Run <code>python train_models.py</code>.</p>`;
  $("#modelNote").textContent = r.model_note || "Experimental pattern matching only.";
  $("#recommendation").textContent = r.recommendation;
  $("#forecast").textContent = r.forecast;
}
$("#printReport").addEventListener("click", () => window.print());
$("#newCheckin").addEventListener("click", () => {
  patient = null; latestAssessment = null; $("#patientForm").reset(); $("#assessmentForm").reset();
  $("#patientSummary").innerHTML = `<div class="empty-profile"><div class="profile-placeholder">✧</div><b>Your profile will appear here</b><p>Start by registering a demo patient.</p></div>`;
  showPanel("registerPanel");
});
$("#themeBtn").addEventListener("click", () => { document.body.classList.toggle("dark"); localStorage.setItem("dc-theme", document.body.classList.contains("dark")?"dark":"light"); });
if (localStorage.getItem("dc-theme")==="dark") document.body.classList.add("dark");
fetch("/api/health").then(r=>r.json()).then(d=>console.log("DigiChikitsak API:",d.status)).catch(()=>{});
