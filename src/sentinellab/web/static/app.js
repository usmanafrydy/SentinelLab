"use strict";
const $ = (id) => document.getElementById(id);
const token = document.querySelector('meta[name="request-token"]').content;
let currentParams = new URLSearchParams({limit: "25"});
let currentOffset = 0, nextOffset = null, loading = false, importing = false, detecting = false, evidenceRequest = 0;

async function api(path, options = {}) {
  const response = await fetch(path, {cache: "no-store", ...options});
  const result = await response.json();
  if (response.status === 401) document.getElementById("session-expired").hidden = false;
  if (!response.ok) {
    const error = new Error(result.error || `Request failed (${response.status}).`);
    error.code = result.code; error.httpStatus = response.status; throw error;
  }
  return result;
}
function status(id, message, error = false) {
  $(id).textContent = message;
  $(id).classList.toggle("error", error);
}
async function refreshCounts() {
  const result = await api("/api/summary");
  $("event-count").textContent = result.total_events;
  $("import-count").textContent = result.total_imports;
}
function toggleSearch(disabled) {
  $("upload-button").disabled = disabled || importing || detecting;
  $("detect-button").disabled = disabled || importing || detecting;
  $("detect-rule").disabled = disabled || importing || detecting;
  for (const control of $("search-form").elements) control.disabled = disabled;
  $("previous").disabled = disabled || currentOffset === 0;
  $("next").disabled = disabled || nextOffset === null;
}
function hideEvidence() {
  evidenceRequest += 1;
  $("evidence-panel").hidden = true;
  $("evidence-content").textContent = "";
  leaveEvidenceWorkspace();
}
async function showEvidence(id) {
  const request = ++evidenceRequest;
  $("evidence-panel").hidden = false;
  revealWorkspace("evidence-panel");
  $("evidence-content").textContent = "";
  status("evidence-status", "Loading evidence…");
  $("evidence-title").focus();
  $("evidence-panel").scrollIntoView({block: "start"});
  try {
    const result = await api(`/api/events/${id}`);
    if (request !== evidenceRequest) return;
    status("evidence-status", `Event ${id} · ${result.event.event_id}`);
    $("evidence-content").textContent = JSON.stringify(result.event, null, 2);
  } catch (error) {
    if (request === evidenceRequest) status("evidence-status", error.message, true);
  }
}
async function search(offset = 0) {
  if (loading) return;
  loading = true;
  toggleSearch(true);
  hideEvidence();
  status("search-status", "Searching saved records…");
  const query = new URLSearchParams(currentParams);
  query.set("offset", String(offset));
  try {
    const result = await api(`/api/events?${query}`);
    currentOffset = offset;
    nextOffset = result.next_offset;
    $("event-rows").replaceChildren();
    for (const event of result.events) {
      const row = document.createElement("tr");
      for (const key of ["timestamp_utc", "username", "source_ip", "outcome"]) {
        const cell = document.createElement("td");
        const label = document.createElement("span");
        label.textContent = event[key];
        if (key === "outcome") label.className = `outcome ${event.outcome === "failure" ? "failure" : "success"}`;
        cell.append(label); row.append(cell);
      }
      const cell = document.createElement("td"), button = document.createElement("button");
      button.className = "secondary"; button.textContent = `View #${event.id}`;
      button.addEventListener("click", () => showEvidence(event.id));
      cell.append(button); row.append(cell); $("event-rows").append(row);
    }
    status("search-status", result.total_matches ? `${result.total_matches} matching login events · oldest first` : "No matching events. Try fewer filters or import a sample file.");
    $("page-description").textContent = result.returned ? `Showing ${offset + 1}–${offset + result.returned} of ${result.total_matches}` : "0 records shown";
  } catch (error) {
    $("event-rows").replaceChildren();
    currentOffset = 0; nextOffset = null;
    $("page-description").textContent = "Search unavailable";
    status("search-status", error.message, true);
  } finally { loading = false; toggleSearch(false); }
}
$("search-form").addEventListener("submit", (event) => {
  event.preventDefault();
  currentParams = new URLSearchParams();
  for (const [name, value] of new FormData(event.currentTarget)) if (value !== "") currentParams.set(name, value);
  search();
});
$("clear-filters").addEventListener("click", () => {
  $("search-form").reset(); currentParams = new URLSearchParams({limit: "25"}); search();
});
$("previous").addEventListener("click", () => search(Math.max(0, currentOffset - Number(currentParams.get("limit")))));
$("next").addEventListener("click", () => { if (nextOffset !== null) search(nextOffset); });
$("close-evidence").addEventListener("click", hideEvidence);
$("upload-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  if (importing || detecting || loading) return;
  const file = $("event-file").files[0];
  if (!file) return;
  $("import-details").hidden = true;
  if (file.size > 2 * 1024 * 1024) { status("upload-status", "Choose a file no larger than 2 MiB.", true); return; }
  importing = true;
  toggleSearch(true);
  status("upload-status", "Validating and saving records…");
  try {
    const result = await api("/api/import", {method: "POST", headers: {"Content-Type": "application/x-ndjson", "X-SentinelLab-Token": token}, body: file});
    status("upload-status", `Import complete: ${result.inserted} saved, ${result.duplicates} duplicates, ${result.conflicts} conflicts, ${result.rejected} rejected.`, Boolean(result.conflicts || result.rejected));
    $("import-report").textContent = JSON.stringify(result, null, 2);
    $("import-details").hidden = false;
    $("import-details").open = Boolean(result.conflicts || result.rejected);
    await refreshCounts();
    await search();
  } catch (error) { status("upload-status", error.message, true); }
  finally { importing = false; toggleSearch(false); }
});
refreshCounts().catch((error) => status("upload-status", error.message, true));
search();
