# Security Supervisor Project Review Prompt

You are a Principal Application Security Architect, AI Agent Security Engineer, Endpoint Security Specialist, DevSecOps Architect, and Open-Source Security Tool Maintainer.

Your task is to perform a deep, brutally honest, evidence-based review of the following project:

## Project

Security SAST Guard Plugin

Repository:

https://github.com/nguyenduydan/security-sast-guard-plugin

Documentation:

https://nguyenduydan.github.io/security-sast-guard-plugin/

Before evaluating the project, inspect the repository, documentation, architecture, configuration, detection rules, execution flow, and available examples.

Do not treat this project as a traditional code-fixing assistant.

The primary purpose of this project is to act as an independent security supervisor for AI coding agents.

Its core responsibilities are:

* Detect dangerous shell, CMD, PowerShell, Bash, terminal, and system commands.
* Block dangerous commands before execution.
* Continue enforcing security controls even when the AI agent has been granted full permissions.
* Monitor code generated or modified by AI agents.
* Detect security vulnerabilities as early as possible during the coding process.
* Warn, block, or escalate risky behavior according to configured security policies.
* Operate independently from the AI agent being supervised.
* Prevent the supervised agent from bypassing, disabling, or manipulating security controls.
* Produce security findings that can later be passed to another specialized agent for remediation.

The project is not responsible for directly fixing vulnerable code.

Code remediation, patch generation, refactoring, and automatic fixes belong to a separate agent or workflow.

The system should therefore be evaluated as:

> An independent security and cybersecurity supervisor for autonomous AI coding agents.

---

# 1. Product Identity and Positioning

Evaluate whether the project should be positioned as:

* AI Security Supervisor
* AI Agent Security Guard
* Runtime Command Security Gateway
* SAST Security Supervisor
* AI Coding Security Middleware
* Agent Execution Firewall
* Security Control Plane for AI Agents
* AI Agent Governance Layer

Determine the strongest and most technically accurate positioning.

Explain:

* What the product truly is.
* What it is not.
* Which name best communicates its role.
* Who the intended users are.
* Which threats it is designed to stop.
* Why this project should remain independent from the AI coding agent.
* How it differs from a traditional SAST scanner.
* How it differs from a code-fixing assistant.
* How it differs from an operating-system sandbox.
* How it differs from endpoint detection and response software.
* How it differs from an AI orchestration framework.

Propose a clear product category and a concise positioning statement.

---

# 2. Core Security Model

Review the project's security model in depth.

Determine whether the architecture can reliably enforce security controls even when the supervised AI agent has:

* Full file-system access.
* Shell access.
* Administrator or root privileges.
* Permission to install packages.
* Permission to run arbitrary scripts.
* Permission to modify project files.
* Permission to invoke external tools.
* Permission to spawn child processes.
* Permission to access environment variables.
* Permission to execute PowerShell, CMD, Bash, Python, Node.js, or other interpreters.

Evaluate whether the project is genuinely capable of supervising a fully privileged agent or whether it currently relies on voluntary compliance from the agent.

Identify any trust assumptions.

Explain what components must remain outside the control of the supervised agent.

---

# 3. Threat Model

Create a complete threat model for the project.

Cover at least the following threat actors:

* A hallucinating AI agent.
* An overly aggressive autonomous agent.
* A compromised AI agent.
* A malicious prompt.
* Prompt injection from repository files.
* Prompt injection from documentation.
* Prompt injection from terminal output.
* Prompt injection from tool responses.
* Supply-chain attacks.
* Malicious dependencies.
* A developer accidentally approving a dangerous operation.
* A malicious repository attempting to disable the supervisor.
* A child process spawned by the supervised agent.
* A script that indirectly executes dangerous commands.
* An encoded or obfuscated command.
* A command split across multiple execution steps.
* A command hidden inside another interpreter.

For each threat, identify:

* Attack path.
* Security impact.
* Current protection.
* Missing protection.
* Recommended enforcement layer.
* Residual risk.

---

# 4. Dangerous Command Detection

Evaluate the project's ability to detect and block dangerous commands across:

