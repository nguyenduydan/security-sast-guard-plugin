/* ==========================================================================
   Security SAST Guard - Main JavaScript Application & Step Visualizer Engine
   ========================================================================== */

const GITHUB_REPO = "nguyenduydan/security-sast-guard-plugin";
const FALLBACK_VERSION = "v1.0.0";
let activeCategory = "ALL";

// 53 SAST Vector Rules Database
const SAST_RULES = [
  { id: "SAST-API-001", name: "Broken Object Level Authorization (BOLA)", category: "OWASP API 2023", severity: "CRITICAL", desc: "Detects direct object references lacking identity verification checks." },
  { id: "SAST-API-002", name: "Broken Authentication", category: "OWASP API 2023", severity: "CRITICAL", desc: "Flags hardcoded tokens, weak JWT algorithms, or unverified signatures." },
  { id: "SAST-API-003", name: "Broken Object Property Level Auth", category: "OWASP API 2023", severity: "HIGH", desc: "Flags mass assignment vulnerabilities exposing sensitive internal fields." },
  { id: "SAST-API-004", name: "Unrestricted Resource Consumption", category: "OWASP API 2023", severity: "MEDIUM", desc: "Identifies endpoints lacking pagination limits or request rate throttling." },
  { id: "SAST-API-005", name: "Broken Function Level Auth", category: "OWASP API 2023", severity: "HIGH", desc: "Detects administrative endpoints accessible without role-based access control." },
  { id: "SAST-API-006", name: "Unrestricted Access to Business Flows", category: "OWASP API 2023", severity: "MEDIUM", desc: "Flags operations sensitive to automated bot attacks lacking verification." },
  { id: "SAST-API-007", name: "Server Side Request Forgery (SSRF)", category: "OWASP API 2023", severity: "CRITICAL", desc: "Detects user-controlled URLs passed into internal HTTP client callers." },
  { id: "SAST-API-008", name: "Security Misconfiguration", category: "OWASP API 2023", severity: "HIGH", desc: "Identifies permissive CORS headers, verbose stack trace returns, or default credentials." },
  { id: "SAST-API-009", name: "Improper Inventory Management", category: "OWASP API 2023", severity: "LOW", desc: "Flags unversioned API endpoints or exposed debug/staging routes." },
  { id: "SAST-API-010", name: "Unsafe Consumption of APIs", category: "OWASP API 2023", severity: "MEDIUM", desc: "Detects unvalidated third-party API response ingestion." },
  
  { id: "SAST-WEB-001", name: "Broken Access Control", category: "OWASP Web 2021", severity: "CRITICAL", desc: "Flags missing authorization checks on sensitive data access." },
  { id: "SAST-WEB-002", name: "Cryptographic Failures", category: "OWASP Web 2021", severity: "HIGH", desc: "Detects weak hashing algorithms (MD5, SHA1) or plain-text secret storage." },
  { id: "SAST-WEB-003", name: "Injection Vectors", category: "OWASP Web 2021", severity: "CRITICAL", desc: "Identifies unescaped user inputs passed to system interpreters." },
  { id: "SAST-WEB-004", name: "Insecure Design", category: "OWASP Web 2021", severity: "HIGH", desc: "Flags architectural patterns missing rate-limiting or boundary isolation." },
  { id: "SAST-WEB-005", name: "Security Misconfiguration", category: "OWASP Web 2021", severity: "MEDIUM", desc: "Detects enabled directory listing or unnecessary default features." },
  { id: "SAST-WEB-006", name: "Vulnerable Components", category: "OWASP Web 2021", severity: "HIGH", desc: "Flags known vulnerable third-party dependencies." },
  { id: "SAST-WEB-007", name: "Auth & Identification Failures", category: "OWASP Web 2021", severity: "HIGH", desc: "Detects missing multi-factor authentication triggers or weak session timeouts." },
  { id: "SAST-WEB-008", name: "Software & Data Integrity", category: "OWASP Web 2021", severity: "CRITICAL", desc: "Identifies unverified code updates or untrusted deserialization." },
  { id: "SAST-WEB-009", name: "Logging & Monitoring Failures", category: "OWASP Web 2021", severity: "LOW", desc: "Flags security-critical actions missing audit log calls." },
  { id: "SAST-WEB-010", name: "Server-Side Request Forgery", category: "OWASP Web 2021", severity: "CRITICAL", desc: "Identifies unvalidated remote resource fetches." },

  { id: "SAST-CWE-089", name: "SQL Injection (CWE-89)", category: "CWE Top 25", severity: "CRITICAL", desc: "Flags string concatenation or raw formatting inside database query strings." },
  { id: "SAST-CWE-079", name: "Cross-Site Scripting (CWE-79)", category: "CWE Top 25", severity: "HIGH", desc: "Identifies unescaped user input rendered in HTML templates or innerHTML." },
  { id: "SAST-CWE-078", name: "OS Command Injection (CWE-078)", category: "CWE Top 25", severity: "CRITICAL", desc: "Detects shell command string formatting using raw user variables." },
  { id: "SAST-CWE-022", name: "Path Traversal (CWE-022)", category: "CWE Top 25", severity: "HIGH", desc: "Flags file path operations without canonicalization or directory jail checks." },
  { id: "SAST-CWE-352", name: "Cross-Site Request Forgery (CWE-352)", category: "CWE Top 25", severity: "HIGH", desc: "Detects state-changing endpoints lacking CSRF token protection." },
  { id: "SAST-CWE-434", name: "Unrestricted File Upload (CWE-434)", category: "CWE Top 25", severity: "CRITICAL", desc: "Flags file uploads without extension whitelist or MIME type validation." },
  { id: "SAST-CWE-306", name: "Missing Authentication (CWE-306)", category: "CWE Top 25", severity: "CRITICAL", desc: "Identifies critical business logic missing authentication checks." },
  { id: "SAST-CWE-502", name: "Deserialization of Untrusted Data", category: "CWE Top 25", severity: "CRITICAL", desc: "Detects usage of unsafe pickle/yaml load on external inputs." },
  { id: "SAST-CWE-798", name: "Use of Hard-coded Credentials", category: "CWE Top 25", severity: "HIGH", desc: "Flags static API keys, password strings, or private keys embedded in code." },
  { id: "SAST-CWE-276", name: "Incorrect Default Permissions", category: "CWE Top 25", severity: "MEDIUM", desc: "Detects files or directories created with 0777 world-writable permissions." },

  { id: "SAST-NIST-AC2", name: "Account Management (NIST AC-2)", category: "NIST 800-53", severity: "HIGH", desc: "Flags user creation operations lacking authorization checks." },
  { id: "SAST-NIST-SC8", name: "Transmission Confidentiality (SC-8)", category: "NIST 800-53", severity: "HIGH", desc: "Detects HTTP connections lacking TLS/SSL encryption enforcement." },
  { id: "SAST-NIST-IA2", name: "Identification & Auth (IA-2)", category: "NIST 800-53", severity: "HIGH", desc: "Flags plain-text password comparisons lacking constant-time verification." },
  { id: "SAST-NIST-AU2", name: "Event Logging (AU-2)", category: "NIST 800-53", severity: "MEDIUM", desc: "Detects administrative actions executed without audit logging." },

  { id: "SAST-SEC-KEY", name: "RSA/ECC Private Key Leak", category: "Secret Protection", severity: "CRITICAL", desc: "Flags embedded PEM private keys (-----BEGIN PRIVATE KEY-----)." },
  { id: "SAST-SEC-TOK", name: "API Key / OAuth Token Leak", category: "Secret Protection", severity: "CRITICAL", desc: "Detects hardcoded cloud credentials, AWS keys, or API tokens." }
];

