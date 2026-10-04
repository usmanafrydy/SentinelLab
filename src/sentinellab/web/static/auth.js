"use strict";
const loginForm = document.getElementById("login-form");
if (loginForm) {
  loginForm.addEventListener("submit", async event => {
    event.preventDefault();
    const button = document.getElementById("login-submit"), message = document.getElementById("login-status");
    if (button.disabled) return;
    button.disabled = true; message.textContent = "Checking your account…";
    try {
      const response = await fetch("/api/login", {method:"POST", credentials:"same-origin",
        headers:{"Content-Type":"application/json", "X-SentinelLab-Token":document.querySelector('meta[name="request-token"]').content},
        body:JSON.stringify({username:document.getElementById("login-username").value, password:document.getElementById("login-password").value})});
      const result = await response.json();
      document.getElementById("login-password").value = "";
      if (!response.ok) throw new Error(result.error || "Sign-in failed.");
      window.location.assign("/");
    } catch (error) { message.textContent = error.message; }
    finally { button.disabled = false; }
  });
} else {
  const account = document.querySelector('meta[name="account-name"]').content;
  for (const id of ["case-create-author","case-author"]) {
    document.getElementById(id).value = account;
    document.getElementById(id).readOnly = true;
  }
  document.getElementById("sign-out").addEventListener("click", async () => {
    const button = document.getElementById("sign-out");
    button.disabled = true;
    try { await api("/api/logout", {method:"POST", headers:{"Content-Type":"application/json", "X-SentinelLab-Token":token}, body:"{}"}); window.location.assign("/login"); }
    catch (error) { document.getElementById("session-status").textContent = error.message; button.disabled = false; }
  });
}