* Windows CMD.
* PowerShell.
* Bash.
* Zsh.
* Fish.
* Python subprocess execution.
* Node.js child processes.
* C# Process.Start.
* Java Runtime.exec.
* Shell scripts.
* Batch files.
* Makefiles.
* Package manager scripts.
* Git hooks.
* Build scripts.
* CI/CD scripts.
* Docker commands.
* Container runtime commands.
* Cloud CLI commands.
* Database administration commands.
* Network administration commands.

Review support for dangerous operations such as:

* Recursive file deletion.
* Disk formatting.
* Partition modification.
* Boot configuration modification.
* Registry modification.
* Firewall disabling.
* Antivirus disabling.
* Security policy modification.
* User and group manipulation.
* Privilege escalation.
* Permission changes.
* Ownership changes.
* Service installation.
* Service deletion.
* Process termination.
* Credential dumping.
* Secret extraction.
* Environment-variable exposure.
* Network exfiltration.
* Reverse shells.
* Remote code execution.
* Download-and-execute patterns.
* Encoded PowerShell.
* Obfuscated commands.
* Persistence mechanisms.
* Scheduled tasks.
* Startup-folder modification.
* SSH key modification.
* Git credential access.
* Browser credential access.
* Destructive database commands.
* Force pushes.
* Repository history rewriting.
* Package publication.
* Infrastructure deletion.
* Cloud resource destruction.

Determine whether detection is based only on string matching or whether it understands command semantics.

---

# 5. Command Normalization and Deobfuscation

Evaluate whether the system normalizes commands before applying security rules.

Review support for:

* Case normalization.
* Whitespace normalization.
* Environment-variable expansion.
* Alias resolution.
* Relative path resolution.
* Quoted-string parsing.
* Escaped characters.
* Command concatenation.
* Command substitution.
* Pipe chains.
* Redirection.
* Semicolon-separated commands.
* Conditional execution.
* Nested interpreters.
* Base64-encoded commands.
* Hex-encoded commands.
* Unicode obfuscation.
* Caret escaping in CMD.
* Backtick escaping in PowerShell.
* Variable-based command construction.
* String concatenation.
* Delayed expansion.
* Shell aliases.
* Wrapper scripts.
* Indirect execution through package managers.
* Execution through temporary files.

Explain how attackers or autonomous agents could bypass naïve pattern matching.

Recommend a robust command-parsing and canonicalization architecture.

---

# 6. Enforcement and Blocking

Determine how commands are intercepted and blocked.

Evaluate whether enforcement occurs:

* Before command execution.
* At the tool invocation layer.
* At the process creation layer.
* Through shell wrappers.
* Through operating-system hooks.
* Through policy engines.
* Through sandbox boundaries.
* Through agent middleware.
* Through CLI proxying.
* Through kernel or endpoint controls.

Assess whether the current blocking mechanism is:

* Advisory.
* Best-effort.
* Mandatory.
* Tamper-resistant.
* Fail-open.
* Fail-closed.

Explain what happens when:

* The supervisor crashes.
* The rule engine fails.
* The configuration cannot be loaded.
* A timeout occurs.
* The command parser fails.
* The agent invokes a shell directly.
* The agent bypasses the expected CLI wrapper.
* The agent spawns a child process.
* The agent invokes an alternate interpreter.
* The agent modifies the supervisor's files.
* The agent disables hooks.
* The agent changes environment variables.
* The agent removes the plugin.

Recommend a fail-closed enforcement design.

---

# 7. Anti-Bypass and Tamper Resistance

Review how the project prevents the supervised agent from:

* Disabling the plugin.
* Editing security rules.
* Deleting logs.
* Modifying configuration.
* Replacing the command wrapper.
* Calling executables directly.
* Using an alternate shell.
* Running commands through another process.
* Encoding dangerous commands.
* Splitting dangerous operations across steps.
* Modifying the PATH.
* Replacing system binaries.
* Escaping the workspace.
* Spawning unsupervised subprocesses.
* Creating scheduled tasks.
* Installing persistence.
* Launching another autonomous agent.
* Modifying CI/CD workflows.
* Disabling security scanning.
* Marking dangerous findings as ignored.

Clearly identify which protections can be implemented at the application layer and which require operating-system enforcement.

Do not overstate the protection level.

---

# 8. SAST Monitoring of AI-Generated Code

Evaluate the project's ability to detect vulnerabilities while AI agents create or modify code.

Review support for:

