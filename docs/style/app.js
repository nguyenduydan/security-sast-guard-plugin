/* ==========================================================================
   Security SAST Guard - Main JavaScript Application & Step Visualizer Engine
   ========================================================================== */

const GITHUB_REPO = "nguyenduydan/security-sast-guard-plugin";
const FALLBACK_VERSION = "v1.8.11";
let activeCategory = "ALL";
let autoPlayTimer = null;
let isAutoPlaying = false;

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
  initScrollToTop();
  fetchLatestRelease();
});

/* --------------------------------------------------------------------------
   8. Scroll To Top Engine
   -------------------------------------------------------------------------- */
function initScrollToTop() {
  const btn = document.getElementById("scroll-to-top-btn");
  if (!btn) return;

  window.addEventListener("scroll", () => {
    if (window.scrollY > 300) {
      btn.classList.remove("opacity-0", "translate-y-4", "pointer-events-none");
      btn.classList.add("opacity-100", "translate-y-0", "pointer-events-auto");
    } else {
      btn.classList.remove("opacity-100", "translate-y-0", "pointer-events-auto");
      btn.classList.add("opacity-0", "translate-y-4", "pointer-events-none");
    }
  });
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: "smooth" });
}

/* --------------------------------------------------------------------------
   9. Global Window Event Handler Expositions
   -------------------------------------------------------------------------- */
window.toggleTheme = toggleTheme;
window.selectStep = selectStep;
window.toggleWorkflowAutoPlay = toggleWorkflowAutoPlay;
window.simulateCommand = simulateCommand;
window.handleCustomCommand = handleCustomCommand;
window.openRulesModal = openRulesModal;
window.closeRulesModal = closeRulesModal;
window.setCategory = setCategory;
window.filterRules = filterRules;
window.switchTab = switchTab;
window.copySnippet = copySnippet;
window.showCopyToast = showCopyToast;
window.scrollToTop = scrollToTop;

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
    ? '<i class="ph-bold ph-sun text-amber-400 text-lg inline-block theme-icon-spin"></i>'
    : '<i class="ph-bold ph-moon-stars text-slate-800 text-lg inline-block theme-icon-spin"></i>';
}

/* --------------------------------------------------------------------------
   2. Floating Cyber-HUD Dock Section Observer
   -------------------------------------------------------------------------- */
