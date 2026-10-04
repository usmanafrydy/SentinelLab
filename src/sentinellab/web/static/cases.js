"use strict";
// Shared API/DOM helpers come from app.js and alerts.js.
const casePageSize = 10, caseDrafts = new Map();
let caseSource = null, creatingAlert = null, currentCase = null, selectedCaseId = null;
let caseBusy = false, caseLoading = false, needsCaseReview = false, exportBusy = false;
let caseReadRequest = 0, caseListRequest = 0, caseHistoryRequest = 0;
let caseOffset = 0, caseNext = null, actionOffset = 0, actionNext = null;
const caseWords = {open: "Open", in_progress: "In progress", closed: "Closed", undecided: "Undecided",
  benign: "Benign", suspicious: "Suspicious", confirmed_compromise: "Confirmed compromise",
  created: "Case created", note: "Note added", state_changed: "Decision updated"};
const caseLabel = value => caseWords[value] || value;

function clearCaseSource() { caseSource = null; $("investigate-alert").disabled = true; }
function prepareCaseSource(alert) {
  caseSource = {id: alert.alert_id, title: `${alert.rule_id}: ${alert.title}`};
  $("investigate-alert").disabled = caseBusy;
}
function caseControls() {
  for (const format of ["json", "markdown"]) $("case-export-" + format).disabled = exportBusy || caseBusy || caseLoading || !currentCase || needsCaseReview;
  $("case-note-fields").disabled = caseBusy || caseLoading || !currentCase;
  $("case-state-fields").disabled = caseBusy || caseLoading || !currentCase || needsCaseReview;
  $("reload-case").disabled = caseBusy || caseLoading || !selectedCaseId;
  $("case-open-alert").disabled = caseBusy || !currentCase;
  $("case-author").disabled = caseBusy || caseLoading;
  $("investigate-alert").disabled = caseBusy || !caseSource;
  for (const control of $("case-create-form").elements) control.disabled = caseBusy;
  $("cancel-case-create").disabled = caseBusy;
}
function rememberCaseDraft() {
  if (selectedCaseId) caseDrafts.set(selectedCaseId, {note: $("case-note").value,
    reason: $("case-reason").value, author: $("case-author").value});
}
function restoreCaseDraft(id) {
  const draft = caseDrafts.get(id) || {note: "", reason: "", author: $("case-create-author").value};
  $("case-note").value = draft.note; $("case-reason").value = draft.reason; $("case-author").value = draft.author;
}
function caseFacts(record) {
  $("case-facts").replaceChildren();
  for (const [key, value] of Object.entries({"Status": caseLabel(record.status), "Conclusion": caseLabel(record.disposition),
    "Revision": record.revision, "Created UTC": record.created_at, "Updated UTC": record.updated_at, "Linked alert": record.alert_id})) {
    const dt = document.createElement("dt"), dd = document.createElement("dd");
    dt.textContent = key; dd.textContent = value; $("case-facts").append(dt, dd);
  }
}
async function loadCases(offset = 0) {
  const request = ++caseListRequest;
  $("cases-previous").disabled = true; $("cases-next").disabled = true;
  $("case-rows").replaceChildren(); status("cases-status", "Loading cases…");
  const query = new URLSearchParams({limit: String(casePageSize), offset: String(offset)});
  if ($("case-filter").value) query.set("status", $("case-filter").value);
  try {
    const result = await api(`/api/cases?${query}`);
    if (request !== caseListRequest) return;
    caseOffset = offset; caseNext = result.next_offset;
    for (const record of result.items) {
      const row = document.createElement("tr");
      for (const value of [`#${record.id}`, record.title, caseLabel(record.status), caseLabel(record.disposition)]) textCell(row, value);
      actionCell(row, `Open case ${record.id}`, () => openCase(record.id)); $("case-rows").append(row);
    }
    $("cases-page").textContent = pageLabel(result);
    status("cases-status", result.total ? "Cases loaded. Choose a case to continue." : $("case-filter").value ? "No cases match this status. Try All cases." : "No cases yet. Open a saved alert and choose Investigate this alert.");
    $("cases-previous").disabled = offset === 0; $("cases-next").disabled = caseNext === null;
  } catch (error) {
    if (request !== caseListRequest) return;
    status("cases-status", error.message, true); $("cases-page").textContent = "Cases unavailable";
  }
}
async function loadCaseActions(offset = 0) {
  const id = selectedCaseId, request = ++caseHistoryRequest;
  if (!id) return;
  $("case-history-previous").disabled = true; $("case-history-next").disabled = true;
  $("case-actions").replaceChildren(); status("case-history-status", "Loading action history…");
  try {
    const result = await api(`/api/cases/${id}/history?limit=${casePageSize}&offset=${offset}`);
    if (id !== selectedCaseId || request !== caseHistoryRequest) return;
    actionOffset = offset; actionNext = result.next_offset;
    for (const action of result.items) {
      const item = document.createElement("li"), title = document.createElement("h4"), meta = document.createElement("p"), text = document.createElement("p"), state = document.createElement("p");
      title.textContent = `Revision ${action.revision} · ${caseLabel(action.kind)}`;
      meta.className = "action-meta"; meta.textContent = `${action.occurred_at} · Author label: ${action.author}`;
      text.className = "action-text"; text.textContent = action.text;
      state.className = "action-meta";
      const describe = value => `${caseLabel(value.status)} / ${caseLabel(value.disposition)}`;
      state.textContent = action.before ? `${describe(action.before)} → ${describe(action.after)}` : describe(action.after);
      item.append(title, meta, text, state); $("case-actions").append(item);
    }
    $("case-history-page").textContent = pageLabel(result);
    status("case-history-status", "Saved actions, oldest first. Use Next actions for later changes.");
    $("case-history-previous").disabled = offset === 0; $("case-history-next").disabled = actionNext === null;
  } catch (error) {
    if (id !== selectedCaseId || request !== caseHistoryRequest) return;
    status("case-history-status", error.message, true); $("case-history-page").textContent = "History unavailable";
  }
}
async function openCase(id, message = "Review the linked evidence before choosing a conclusion.") {
  if (caseBusy) return;
  rememberCaseDraft(); selectedCaseId = String(id); restoreCaseDraft(selectedCaseId);
  currentCase = null; caseLoading = true; needsCaseReview = false;
  const request = ++caseReadRequest; ++caseHistoryRequest;
  $("case-detail").hidden = false; $("case-title").textContent = `Case #${id}`;
  revealWorkspace("case-detail");
  $("case-facts").replaceChildren(); $("case-actions").replaceChildren();
  $("case-history-previous").disabled = true; $("case-history-next").disabled = true;
  $("case-history-page").textContent = ""; status("case-history-status", "");
  $("case-title").focus(); $("case-detail").scrollIntoView({block: "start"});
  status("case-detail-status", "Loading the latest case…"); caseControls();
  status("case-export-status", "");
  try {
    const record = await api(`/api/cases/${id}`);
    if (request !== caseReadRequest) return;
    currentCase = record; $("case-title").textContent = `Case #${record.id} · ${record.title}`;
    caseFacts(record); $("case-state").value = record.status; $("case-disposition").value = record.disposition;
    status("case-detail-status", message);
    await loadCaseActions();
  } catch (error) { if (request === caseReadRequest) status("case-detail-status", error.message, true); }
  finally { if (request === caseReadRequest) { caseLoading = false; caseControls(); } }
}
async function casePost(path, data) {
  return api(path, {method: "POST", headers: {"Content-Type": "application/json", "X-SentinelLab-Token": token}, body: JSON.stringify(data)});
}
$("investigate-alert").addEventListener("click", () => {
  if (!caseSource || caseBusy) return;
  creatingAlert = {...caseSource}; $("case-create-panel").hidden = false;
  revealWorkspace("case-create-panel");
  $("case-create-source").textContent = `Linked alert: ${creatingAlert.id}`;
  $("case-create-title").value = creatingAlert.title.slice(0, 120);
  status("case-create-status", "Add a short title and author label. Existing cases open without changes.");
  $("case-create-heading").focus(); $("case-create-panel").scrollIntoView({block: "start"});
});
$("cancel-case-create").addEventListener("click", () => { if (!caseBusy) $("case-create-panel").hidden = true; });
$("case-create-form").addEventListener("submit", async event => {
  event.preventDefault(); if (caseBusy || !creatingAlert) return;
  const data = {alert_id: creatingAlert.id, title: $("case-create-title").value, author: $("case-create-author").value};
  caseBusy = true; caseControls(); status("case-create-status", "Saving or opening this alert's case…");
  let result;
  try {
    result = await casePost("/api/cases", data);
    status("case-create-status", result.created ? "Case created. It starts Open / Undecided." : "Existing case found. Its title, notes, and status are unchanged.");
  } catch (error) { status("case-create-status", `${error.message} Refresh cases before retrying if the connection was lost.`, true); }
  finally { caseBusy = false; caseControls(); }
  if (result) { await openCase(result.case.id, result.created ? "Case created. Add observations below." : "Existing case opened. Previous work is preserved."); await loadCases(); }
});
async function saveCaseAction(kind) {
  if (caseBusy || caseLoading || !currentCase || (kind === "state" && needsCaseReview)) return;
  if (!$("case-author").reportValidity()) return;
  const id = currentCase.id, author = $("case-author").value;
  const data = kind === "notes" ? {text: $("case-note").value, author} : {
    status: $("case-state").value, disposition: $("case-disposition").value,
    reason: $("case-reason").value, author, expected_revision: currentCase.revision};
  caseBusy = true; caseControls(); status("case-detail-status", "Saving this action…");
  let saved = false;
  try {
    await casePost(`/api/cases/${id}/${kind}`, data); saved = true;
    $(kind === "notes" ? "case-note" : "case-reason").value = "";
    rememberCaseDraft();
  } catch (error) {
    if (error.code === "stale_revision") {
      needsCaseReview = true;
      status("case-detail-status", "This case changed elsewhere. Your reason is kept. Select Refresh selected case, review the latest history, then choose your decision again. Nothing was overwritten.", true);
    } else status("case-detail-status", `${error.message} Your text is kept. If the connection was lost, refresh and check history before trying again; the action may already be saved.`, true);
  } finally { caseBusy = false; caseControls(); }
  if (saved) { await openCase(id, "Action saved. Original alert and login records are unchanged."); await loadCases(); }
}
$("case-note-form").addEventListener("submit", event => { event.preventDefault(); saveCaseAction("notes"); });
$("case-state-form").addEventListener("submit", event => { event.preventDefault(); saveCaseAction("state"); });
$("reload-case").addEventListener("click", () => { if (selectedCaseId) openCase(selectedCaseId, "Latest case loaded. Draft text kept; status and conclusion show the saved values. Review history before saving again."); });
$("case-open-alert").addEventListener("click", () => { if (currentCase && !caseBusy) openAlert(currentCase.alert_id); });
$("case-filter-form").addEventListener("submit", event => { event.preventDefault(); loadCases(); });
$("cases-previous").addEventListener("click", () => loadCases(Math.max(0, caseOffset - casePageSize)));
$("cases-next").addEventListener("click", () => { if (caseNext !== null) loadCases(caseNext); });
$("case-history-previous").addEventListener("click", () => loadCaseActions(Math.max(0, actionOffset - casePageSize)));
$("case-history-next").addEventListener("click", () => { if (actionNext !== null) loadCaseActions(actionNext); });
async function downloadCase(format) {
  if (exportBusy || caseBusy || caseLoading || !currentCase || needsCaseReview) return;
  const {id, revision} = currentCase;
  exportBusy = true; caseControls();
  status("case-export-status", "Preparing saved evidence and complete history…");
  try {
    const response = await fetch(`/api/cases/${id}/report?format=${format}&revision=${revision}`, {cache: "no-store"});
    if (response.status === 401) $("session-expired").hidden = false;
    if (!response.ok) {
      const result = await response.json();
      throw new Error(result.error || "Report could not be exported.");
    }
    const blob = await response.blob(), url = URL.createObjectURL(blob), link = document.createElement("a");
    link.href = url; link.download = `sentinellab-case-${id}-rev-${revision}.${format === "json" ? "json" : "md"}`;
    document.body.append(link); link.click(); link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 10000);
    if (selectedCaseId === id) status("case-export-status", `Download requested for case ${id}, revision ${revision}. Check your browser downloads. Unsaved text was not included.`);
  } catch (error) {
    if (selectedCaseId === id) status("case-export-status", error.message, true);
  } finally { exportBusy = false; caseControls(); }
}
for (const format of ["json", "markdown"]) $("case-export-" + format).addEventListener("click", () => downloadCase(format));
loadCases();