* Incremental scanning.
* Changed-file scanning.
* Diff-based scanning.
* Pre-write scanning.
* Post-write scanning.
* Pre-commit scanning.
* Continuous workspace monitoring.
* Cross-file analysis.
* Language-specific analyzers.
* Framework-specific rules.
* Dependency-aware detection.
* Secret detection.
* Configuration scanning.
* Infrastructure-as-code scanning.
* CI/CD workflow scanning.

Evaluate detection capability for:

* SQL injection.
* Cross-site scripting.
* Command injection.
* Path traversal.
* Server-side request forgery.
* Insecure deserialization.
* Authentication flaws.
* Authorization flaws.
* IDOR.
* Hardcoded secrets.
* Weak cryptography.
* Unsafe file uploads.
* Arbitrary file writes.
* Unsafe process execution.
* Insecure temporary files.
* Sensitive data exposure.
* Misconfigured CORS.
* Missing security headers.
* Open redirects.
* XML external entities.
* Template injection.
* Prototype pollution.
* Race conditions.
* Unsafe dependency usage.
* Dangerous regular expressions.
* Insecure infrastructure configuration.

Determine whether the current SAST engine is suitable for early warning or whether it is being presented as more capable than it actually is.

---

# 9. Separation of Detection and Remediation

Verify that the project maintains strict separation between:

## Security Supervisor

Responsible for:

* Monitoring.
* Detection.
* Blocking.
* Warning.
* Classification.
* Logging.
* Risk scoring.
* Policy enforcement.
* Escalation.
* Producing structured findings.

## Remediation Agent

Responsible for:

* Understanding findings.
* Proposing code changes.
* Creating patches.
* Refactoring code.
* Running tests.
* Requesting approval.
* Applying fixes.

Evaluate whether the current architecture accidentally mixes these responsibilities.

Recommend a clean integration contract between the supervisor and remediation agent.

The supervisor should produce structured findings but must not directly rewrite vulnerable code.

---

# 10. Finding and Event Schema

Propose a production-grade schema for security findings and blocked command events.

The schema should include:

* Event ID.
* Rule ID.
* Timestamp.
* Agent identity.
* Session ID.
* Parent process.
* Child process.
* Working directory.
* Original command.
* Normalized command.
* Interpreter.
* Arguments.
* Risk category.
* Severity.
* Confidence.
* Action taken.
* Block reason.
* Matched evidence.
* Rule version.
* Policy version.
* File path.
* Line number.
* Code snippet.
* CWE.
* OWASP category.
* MITRE ATT&CK technique where applicable.
* Related process tree.
* Related previous events.
* Recommended next action.
* Remediation-agent payload.
* Audit metadata.

The output should be suitable for another agent to consume without requiring direct access to raw internal supervisor state.

---

# 11. Policy Engine

Evaluate whether the project needs a formal policy engine.

Review support for policies such as:

* Allow.
* Deny.
* Warn.
* Require approval.
* Require multi-party approval.
* Log only.
* Restrict by workspace.
* Restrict by executable.
* Restrict by argument.
* Restrict by file path.
* Restrict by network destination.
* Restrict by user.
* Restrict by agent.
* Restrict by project.
* Restrict by environment.
* Restrict by risk level.
* Restrict by time.
* Restrict by execution context.

Recommend a policy model that is:

* Deterministic.
* Auditable.
* Versioned.
* Testable.
* Tamper-resistant.
* Easy to configure.
* Safe by default.

Explain whether the project should use declarative policy files or hardcoded rules.

---

# 12. Risk Classification

Evaluate the current severity model.

Determine whether the system should distinguish between:

* Informational.
* Suspicious.
* Dangerous.
* Destructive.
* Privilege-sensitive.
* Data-exfiltration risk.
* Persistence risk.
* Credential-access risk.
* Defense-evasion risk.
* Supply-chain risk.
* Repository-integrity risk.
* Production-impact risk.

Recommend a risk-scoring model.

The score should consider:

* Command intent.
* Scope of impact.
* Required privileges.
* Reversibility.
* Target environment.
* Data sensitivity.
* Network exposure.
* Agent autonomy level.
* Whether user approval exists.
* Whether the command is obfuscated.
* Whether the operation is part of a larger suspicious sequence.

---

# 13. Stateful and Sequence-Based Detection

Evaluate whether the project can detect dangerous behavior across multiple individually harmless actions.