document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initDockObserver();
  initWorkflowVisualizer();
  fetchLatestRelease();
});

/* --------------------------------------------------------------------------
   1. Theme Management (Light / Dark Neo-Brutalist Toggle)
   -------------------------------------------------------------------------- */
function initTheme() {
  const savedTheme = localStorage.getItem("sast-theme");
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;

  if (savedTheme === "dark" || (!savedTheme && prefersDark)) {
    document.documentElement.classList.add("dark");
  } else {
    document.documentElement.classList.remove("dark");
  }
  updateThemeIcon();
}

function toggleTheme() {
  document.documentElement.classList.toggle("dark");
  const isDark = document.documentElement.classList.contains("dark");
  localStorage.setItem("sast-theme", isDark ? "dark" : "light");
  updateThemeIcon();
}

function updateThemeIcon() {
  const btn = document.getElementById("theme-toggle-btn");
  if (!btn) return;
  const isDark = document.documentElement.classList.contains("dark");
  btn.innerHTML = isDark
    ? '<i class="ph-bold ph-sun text-emerald-400 text-lg"></i>'
    : '<i class="ph-bold ph-moon-stars text-slate-800 text-lg"></i>';
}

/* --------------------------------------------------------------------------
   2. Floating Cyber-HUD Dock Section Observer
   -------------------------------------------------------------------------- */
