// Encrypts dashboard.html with a six-digit PIN and writes the lock-screen index.html one level up.
// Run locally: DASHBOARD_PIN=###### node src/build-gate.mjs
// The PIN is never written to disk; the output contains only salt, IV, and ciphertext.

import { readFileSync, writeFileSync } from "node:fs";

const ITERATIONS = 600000;
const pin = process.env.DASHBOARD_PIN;
if (!/^\d{6}$/.test(pin ?? "")) {
  console.error("DASHBOARD_PIN must be exactly six digits");
  process.exit(1);
}

async function deriveKey(code, salt, usage) {
  const material = await crypto.subtle.importKey("raw", new TextEncoder().encode(code), "PBKDF2", false, ["deriveKey"]);
  return crypto.subtle.deriveKey(
    { name: "PBKDF2", salt, iterations: ITERATIONS, hash: "SHA-256" },
    material,
    { name: "AES-GCM", length: 256 },
    false,
    [usage]
  );
}

const plaintext = new TextEncoder().encode(readFileSync(new URL("./dashboard.html", import.meta.url), "utf8"));
const salt = crypto.getRandomValues(new Uint8Array(16));
const iv = crypto.getRandomValues(new Uint8Array(12));
const key = await deriveKey(pin, salt, "encrypt");
const ciphertext = new Uint8Array(await crypto.subtle.encrypt({ name: "AES-GCM", iv }, key, plaintext));
const payload = Buffer.concat([Buffer.from(salt), Buffer.from(iv), Buffer.from(ciphertext)]).toString("base64");

const shell = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Claude Code 360° — locked</title>
<style>
  :root{ color-scheme: light dark; }
  body{ margin:0; min-height:100vh; display:flex; align-items:center; justify-content:center; padding:24px;
    background:#f9f9f7; color:#0b0b0b; font-family:system-ui,-apple-system,"Segoe UI",sans-serif; }
  @media (prefers-color-scheme: dark){ body{ background:#0d0d0d; color:#ffffff; } }
  form{ width:min(320px,100%); text-align:center; }
  h1{ font-size:18px; margin:0 0 6px; }
  p{ font-size:13px; opacity:.7; margin:0 0 18px; }
  input, button{ box-sizing:border-box; display:block; width:100%; margin:0; }
  button{ margin-top:12px; }
  input{ width:100%; font-size:24px; letter-spacing:.4em; text-align:center; padding:10px; border-radius:10px;
    border:1px solid rgba(127,127,127,.4); background:transparent; color:inherit; }
  button{ margin-top:12px; width:100%; padding:10px; border:0; border-radius:10px; font-weight:700; font-size:14px;
    background:#2a78d6; color:#fff; cursor:pointer; }
  button:disabled{ opacity:.6; cursor:default; }
  #err{ min-height:18px; margin-top:12px; font-size:13px; color:#d03b3b; }
</style>
</head>
<body>
<form id="gate" autocomplete="off">
  <h1>Claude Code 360°</h1>
  <p>Enter the six-digit code to open this dashboard.</p>
  <input id="pin" name="pin" type="password" inputmode="numeric" pattern="[0-9]{6}" maxlength="6" required aria-label="Six-digit code">
  <button id="go" type="submit">Unlock</button>
  <div id="err" role="alert"></div>
</form>
<script>
(function(){
  "use strict";
  var PAYLOAD = "${payload}";
  var ITERATIONS = ${ITERATIONS};

  async function decrypt(code){
    var raw = Uint8Array.from(atob(PAYLOAD), function(c){ return c.charCodeAt(0); });
    var salt = raw.slice(0, 16), iv = raw.slice(16, 28), ciphertext = raw.slice(28);
    var material = await crypto.subtle.importKey("raw", new TextEncoder().encode(code), "PBKDF2", false, ["deriveKey"]);
    var key = await crypto.subtle.deriveKey(
      {name:"PBKDF2", salt:salt, iterations:ITERATIONS, hash:"SHA-256"}, material,
      {name:"AES-GCM", length:256}, false, ["decrypt"]);
    var plain = await crypto.subtle.decrypt({name:"AES-GCM", iv:iv}, key, ciphertext);
    return new TextDecoder().decode(plain);
  }

  document.getElementById("gate").addEventListener("submit", async function(e){
    e.preventDefault();
    var input = document.getElementById("pin"), go = document.getElementById("go"), err = document.getElementById("err");
    if(!/^\\d{6}$/.test(input.value)){ err.textContent = "Enter six digits."; return; }
    go.disabled = true; err.textContent = "";
    try{
      var html = await decrypt(input.value);
      document.open(); document.write(html); document.close();
    }catch(_){
      go.disabled = false; input.value = ""; input.focus();
      err.textContent = "That code didn't open the dashboard.";
    }
  });
})();
</script>
</body>
</html>
`;

writeFileSync(new URL("../index.html", import.meta.url), shell);
console.log(`wrote index.html (${payload.length} base64 chars of ciphertext)`);
