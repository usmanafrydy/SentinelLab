"use strict";
// Reuse app.js API, text status, original evidence, and shared write controls.
const historySize = 10, evidenceSize = 25;
const historyPages = {alerts: {offset: 0, next: null, request: 0}, runs: {offset: 0, next: null, request: 0}};
let selectedRun = null, selectedAlert = null, alertRequest = 0, evidenceOffset = 0, evidenceNext = null;

function textCell(row, value) {
  const cell = document.createElement("td"); cell.textContent = String(value); row.append(cell); return cell;
}
function actionCell(row, label, action) {
  const cell = document.createElement("td"), button = document.createElement("button");
  button.type = "button"; button.className = "secondary"; button.textContent = label;
  button.addEventListener("click", action); cell.append(button); row.append(cell);
}
function pageLabel(result) {
  return result.items.length ? `Showing ${result.offset + 1}–${result.offset + result.items.length} of ${result.total}` : `0 shown · ${result.total} total`;
}
async function refreshAlertCounts() {
  const result = await api("/api/alerts/summary");
  $("alert-count").textContent = result.saved_alerts;
  $("run-count").textContent = result.detection_runs;
}
function closeAlert() {
  alertRequest += 1; selectedAlert = null;
  $("alert-detail").hidden = true;
  $("alert-evidence-rows").replaceChildren(); hideEvidence();
}
async function loadHistory(kind, offset = 0) {
  const page = historyPages[kind], request = ++page.request;
  $(`${kind}-previous`).disabled = true; $(`${kind}-next`).disabled = true;
  status(`${kind}-status`, "Loading saved history…");
  const query = new URLSearchParams({limit: String(historySize), offset: String(offset)});
  if (kind === "alerts" && selectedRun !== null) query.set("run_id", String(selectedRun));
  const body = $(kind === "alerts" ? "alert-rows" : "run-rows");
  body.replaceChildren();
  try {
    const result = await api(`/api/${kind}?${query}`);
    if (request !== page.request) return;
    page.offset = offset; page.next = result.next_offset;
    for (const item of result.items) {
      const row = document.createElement("tr");
      if (kind === "alerts") {
        textCell(row, item.rule_id); textCell(row, item.triggered_at); textCell(row, item.first_run_id);
        actionCell(row, `Open ${item.rule_id} alert`, () => openAlert(item.alert_id));
      } else {
        textCell(row, `#${item.id} · ${item.completed_at}`);
        textCell(row, item.configurations.map(rule => `${rule.rule_id} v${rule.rule_version}: ${rule.threshold} / ${rule.window_seconds}s`).join("; "));
        for (const key of ["events_scanned", "matched_count", "new_count", "existing_count"]) textCell(row, item[key]);
        actionCell(row, `Alerts from run ${item.id}`, () => selectRun(item.id));
      }
      body.append(row);
    }
    $(`${kind}-page`).textContent = pageLabel(result);
    status(`${kind}-status`, result.total ? "Saved history loaded." : kind === "runs" ? "No saved runs yet. Use Run detection and save." : selectedRun !== null ? "This run matched no alerts." : "No saved alerts yet. A successful check can also find zero alerts.");
    $(`${kind}-previous`).disabled = offset === 0;
    $(`${kind}-next`).disabled = page.next === null;
  } catch (error) {
    if (request !== page.request) return;
    page.offset = 0; page.next = null;
    $(`${kind}-page`).textContent = "History unavailable";
    status(`${kind}-status`, error.message, true);
  }
}
function selectRun(id) {
  selectedRun = id; closeAlert();
  $("alert-scope").textContent = id === null ? "All saved alerts, including historical findings. These are not confirmed incidents." : `Findings matched by run #${id}. Some may have been saved in an earlier run.`;
  loadHistory("alerts"); $("alerts-title").focus(); $("alerts-title").scrollIntoView({block: "start"});
}
async function openAlert(id, offset = 0) {
  const request = ++alertRequest;
  selectedAlert = id; hideEvidence();
  $("alert-detail").hidden = false; $("alert-detail-title").textContent = "Alert evidence";
  $("alert-detail-title").focus();
  if (offset === 0) $("alert-detail").scrollIntoView({block: "start"});
  $("evidence-previous").disabled = true; $("evidence-next").disabled = true;
  $("alert-facts").replaceChildren(); $("alert-evidence-rows").replaceChildren();
  $("alert-reason").textContent = ""; $("alert-evidence-page").textContent = "";
  status("alert-detail-status", "Loading saved evidence…");
  try {
    const result = await api(`/api/alerts/${encodeURIComponent(id)}?limit=${evidenceSize}&offset=${offset}`);
    if (request !== alertRequest) return;
    const alert = result.alert;
    $("alert-detail-title").textContent = `${alert.rule_id} · ${alert.title}`;
    $("alert-reason").textContent = alert.reason;
    const facts = {"Alert ID": alert.alert_id, "Rule version": alert.rule_version,
      "Account": alert.group.username ?? "Multiple accounts", "Source IP": alert.group.source_ip,
      "Threshold": `${alert.parameters.threshold} in ${alert.parameters.window_seconds} seconds`,
      "Failures": alert.failure_count, "First event UTC": alert.first_event_at,
      "Triggered at UTC": alert.triggered_at, "First saved run": result.first_run_id};
    if (alert.distinct_account_count !== undefined) facts["Distinct accounts"] = alert.distinct_account_count;
    for (const [label, value] of Object.entries(facts)) {
      const term = document.createElement("dt"), description = document.createElement("dd");
      term.textContent = label; description.textContent = String(value); $("alert-facts").append(term, description);
    }
    for (const reference of result.evidence.items) {
      const row = document.createElement("tr");
      textCell(row, `${reference.source} / ${reference.event_id}${reference.username === undefined ? "" : " · " + reference.username}`);
      textCell(row, reference.timestamp_utc); textCell(row, reference.role ?? "failure");
      actionCell(row, `Original #${reference.internal_id}`, () => showEvidence(reference.internal_id));
      $("alert-evidence-rows").append(row);
    }
    evidenceOffset = offset; evidenceNext = result.evidence.next_offset;
    $("alert-evidence-page").textContent = pageLabel(result.evidence);
    $("evidence-previous").disabled = offset === 0; $("evidence-next").disabled = evidenceNext === null;
    status("alert-detail-status", "Saved snapshot. Investigate before concluding compromise.");
  } catch (error) {
    if (request === alertRequest) status("alert-detail-status", error.message, true);
  }
}
async function refreshHistory() {
  await Promise.all([refreshAlertCounts(), loadHistory("alerts"), loadHistory("runs")]);
}
for (const kind of ["alerts", "runs"]) {
  $(`${kind}-previous`).addEventListener("click", () => loadHistory(kind, Math.max(0, historyPages[kind].offset - historySize)));
  $(`${kind}-next`).addEventListener("click", () => { if (historyPages[kind].next !== null) loadHistory(kind, historyPages[kind].next); });
}
$("all-alerts").addEventListener("click", () => selectRun(null));
$("close-alert").addEventListener("click", closeAlert);
$("evidence-previous").addEventListener("click", () => { if (selectedAlert) openAlert(selectedAlert, Math.max(0, evidenceOffset - evidenceSize)); });
$("evidence-next").addEventListener("click", () => { if (selectedAlert && evidenceNext !== null) openAlert(selectedAlert, evidenceNext); });
$("refresh-history").addEventListener("click", () => refreshHistory().catch(error => status("detect-status", error.message, true)));
$("detect-form").addEventListener("submit", async event => {
  event.preventDefault();
  if (detecting || importing || loading) return;
  const rule = $("detect-rule").value;
  detecting = true; toggleSearch(true);
  status("detect-status", "Checking stored events and saving one complete run…");
  let saved = false;
  try {
    const result = await api("/api/detect", {method: "POST", headers: {"Content-Type": "application/x-www-form-urlencoded", "X-SentinelLab-Token": token}, body: new URLSearchParams({rule}).toString()});
    saved = true;
    status("detect-status", `Saved run #${result.run_id}: ${result.events_scanned} events checked · ${result.new_alerts} new alerts · ${result.existing_alerts} already saved · ${result.total_saved_alerts} total saved alerts.`);
    selectedRun = null; closeAlert();
    $("alert-scope").textContent = "All saved alerts, including historical findings. These are not confirmed incidents.";
    await refreshHistory();
  } catch (error) {
    status("detect-status", saved ? `Run was saved, but history could not refresh. Use Refresh history. ${error.message}` : `Check did not return a saved result. ${error.message} Refresh history before retrying if the connection was lost.`, true);
  } finally { detecting = false; toggleSearch(loading || importing); }
});
refreshHistory().catch(error => status("detect-status", error.message, true));