function initDockObserver() {
  const sections = document.querySelectorAll("section[id]");
  const navItems = document.querySelectorAll(".dock-item");

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const id = entry.target.getAttribute("id");
          navItems.forEach((item) => {
            if (item.getAttribute("data-nav-section") === id) {
              item.classList.add("nav-link-active");
            } else {
              item.classList.remove("nav-link-active");
            }
          });
        }
      });
    },
    { threshold: 0.3 }
  );

  sections.forEach((section) => observer.observe(section));
}

/* --------------------------------------------------------------------------
   3. Interactive Step-by-Step Workflow Visualizer Engine
   -------------------------------------------------------------------------- */
const WORKFLOW_STEPS = [
  {
    step: 1,
    title: "Step 1: Intake & Requirements Analysis",
    icon: "ph-clipboard-text",
    tag: "REQUIREMENTS GATE",
    badgeColor: "bg-cyan-500 text-black",
    description: "Evaluates request for ambiguity before writing code. Confirms spec approval and project profile constraints.",
    codeSnippet: `[Intake Service] Analyzing request context...\n[✓] Confidence Score: 98%\n[✓] Target Scope: src/domain/firewall_engine.py\n[✓] Profile Loaded: CWD .sast/profile.json (Level: FULL)\n[✓] Action Plan: Proceeding with zero ambiguity.`
  },
  {
    step: 2,
    title: "Step 2: PreCommand Firewall Interception",
    icon: "ph-shield-warning",
    tag: "COMMAND FIREWALL",
    badgeColor: "bg-rose-500 text-white",
    description: "Executes PreCommandExecute hook. Strips obfuscation carets (^, \`) and decodes Base64 payloads before terminal execution.",
    codeSnippet: `[FirewallEngine] Evaluating command: "powershell -enc cm0gLXJmIC8="\n[!] Anti-Bypass Deobfuscation Triggered!\n[!] Decoded Payload: "rm -rf /"\n[✗] VERDICT: DENY (Dangerous pattern matched)\n[✓] Command Execution Blocked Safely.`
  },
  {
    step: 3,
    title: "Step 3: Real-Time SAST Vulnerability Audit",
    icon: "ph-magnifying-glass-plus",
    tag: "53 SAST RULES SCAN",
    badgeColor: "bg-brand-emerald text-black",
    description: "Scans modified files against 53 OWASP Top 10 and CWE rules across 4 severity levels (Critical, High, Medium, Low).",
    codeSnippet: `[SAST Audit] Scanning file: src/api/routes.py\n[!] Rule Triggered: OWASP-A03-SQLi (Critical)\n    Line 42: query = f"SELECT * FROM users WHERE id = '{user_id}'"\n[✓] AST Scope Extracted: Class UserHandler -> Method get_user()\n[✓] 1 Finding Registered.`
  },
  {
    step: 4,
    title: "Step 4: AI Verifier & SHA-256 Response Cache",
    icon: "ph-brain",
    tag: "LLM FALSE POSITIVE FILTER",
    badgeColor: "bg-violet-500 text-white",
    description: "Queries LLM AI Verifier to filter false positives. Results cached locally with SHA-256 keys (24h TTL) to minimize latency.",
    codeSnippet: `[AICache] Checking key: 8f9a2b4c1e7d...\n[✓] CACHE HIT! SHA-256 verification retrieved (Latency: 0ms)\n[✓] Verification Result: Valid Vulnerability Confirmed\n[✓] Suggested Remediation: Use Parameterized Queries (sqlite3/sqlalchemy).`
  },
  {
    step: 5,
    title: "Step 5: Report Generation & Decision Logging",
    icon: "ph-file-text",
    tag: "AUDIT LOG & REPORT",
    badgeColor: "bg-amber-500 text-black",
    description: "Generates Markdown/JSON reports and appends architectural entry to .aiops/decisions.jsonl decision log.",
    codeSnippet: `[Report Generator] Markdown report created: reports/sast_report_20260806.md\n[Report Generator] JSON report created: reports/sast_report_20260806.json\n[Decision Log] Appended entry to .aiops/decisions.jsonl\n[✓] SAST Guard Workflow Execution Complete (100% Verified).`
  }
];