function initDockObserver() {
  const sections = document.querySelectorAll("section[id]");
  const navItems = document.querySelectorAll(".dock-item");

  const activeExists = Array.from(navItems).some((item) => item.classList.contains("nav-link-active"));
  if (!activeExists && navItems.length > 0) {
    const firstItem = document.querySelector('.dock-item[data-nav-section="firewall"]');
    if (firstItem) firstItem.classList.add("nav-link-active");
  }

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
    title: "Node 01-A: Intake & Requirements Gate (PreCommand Hook)",
    icon: "ph-clipboard-text",
    tag: "CLIENT & HOOK LAYER",
    badgeColor: "bg-emerald-500 text-black",
    description: "Intercepts shell execution before terminal run. Evaluates request intent and enforces profile constraints.",
    codeSnippet: `[Intake Service] Analyzing request context...\n[✓] Confidence Score: 98%\n[✓] Target Scope: src/domain/firewall_engine.py\n[✓] Profile Loaded: CWD .sast/profile.json (Level: FULL)\n[✓] Action Plan: Proceeding with zero ambiguity.`
  },
  {
    step: "1b",
    title: "Node 01-B: AI File Modifications Guard (PostToolCallExecute)",
    icon: "ph-code-simple",
    tag: "CLIENT & HOOK LAYER",
    badgeColor: "bg-emerald-500 text-black",
    description: "Triggers automatically after AI code modifications. Immediately runs SAST scan on generated diffs before saving to disk.",
    codeSnippet: `[PostToolCallExecute] File modified: src/domain/scanner.py\n[✓] Diff Extracted: +42 lines, -12 lines\n[✓] Auto-Scan Initiated against OWASP Vector Rules\n[✓] Zero vulnerabilities detected in generated diff.`
  },
  {
    step: "1c",
    title: "Node 01-C: Antigravity Slash Commands Suite",
    icon: "ph-terminal-window",
    tag: "CLIENT & HOOK LAYER",
    badgeColor: "bg-emerald-500 text-black",
    description: "Slash commands integrated into AI session (/sast-audit, /sast-init, /sast-mode, /sast-rules) for on-demand security auditing.",
    codeSnippet: `[Slash Commands] Executing /sast-audit file=src/app.py --level=ultra\n[✓] Scanning against 53 OWASP Vector Rules...\n[✓] Taint Dataflow Traces Extracted\n[✓] Zero critical vulnerabilities found.`
  },
  {
    step: 2,
    title: "Node 02-A: Command Firewall & Anti-Bypass Deobfuscator",
    icon: "ph-shield-warning",
    tag: "FIREWALL ENGINE",
    badgeColor: "bg-rose-500 text-white",
    description: "Executes PreCommandExecute hook. Strips obfuscation carets (^, \`) and decodes Base64 shell payloads before terminal execution.",
    codeSnippet: `[FirewallEngine] Evaluating command: "powershell -enc cm0gLXJmIC8="\n[!] Anti-Bypass Deobfuscation Triggered!\n[!] Decoded Payload: "rm -rf /"\n[✗] VERDICT: DENY (Dangerous pattern matched)\n[✓] Command Execution Blocked Safely.`
  },
  {
    step: "2b",
    title: "Node 02-B: PowerShell AST Parser & Pattern Matcher",
    icon: "ph-terminal-window",
    tag: "FIREWALL ENGINE",
    badgeColor: "bg-rose-500 text-white",
    description: "Parses PowerShell AST tokens and evaluates commands against ALLOW, CONFIRM, and DENY security rules.",
    codeSnippet: `[AST Parser] Analyzing command tokens: "Remove-Item -Path C:\\Windows -Recurse"\n[!] Match Found: Remove-Item (Destructive file deletion)\n[!] Action Required: User confirmation modal triggered\n[✓] VERDICT: CONFIRM.`
  },
  {
    step: "2c",
    title: "Node 02-C: Firewall Verdict Engine (DENY / CONFIRM / ALLOW)",
    icon: "ph-gavel",
    tag: "FIREWALL ENGINE",
    badgeColor: "bg-rose-500 text-white",
    description: "Enforces zero-trust command verdicts. DENY blocks destructive calls automatically; CONFIRM requests explicit user approval.",
    codeSnippet: `[Verdict Engine] Final Evaluation:\n  - DENY: Blocked "rm -rf /", "Format-Volume", "Disable-Defender"\n  - CONFIRM: Prompted user for "Remove-Item", "git push --force"\n  - ALLOW: Permitted clean read-only status commands.`
  },
  {
    step: "3a",
    title: "Node 03-A: Profile Cascade Resolver (.sast/profile.json)",
    icon: "ph-gear-six",
    tag: "CONTROL PLANE",
    badgeColor: "bg-cyan-500 text-black",
    description: "Resolves project configuration cascading from CWD (.sast/profile.json) -> Git Root -> Global Fallback (~/.gemini/config).",
    codeSnippet: `[Profile Cascade] Resolving settings...\n[✓] Local Profile Found: .sast/profile.json\n[✓] Audit Level: FULL (53 Rules Active)\n[✓] Operation Mode: STRICT (Fail-Closed Enforcement).`
  },
  {
    step: "core",
    title: "Node CORE: Stdio MCP Server (9 Stdio JSON-RPC Tools)",
    icon: "ph-cpu",
    tag: "CONTROL PLANE & MCP",
    badgeColor: "bg-brand-emerald text-black",
    description: "Central Stdio MCP Server exposing 9 specialized security tools (sast_scan_file, sast_scan_diff, sast_check_command, sast_init, etc.) to AI agent.",
    codeSnippet: `[MCP Server] Stdio JSON-RPC Transport Connected\n[✓] Available Tools: 9 Eager & Lazy Tools Registered\n[✓] Real-time JSON-RPC Query Processing Active\n[✓] Zero-Latency Subprocess IPC Communication.`
  },
  {
    step: "3c",
    title: "Node 03-C: Operation Mode & Audit Level Controls",
    icon: "ph-sliders-horizontal",
    tag: "CONTROL PLANE",
    badgeColor: "bg-cyan-500 text-black",
    description: "Controls strictness levels (lite, full, ultra) and operation modes (strict, draft). Parses inline # sast-ignore suppressions.",
    codeSnippet: `[Mode Engine] Active Settings:\n  - Mode: strict (Blocks execution on any Critical/High finding)\n  - Level: ultra (Includes dataflow taint tracking)\n  - Comment Suppression: # sast-ignore parsed on Line 88.`
  },
  {
    step: 3,
    title: "Node 03: 53 SAST Vector Audit Engine",
    icon: "ph-magnifying-glass-plus",
    tag: "SAST SCAN ENGINE",
    badgeColor: "bg-brand-cyan text-black",
    description: "Scans modified files against 53 OWASP Top 10, CWE Top 25, NIST 800-53, and ASP.NET security rules.",
    codeSnippet: `[SAST Audit] Scanning file: src/api/routes.py\n[!] Rule Triggered: OWASP-A03-SQLi (Critical)\n    Line 42: query = f"SELECT * FROM users WHERE id = '{user_id}'"\n[✓] AST Scope Extracted: Class UserHandler -> Method get_user()\n[✓] 1 Finding Registered.`
  },
  {
    step: 4,
    title: "Node 04: SHA-256 AI Response Cache",
    icon: "ph-brain",
    tag: "AI CACHE ENGINE",
    badgeColor: "bg-violet-500 text-white",
    description: "Queries LLM AI Verifier to filter false positives. Results cached locally with SHA-256 keys (24h TTL) for 0ms latency verification.",
    codeSnippet: `[AICache] Checking key: 8f9a2b4c1e7d...\n[✓] CACHE HIT! SHA-256 verification retrieved (Latency: 0ms)\n[✓] Verification Result: Valid Vulnerability Confirmed\n[✓] Suggested Remediation: Use Parameterized Queries.`
  },
  {
    step: 5,
    title: "Node 05: Report Generator & Audit Trail Logger",
    icon: "ph-file-text",
    tag: "EXPORTERS & LOGS",
    badgeColor: "bg-amber-500 text-black",
    description: "Generates ISO SARIF 2.1.0, Markdown, and JSON reports while logging audit decisions to .aiops/decisions.jsonl.",
    codeSnippet: `[Report Generator] SARIF report created: reports/sast_audit.sarif\n[Report Generator] Markdown report created: reports/sast_audit.md\n[Decision Log] Appended entry to .aiops/decisions.jsonl\n[✓] SAST Guard Workflow Execution Complete.`
  }
];