Examples:

* Writing a script and executing it later.
* Downloading a payload and running it later.
* Reading credentials and then making an outbound request.
* Modifying permissions before deleting files.
* Disabling protection before executing malware.
* Creating a scheduled task after writing a script.
* Gathering system information before exfiltration.
* Splitting a destructive command across variables.
* Creating a shell alias that hides a dangerous command.
* Writing a command into a build script and triggering the build.

Recommend an event-correlation engine or stateful detection approach.

---

# 14. Audit Logging and Forensics

Review the quality of audit logging.

Determine whether logs are:

* Complete.
* Structured.
* Immutable.
* Append-only.
* Timestamped.
* Cryptographically verifiable.
* Exportable.
* Searchable.
* Suitable for incident investigation.
* Resistant to deletion or modification by the supervised agent.

Recommend logging formats and storage strategies.

Explain what evidence should be preserved when a command is blocked.

---

# 15. Performance and Developer Experience

Evaluate:

* Command interception latency.
* Scan latency.
* CPU usage.
* Memory usage.
* Startup time.
* Workspace monitoring overhead.
* Large repository performance.
* Rule-loading performance.
* False-positive rate.
* Noise level.
* Configuration complexity.
* Installation process.
* Cross-platform behavior.
* Compatibility with existing AI coding tools.

The supervisor must be strict without making development unusable.

Recommend performance budgets and acceptable latency targets.

---

# 16. False Positives and False Negatives

Analyze likely sources of:

* False positives.
* False negatives.
* Context loss.
* Parsing failures.
* Unsupported interpreters.
* Framework-specific blind spots.
* Obfuscation bypasses.
* Wrapper bypasses.
* Indirect command execution.
* Rule conflicts.

Recommend how the project should handle uncertain findings.

Do not recommend allowing the AI agent to freely override security policy.

---

# 17. Human Approval Model

Evaluate when a human should be involved.

Possible actions:

* Automatically allow.
* Automatically block.
* Ask for approval.
* Require elevated approval.
* Require a written justification.
* Require approval from multiple maintainers.
* Allow only in an isolated environment.

Recommend approval rules for:

* File deletion.
* Dependency installation.
* Network access.
* Database modification.
* Git history rewriting.
* Credential access.
* System configuration changes.
* Infrastructure changes.
* Production operations.
* Privileged commands.

---

# 18. Integration With AI Agents

Evaluate how the supervisor should integrate with:

* Claude Code.
* Codex CLI.
* Gemini CLI.
* Antigravity.
* Cursor.
* Windsurf.
* VS Code agents.
* Custom autonomous agents.
* MCP-based tools.
* CI/CD agents.
* Local shell-based agents.

Determine whether integration should occur through:

* Hooks.
* Tool wrappers.
* MCP proxies.
* Shell proxies.
* Process brokers.
* Local daemons.
* Agent SDK middleware.
* IDE extensions.
* CLI plugins.
* Operating-system services.

Recommend the most reliable integration architecture.

---

# 19. Security Boundaries

Clearly define the limits of the project.

Explain which guarantees are possible when:

* The supervisor runs in the same process as the agent.
* The supervisor runs as a separate process.
* The supervisor runs under the same operating-system account.
* The supervisor runs under a different account.
* The agent has administrator or root access.
* The agent can modify the supervisor's files.
* The agent can invoke the kernel directly.
* The agent can access container or virtualization controls.

State what must be true before the project can honestly claim:

> Even a fully privileged AI agent cannot execute blocked operations.

Avoid exaggerated claims.

---

# 20. Market and Technology Comparison

Compare the project against relevant categories and tools, such as:

* Traditional SAST tools.
* Semgrep.
* CodeQL.
* SonarQube.
* Snyk Code.
* Endpoint detection and response systems.
* Application allowlisting.
* Shell command filters.
* Operating-system sandboxing.
* Container isolation.
* Policy engines.
* AI agent governance platforms.
* AI execution-control middleware.
* Runtime application self-protection.
* MCP security gateways.

Do not claim direct competition when the tool categories are fundamentally different.

Identify the project's real differentiation.

---

# 21. Website and Documentation Review

Evaluate whether the website clearly communicates that the project is:

* A security supervisor.
* A command execution guard.
* A SAST monitoring layer.
* Independent from the supervised agent.
* Focused on detection, blocking, and escalation.
* Not a code-fixing tool.