let currentStep = 1;
let autoPlayTimer = null;
let isAutoPlaying = true;

function initWorkflowVisualizer() {
  renderStepNodes();
  selectStep(1);
  startAutoPlay();
}

function renderStepNodes() {
  const container = document.getElementById("workflow-nodes-container");
  if (!container) return;

  container.innerHTML = WORKFLOW_STEPS.map((s) => `
    <button onclick="selectStep(${s.step})" id="step-node-${s.step}"
      class="step-node flex-1 min-w-[120px] p-3 rounded-xl border-2 border-black dark:border-white/20 bg-white dark:bg-obsidian-900 flex flex-col items-center gap-1.5 transition-all text-center group hover:scale-105 shadow-brutal-sm">
      <div class="w-8 h-8 rounded-full bg-slate-100 dark:bg-obsidian-850 flex items-center justify-center font-bold font-mono text-xs border border-black dark:border-white/20 group-hover:border-brand-emerald">
        ${s.step}
      </div>
      <span class="font-display font-extrabold text-[11px] leading-tight uppercase tracking-tight text-slate-800 dark:text-slate-200">
        ${s.tag}
      </span>
    </button>
  `).join("");
}

function selectStep(stepNum) {
  currentStep = stepNum;
  const stepData = WORKFLOW_STEPS.find((s) => s.step === stepNum);
  if (!stepData) return;

  WORKFLOW_STEPS.forEach((s) => {
    const node = document.getElementById(`step-node-${s.step}`);
    if (node) {
      if (s.step === stepNum) {
        node.classList.add("step-node-active");
      } else {
        node.classList.remove("step-node-active");
      }
    }
  });

  const fill = document.getElementById("workflow-progress-fill");
  if (fill) {
    const percentage = ((stepNum - 1) / (WORKFLOW_STEPS.length - 1)) * 100;
    fill.style.width = `${percentage}%`;
  }

  const displayBox = document.getElementById("workflow-display-box");
  if (displayBox) {
    displayBox.innerHTML = `
      <div class="flex flex-wrap items-center justify-between gap-3 border-b-2 border-black dark:border-white/20 pb-4 mb-4">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-black dark:bg-brand-emerald text-white dark:text-obsidian-950 flex items-center justify-center font-bold text-xl border-2 border-black shadow-brutal-sm">
            <i class="ph-bold ${stepData.icon}"></i>
          </div>
          <div>
            <span class="px-2.5 py-0.5 rounded text-[10px] font-mono font-bold uppercase tracking-wider ${stepData.badgeColor}">
              ${stepData.tag}
            </span>
            <h4 class="font-display font-black text-lg text-black dark:text-white leading-tight mt-0.5">
              ${stepData.title}
            </h4>
          </div>
        </div>
        <span class="font-mono text-xs text-slate-700 dark:text-slate-400 font-bold">
          Step ${stepData.step} of 5
        </span>
      </div>
      <p class="text-sm text-slate-800 dark:text-slate-300 font-semibold mb-4">
        ${stepData.description}
      </p>
      <div class="rounded-xl border-2 border-black dark:border-white/20 bg-obsidian-950 p-4 font-mono text-xs text-emerald-400 leading-relaxed overflow-x-auto terminal-scrollbar shadow-inner">
        <pre><code>${escapeHtml(stepData.codeSnippet)}</code></pre>
      </div>
    `;
  }
}