const WORKFLOW_MODES = {
  firewall: {
    activeNodes: ['1', '2', 'core', '2c', '5'],
    defaultStep: '2',
    btnId: 'mode-btn-firewall',
    btnClass: 'bg-rose-500 text-white'
  },
  autoscan: {
    activeNodes: ['1b', '2b', 'core', '4'],
    defaultStep: '1b',
    btnId: 'mode-btn-autoscan',
    btnClass: 'bg-emerald-500 text-black'
  },
  slash: {
    activeNodes: ['1c', '3a', 'core', '3c', '3'],
    defaultStep: '1c',
    btnId: 'mode-btn-slash',
    btnClass: 'bg-cyan-500 text-black'
  },
  all: {
    activeNodes: ['1', '1b', '1c', '2', '2b', '2c', '3a', 'core', '3c', '3', '4', '5'],
    defaultStep: 1,
    btnId: 'mode-btn-all',
    btnClass: 'bg-brand-emerald text-black'
  }
};

let currentWorkflowMode = 'firewall';

function initWorkflowVisualizer() {
  renderStepNodes();
  switchWorkflowMode('firewall');
  startAutoPlay();
}

function switchWorkflowMode(modeKey) {
  currentWorkflowMode = modeKey;
  const mode = WORKFLOW_MODES[modeKey];
  if (!mode) return;

  // 1. Update Mode Tab Buttons styling
  Object.keys(WORKFLOW_MODES).forEach((key) => {
    const btn = document.getElementById(WORKFLOW_MODES[key].btnId);
    if (btn) {
      if (key === modeKey) {
        btn.className = `mode-tab-btn px-3 py-1.5 rounded-lg text-xs font-mono font-black transition-all border-2 border-black shadow-brutal-sm ${WORKFLOW_MODES[key].btnClass}`;
      } else {
        btn.className = `mode-tab-btn px-3 py-1.5 rounded-lg text-xs font-mono font-black transition-all border-2 border-black bg-white dark:bg-obsidian-950 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-obsidian-850`;
      }
    }
  });

  // 2. Filter Packet Streams
  const firewallPackets = document.querySelector('.stream-packet-firewall');
  const autoscanPackets = document.querySelector('.stream-packet-autoscan');
  const slashPackets = document.querySelector('.stream-packet-slash');

  if (firewallPackets) firewallPackets.style.display = (modeKey === 'firewall' || modeKey === 'all') ? 'inline' : 'none';
  if (autoscanPackets) autoscanPackets.style.display = (modeKey === 'autoscan' || modeKey === 'all') ? 'inline' : 'none';
  if (slashPackets) slashPackets.style.display = (modeKey === 'slash' || modeKey === 'all') ? 'inline' : 'none';

  // 3. Filter Node Opacity
  WORKFLOW_STEPS.forEach((s) => {
    const node = document.getElementById(`step-node-${s.step}`);
    if (node) {
      if (mode.activeNodes.includes(String(s.step))) {
        node.style.opacity = "1";
      } else {
        node.style.opacity = "0.35";
      }
    }
  });

  // 4. Select default step for active workflow mode
  selectStep(mode.defaultStep);
}