Identify misleading or unclear wording.

Recommend concrete improvements to:

* Headline.
* Subtitle.
* Feature descriptions.
* Architecture diagram.
* Threat-model section.
* Security guarantees.
* Limitations.
* Installation guide.
* Demo scenarios.
* Comparison table.
* Call to action.

Propose three suitable slogans.

---

# 22. Open-Source Readiness

Evaluate:

* Repository structure.
* Rule organization.
* Test coverage.
* Security policy.
* Threat model.
* Contribution guide.
* License.
* Release process.
* Versioning.
* Rule update process.
* Signed releases.
* Supply-chain security.
* Dependency pinning.
* Issue templates.
* Vulnerability disclosure process.
* Governance.
* Documentation quality.

Determine what is missing before external developers should trust and install the plugin.

---

# 23. Testing Strategy

Recommend tests for:

* Dangerous-command detection.
* Command normalization.
* Obfuscation handling.
* Interpreter nesting.
* Process-tree monitoring.
* Rule precedence.
* Policy conflicts.
* Fail-closed behavior.
* Plugin tampering.
* Log integrity.
* SAST detection.
* Incremental scanning.
* Large repository performance.
* Windows behavior.
* Linux behavior.
* macOS behavior.
* Agent bypass attempts.

Include adversarial test cases.

The tests should attempt to bypass the supervisor rather than only prove normal behavior.

---

# 24. Strategic Roadmap

Create a realistic roadmap focused on the project's actual mission.

Suggested phases:

## Phase 1 — Reliable Command Guard

* Command interception.
* Canonicalization.
* Core dangerous-command rules.
* Fail-closed behavior.
* Structured logging.
* Basic policy engine.

## Phase 2 — Anti-Bypass Protection

* Nested interpreter detection.
* Child-process monitoring.
* Obfuscation handling.
* Tamper detection.
* Rule signing.
* Immutable configuration.

## Phase 3 — Continuous SAST Supervisor

* Incremental scanning.
* Diff-based scanning.
* Secret detection.
* Configuration scanning.
* Structured findings.
* Integration with remediation agents.

## Phase 4 — Stateful Agent Security

* Event correlation.
* Process-tree analysis.
* Multi-step attack detection.
* Behavioral risk scoring.
* Session-level policies.

## Phase 5 — Security Control Plane

* Multi-agent supervision.
* Centralized policies.
* Enterprise audit logs.
* Remote administration.
* Signed policies.
* Team approval workflows.
* Cross-environment enforcement.

For each phase, provide:

* Priority.
* Complexity.
* Expected impact.
* Security benefit.
* Dependencies.
* Exit criteria.

---

# 25. Brutally Honest Criticism

List the project's:

* Biggest technical weakness.
* Biggest architectural weakness.
* Biggest security claim risk.
* Biggest likely bypass.
* Biggest false-positive problem.
* Biggest false-negative problem.
* Biggest product-positioning mistake.
* Biggest documentation weakness.
* Biggest scalability concern.
* Biggest open-source adoption barrier.

Be direct and specific.

---

# 26. Final Evaluation

Provide scores from 0 to 10 for:

* Product clarity.
* Security architecture.
* Dangerous-command detection.
* Enforcement strength.
* Anti-bypass capability.
* SAST capability.
* Auditability.
* Extensibility.
* Developer experience.
* Open-source readiness.
* Production readiness.
* Enterprise readiness.

Then answer:

1. What is the strongest aspect of this project?
2. What is the most dangerous assumption in its current design?
3. Can it truly supervise an AI agent with full permissions?
4. Which parts are security enforcement and which parts are only advisory?
5. What must be implemented before claiming the system blocks dangerous commands comprehensively?
6. What should remain inside the supervisor?
7. What should be delegated to the remediation agent?
8. What would impress a senior AI security architect?
9. What would immediately concern them?
10. What is the clearest path toward a production-grade AI Security Supervisor?

Every conclusion must be tied to observable evidence from the repository or documentation.

When evidence is missing, explicitly state:

> Not demonstrated by the current implementation.

Do not invent capabilities that are not present.

Do not recommend adding automatic code fixing to the supervisor.

The final architecture must preserve strict separation between security enforcement and code remediation.