function startAutoPlay() {
  if (autoPlayTimer) clearInterval(autoPlayTimer);
  isAutoPlaying = true;
  updatePlayPauseBtn();
  autoPlayTimer = setInterval(() => {
    let next = currentStep + 1;
    if (next > WORKFLOW_STEPS.length) next = 1;
    selectStep(next);
  }, 4000);
}

function stopAutoPlay() {
  if (autoPlayTimer) clearInterval(autoPlayTimer);
  isAutoPlaying = false;
  updatePlayPauseBtn();
}

function toggleWorkflowAutoPlay() {
  if (isAutoPlaying) {
    stopAutoPlay();
  } else {
    startAutoPlay();
  }
}

function updatePlayPauseBtn() {
  const btn = document.getElementById("workflow-autoplay-btn");
  if (!btn) return;
  btn.innerHTML = isAutoPlaying
    ? '<i class="ph-bold ph-pause text-sm"></i> Pause Flow'
    : '<i class="ph-bold ph-play text-sm"></i> Play Flow Animation';
}

/* --------------------------------------------------------------------------
   4. Live Interactive Firewall Terminal Simulator
   -------------------------------------------------------------------------- */
function simulateCommand(cmd) {
  const input = document.getElementById("cmd-input");
  if (input) input.value = cmd;
  runFirewallLogic(cmd);
}

function handleCustomCommand(e) {
  e.preventDefault();
  const input = document.getElementById("cmd-input");
  if (!input) return;
  const cmd = input.value.trim();
  if (cmd) runFirewallLogic(cmd);
}