function renderStepNodes() {
  // Static SVG Node Graph structure is defined in HTML docs/index.html
}

function selectStep(stepKey) {
  currentStep = stepKey;
  const stepData = WORKFLOW_STEPS.find((s) => String(s.step) === String(stepKey));
  if (!stepData) return;

  const modeObj = WORKFLOW_MODES[currentWorkflowMode] || WORKFLOW_MODES.all;

  WORKFLOW_STEPS.forEach((s) => {
    const node = document.getElementById(`step-node-${s.step}`);
    if (node) {
      const rect = node.querySelector('.node-rect');
      const isActiveInMode = modeObj.activeNodes.includes(String(s.step));

      if (String(s.step) === String(stepKey)) {
        node.classList.add("step-node-active");
        node.style.opacity = "1";
        if (rect) {
          rect.setAttribute("stroke-width", "3.5");
          rect.setAttribute("filter", "url(#neon-glow)");
        }
      } else {
        node.classList.remove("step-node-active");
        node.style.opacity = isActiveInMode ? "1" : "0.35";
        if (rect) {
          rect.setAttribute("stroke-width", "1.5");
          rect.removeAttribute("filter");
        }
      }
    }
  });

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
    lower.includes("diskutil") ||
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
    lower.includes("git checkout --") ||
    lower.includes("git restore") ||
    lower.includes("git reset --hard") ||
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
      let sevBadgeClass = "bg-black dark:bg-brand-cyan text-white dark:text-obsidian-950";
      if (r.severity === "CRITICAL") {
        sevBadgeClass = "bg-rose-600 dark:bg-rose-500 text-white font-black";
      } else if (r.severity === "HIGH") {
        sevBadgeClass = "bg-amber-500 text-black font-black";
      } else if (r.severity === "MEDIUM") {
        sevBadgeClass = "bg-cyan-500 text-black font-bold";
      } else if (r.severity === "LOW") {
        sevBadgeClass = "bg-slate-300 dark:bg-slate-700 text-black dark:text-white font-bold";
      }
      return `
      <div class="p-4 rounded-xl bg-slate-100 dark:bg-obsidian-900 border-2 border-black dark:border-white/10 space-y-2">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <span class="font-mono font-bold text-white dark:text-obsidian-950 bg-black dark:bg-brand-emerald px-2 py-0.5 rounded text-xs">${r.id}</span>
            <span class="font-display font-black text-black dark:text-white text-base">${r.name}</span>
          </div>
          <span class="text-[10px] font-mono px-2.5 py-0.5 rounded ${sevBadgeClass} uppercase tracking-wider">${r.severity}</span>
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
function parseVer(v) {
  return (v || "").replace(/^v/, "").split(".").map(Number);
}

function compareVer(v1, v2) {
  const a = parseVer(v1);
  const b = parseVer(v2);
  for (let i = 0; i < Math.max(a.length, b.length); i++) {
    const numA = a[i] || 0;
    const numB = b[i] || 0;
    if (numA > numB) return 1;
    if (numA < numB) return -1;
  }
  return 0;
}

async function fetchLatestRelease() {
  try {
    const res = await fetch(
      `https://api.github.com/repos/${GITHUB_REPO}/releases/latest`,
      { headers: { Accept: "application/vnd.github.v3+json" } }
    );
    if (!res.ok) throw new Error(`GitHub API ${res.status}`);
    const data = await res.json();
    let tag = data.tag_name || FALLBACK_VERSION;
    if (compareVer(FALLBACK_VERSION, tag) > 0) {
      tag = FALLBACK_VERSION;
    }
    applyVersionToPage(
      tag,
      data.html_url || `https://github.com/${GITHUB_REPO}/releases/tag/${tag}`
    );
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
  document.title = `Security SAST Guard ${tag} — Dual Theme Neo-Brutalist Security Platform`;
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

