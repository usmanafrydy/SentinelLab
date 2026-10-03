"use strict";
// Keep the same forms and application state; only their containing view changes.
const workspaceDefinitions = {
  overview: {title: "Follow the evidence.", hint: "A clear path from login records to a documented investigation.",
    targets: [".stats", ".getting-started"]},
  events: {title: "Login activity", hint: "Add records, narrow your search, and inspect what happened.",
    targets: ['section[aria-labelledby="import-title"]', 'section[aria-labelledby="search-title"]']},
  detection: {title: "Detection & alerts", hint: "Run an explicit check, understand a finding, then investigate it.",
    targets: ['section[aria-labelledby="detect-title"]', 'section[aria-labelledby="alerts-title"]', '#alert-detail', 'section[aria-labelledby="runs-title"]']},
  cases: {title: "Investigations", hint: "Keep observations, record a reasoned decision, and download saved work.",
    targets: ['section[aria-labelledby="cases-title"]', '#case-create-panel', '#case-detail']},
  evidence: {title: "Original evidence", hint: "Read the stored record. Viewing it never changes it.", targets: ['#evidence-panel']}
};
const workspaceViews = new Map();
let activeWorkspace = "overview", evidenceOrigin = "events", evidenceOriginFocus = null;
for (const [key, definition] of Object.entries(workspaceDefinitions)) {
  const view = document.createElement("div");
  view.dataset.workspace = key; view.id = `workspace-${key}`;
  for (const selector of definition.targets) view.append(document.querySelector(selector));
  document.querySelector("main").insertBefore(view, document.querySelector("noscript"));
  workspaceViews.set(key, view);
}
function workspaceFor(target) {
  return target?.closest("[data-workspace]")?.dataset.workspace;
}
function activateWorkspace(key) {
  for (const [name, view] of workspaceViews) view.hidden = name !== key;
  activeWorkspace = key;
  document.getElementById("workspace-title").textContent = workspaceDefinitions[key].title;
  document.getElementById("workspace-description").textContent = workspaceDefinitions[key].hint;
  document.title = `${key === "overview" ? "Overview" : workspaceDefinitions[key].title} | SentinelLab`;
  for (const link of document.querySelectorAll(".workspace-nav a")) {
    if (link.dataset.view === (key === "evidence" ? evidenceOrigin : key)) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  }
}
function focusWorkspaceTarget(target) {
  if (!target || target.dataset.workspace || target.closest("[hidden]")) target = document.getElementById("workspace-title");
  if (!target.matches("a,button,input,select,textarea,[tabindex]")) target.tabIndex = -1;
  target.focus({preventScroll: true}); target.scrollIntoView({block: "start"});
}
function revealWorkspace(targetId) {
  const target = document.getElementById(targetId), key = workspaceFor(target);
  if (!key) return;
  if (key === "evidence" && activeWorkspace !== "evidence") {
    evidenceOrigin = activeWorkspace; evidenceOriginFocus = document.activeElement;
  }
  activateWorkspace(key);
  if (location.hash !== `#${targetId}`) history.pushState(null, "", `#${targetId}`);
}
function leaveEvidenceWorkspace() {
  if (activeWorkspace !== "evidence") return;
  activateWorkspace(evidenceOrigin);
  history.replaceState(null, "", `#workspace-${evidenceOrigin}`);
  focusWorkspaceTarget(evidenceOriginFocus?.isConnected ? evidenceOriginFocus : null);
}
function followWorkspaceHash({focus = true} = {}) {
  let id;
  try { id = decodeURIComponent(location.hash.slice(1)); } catch { id = ""; }
  const target = document.getElementById(id);
  let key = workspaceFor(target);
  if (!key || (target.closest("[hidden]") && !target.closest("[data-workspace]")?.hidden)
      || (key === "evidence" && document.getElementById("evidence-panel").hidden)) key = "overview";
  // A hidden view is normal; a hidden record panel inside it is unavailable.
  if (key !== "overview" && target !== workspaceViews.get(key)) {
    let parent = target;
    while (parent && parent !== workspaceViews.get(key)) {
      if (parent.hidden) { key = "overview"; break; }
      parent = parent.parentElement;
    }
  }
  activateWorkspace(key);
  if (focus) focusWorkspaceTarget(key === workspaceFor(target) ? target : null);
}
document.addEventListener("click", event => {
  const link = event.target.closest('a[href^="#"]');
  if (!link || event.defaultPrevented || event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
  const id = link.getAttribute("href").slice(1);
  if (id === "workspace-title") {
    event.preventDefault(); focusWorkspaceTarget(document.getElementById(id)); return;
  }
  const target = document.getElementById(id);
  if (!workspaceFor(target)) return;
  event.preventDefault(); revealWorkspace(id); focusWorkspaceTarget(target);
});
window.addEventListener("popstate", () => followWorkspaceHash());
window.addEventListener("hashchange", () => followWorkspaceHash());
followWorkspaceHash({focus: false});