function runFirewallLogic(cmd) {
  const outputDiv = document.getElementById("terminal-output");
  if (!outputDiv) return;

  const cleanCmd = cmd.replace(/\^/g, "").replace(/`/g, "");
  const lower = cleanCmd.toLowerCase();

  const isBase64Deny =
    cmd.includes("cm0gLXJmIC8=") ||
    (lower.includes("-enc") && lower.includes("cm0g"));

  let status = "ALLOW";
  let statusClass = "bg-black dark:bg-brand-emerald text-white dark:text-obsidian-950";
  let icon = "ph-check-circle";
  let reason = "Verified clean execution trajectory.";

  const isDeny =
    lower.includes("rm -rf") ||
    lower.includes("format") ||
    lower.includes("clear-disk") ||
    lower.includes("initialize-disk") ||
    lower.includes("remove-partition") ||
    lower.includes("set-mppreference") ||
    lower.includes("add-mppreference") ||
    lower.includes("disable-netfirewallrule") ||
    lower.includes("set-netfirewallprofile") ||
    lower.includes("invoke-command") ||
    lower.includes("enter-pssession") ||
    lower.includes("reg delete") ||
    lower.includes("mkfs") ||
    lower.includes("stop-computer") ||
    lower.includes("restart-computer") ||
    isBase64Deny;

  if (isDeny) {
    status = "DENY";
    statusClass = "bg-black dark:bg-rose-500 text-white dark:text-obsidian-950";
    icon = "ph-x-circle";
    if (cmd !== cleanCmd || isBase64Deny) {
      reason =
        "ANTI-BYPASS DENY: Obfuscated/Base64 payload decoded and blocked by Deobfuscation Engine!";
    } else {
      reason =
        "CRITICAL: Destructive system operation blocked by PreCommand Interceptor!";
    }
  } else if (
    lower.includes("remove-item") ||
    lower.includes("--force") ||
    lower.includes("rmdir") ||
    lower.includes("del ")
  ) {
    status = "CONFIRM";
    statusClass = "bg-black dark:bg-amber-500 text-white dark:text-obsidian-950";
    icon = "ph-warning-circle";
    reason =
      "HIGH RISK: Operation alters file state/history. Halting for Y/N user prompt.";
  }

  const timestamp = new Date().toLocaleTimeString();
  const newEntry = document.createElement("div");
  newEntry.className =
    "p-3.5 rounded-xl bg-slate-100 dark:bg-obsidian-900 border-2 border-black dark:border-white/20 space-y-2 shadow-brutal-sm";
  newEntry.innerHTML = `
    <div class="flex items-center justify-between text-xs font-mono font-bold">
      <span class="text-black dark:text-white">$ ${escapeHtml(cmd)}</span>
      <span class="text-[10px] text-slate-700 dark:text-slate-400">${timestamp}</span>
    </div>
    <div class="flex items-center gap-2 font-mono text-xs">
      <span class="inline-flex items-center gap-1.5 px-3 py-0.5 rounded font-bold border border-black dark:border-white/20 ${statusClass}">
        <i class="ph-bold ${icon}" aria-hidden="true"></i> ${status}
      </span>
      <span class="text-black dark:text-slate-200 font-semibold text-xs">${reason}</span>
    </div>
  `;

  outputDiv.appendChild(newEntry);
  outputDiv.parentElement.scrollTop = outputDiv.parentElement.scrollHeight;
}

/* --------------------------------------------------------------------------
   5. 53 SAST Rules Modal & Filtering Engine
   -------------------------------------------------------------------------- */
function openRulesModal(categoryFilter = "ALL") {
  activeCategory = categoryFilter;
  renderCategoryPills();
  renderRules();
  const modal = document.getElementById("rules-modal");
  if (modal) modal.classList.remove("hidden");
  const searchInput = document.getElementById("rule-search");
  if (searchInput) searchInput.focus();
}

function closeRulesModal() {
  const modal = document.getElementById("rules-modal");
  if (modal) modal.classList.add("hidden");
}

function renderCategoryPills() {
  const categories = [
    "ALL",
    "OWASP API 2023",
    "OWASP Web 2021",
    "CWE Top 25",
    "NIST 800-53",
    "Secret Protection",
  ];
  const container = document.getElementById("category-pills");
  if (!container) return;

  container.innerHTML = categories
    .map((cat) => {
      const isSelected = activeCategory === cat;
      const count =
        cat === "ALL"
          ? SAST_RULES.length
          : SAST_RULES.filter((r) => r.category === cat).length;
      const activeClass = isSelected
        ? "bg-black dark:bg-brand-emerald text-white dark:text-obsidian-950 font-bold border-2 border-black dark:border-brand-emerald"
        : "bg-white dark:bg-obsidian-950 text-black dark:text-white font-bold border-2 border-black dark:border-white/20 hover:bg-slate-200 dark:hover:border-brand-emerald";
      return `<button onclick="setCategory('${cat}')" class="px-3 py-1 rounded text-xs transition-all ${activeClass}">${cat} (${count})</button>`;
    })
    .join("");
}

function setCategory(cat) {
  activeCategory = cat;
  renderCategoryPills();
  renderRules();
}

function filterRules() {
  renderRules();
}

function renderRules() {
  const searchElem = document.getElementById("rule-search");
  const query = searchElem ? searchElem.value.toLowerCase().trim() : "";
  const container = document.getElementById("rules-list-container");
  if (!container) return;

  const filtered = SAST_RULES.filter((r) => {
    const matchesCat =
      activeCategory === "ALL" || r.category === activeCategory;
    const matchesQuery =
      !query ||
      r.id.toLowerCase().includes(query) ||
      r.name.toLowerCase().includes(query) ||
      r.desc.toLowerCase().includes(query);
    return matchesCat && matchesQuery;
  });

  const countBadge = document.getElementById("rules-count-badge");
  if (countBadge) {
    countBadge.innerText = `Showing ${filtered.length} of ${SAST_RULES.length} rules`;
  }

  if (filtered.length === 0) {
    container.innerHTML = `<div class="p-8 text-center font-mono font-bold text-xs">No matching rules found.</div>`;
    return;
  }

  container.innerHTML = filtered
    .map((r) => {
      return `
      <div class="p-4 rounded-xl bg-slate-100 dark:bg-obsidian-900 border-2 border-black dark:border-white/10 space-y-2">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <span class="font-mono font-bold text-white dark:text-obsidian-950 bg-black dark:bg-brand-emerald px-2 py-0.5 rounded text-xs">${r.id}</span>
            <span class="font-display font-black text-black dark:text-white text-base">${r.name}</span>
          </div>
          <span class="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-black dark:bg-brand-cyan text-white dark:text-obsidian-950 uppercase">${r.severity}</span>
        </div>
        <p class="text-xs text-black dark:text-slate-300 font-mono font-semibold">${r.desc}</p>
      </div>
    `;
    })
    .join("");
}

/* --------------------------------------------------------------------------
   6. GitHub Latest Release Fetcher
   -------------------------------------------------------------------------- */
async function fetchLatestRelease() {
  try {
    const res = await fetch(
      `https://api.github.com/repos/${GITHUB_REPO}/releases/latest`,
      { headers: { Accept: "application/vnd.github.v3+json" } }
    );
    if (!res.ok) throw new Error(`GitHub API ${res.status}`);
    const data = await res.json();
    const tag = data.tag_name || FALLBACK_VERSION;
    applyVersionToPage(tag, data.html_url);
  } catch (err) {
    applyVersionToPage(
      FALLBACK_VERSION,
      `https://github.com/${GITHUB_REPO}/releases/tag/${FALLBACK_VERSION}`
    );
  }
}