function initScrollSpy() {
  const sections = [...document.querySelectorAll('[data-nav-section]')]
    .map(link => document.getElementById(link.dataset.navSection))
    .filter(Boolean);
  const links = document.querySelectorAll('[data-nav-section]');
  const observer = new IntersectionObserver((entries) => {
    const visible = entries.filter(entry => entry.isIntersecting)
      .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
    if (!visible) return;
    links.forEach(link => {
      const active = link.dataset.navSection === visible.target.id;
      link.classList.toggle('nav-link-active', active);
      link.setAttribute('aria-current', active ? 'page' : 'false');
    });
  }, { rootMargin: '-18% 0px -62% 0px', threshold: [0.1, 0.35, 0.6] });
  sections.forEach(section => observer.observe(section));
}

/* --------------------------------------------------------------------------
   8. Global Window Event Handler Expositions
   -------------------------------------------------------------------------- */
window.toggleTheme = toggleTheme;
window.selectStep = selectStep;
window.toggleWorkflowAutoPlay = toggleWorkflowAutoPlay;
window.simulateCommand = simulateCommand;
window.handleCustomCommand = handleCustomCommand;
window.openRulesModal = openRulesModal;
window.closeRulesModal = closeRulesModal;
window.setCategory = setCategory;
window.filterRules = filterRules;
window.switchTab = switchTab;
window.copySnippet = copySnippet;
window.showCopyToast = showCopyToast;
window.syncVersionFromGitHub = fetchLatestRelease;
window.initScrollSpy = initScrollSpy;