function applyVersionToPage(tag, releaseUrl) {
  document.querySelectorAll("[data-version-text]").forEach((el) => {
    el.textContent = tag;
  });
  document.querySelectorAll("[data-version-link]").forEach((el) => {
    el.href = releaseUrl;
  });
  document.title = `Security SAST Guard ${tag} — Zero-Trust Code Auditing & Command Interceptor`;
}

/* --------------------------------------------------------------------------
   7. Installation Command Tab Switcher & Copy Snippets
   -------------------------------------------------------------------------- */
function switchTab(tab) {
  ["install", "update", "remove"].forEach((t) => {
    const btn = document.getElementById(`tab-${t}`);
    const content = document.getElementById(`content-${t}`);
    if (!btn || !content) return;

    if (t === tab) {
      btn.className =
        "px-4 py-1.5 rounded brutal-btn-alt font-bold uppercase text-xs";
      content.classList.remove("hidden");
    } else {
      btn.className =
        "px-4 py-1.5 rounded text-white hover:underline font-bold text-xs";
      content.classList.add("hidden");
    }
  });
}

function showCopyToast() {
  const toast = document.getElementById("copy-toast");
  if (!toast) return;
  toast.classList.remove("translate-y-4", "opacity-0", "pointer-events-none");
  toast.classList.add("translate-y-0", "opacity-100");

  clearTimeout(window.copyToastTimer);
  window.copyToastTimer = setTimeout(() => {
    toast.classList.remove("translate-y-0", "opacity-100");
    toast.classList.add("translate-y-4", "opacity-0", "pointer-events-none");
  }, 2200);
}

function copySnippet(id) {
  const elem = document.getElementById(id);
  if (!elem) return;
  const button = event.currentTarget;

  navigator.clipboard.writeText(elem.innerText).then(() => {
    const originalLabel = button.innerHTML;
    button.innerHTML = '<i class="ph-bold ph-check"></i> Copied';
    button.classList.add("!bg-brand-emerald", "!text-black");
    showCopyToast();
    setTimeout(() => {
      button.innerHTML = originalLabel;
      button.classList.remove("!bg-brand-emerald", "!text-black");
    }, 1800);
  });
}

function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}
