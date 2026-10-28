# PROJECT: WinFix AI
## AI-Powered Remote Windows Diagnostics, Repair, and Administration

You are acting as a senior software architect, Windows internals engineer, cybersecurity engineer, and full-stack developer.

Your task is to design and implement a functional, secure, open-source remote Windows administration system called **WinFix AI**.

The system must allow an authorized technician to use **OpenAI Codex Cloud**, through an existing ChatGPT subscription, to diagnose, configure, troubleshoot, and repair remote Windows computers.

The long-term goal is to create an AI-powered Windows technical support system capable of performing both command-line and graphical troubleshooting.

This is a real software development project, not a theoretical architecture exercise.

You must implement working code, tests, documentation, and usable application builds.

---

# 1. PRIMARY OBJECTIVE

Enable workflows such as:

A technician opens Codex Cloud on a computer or smartphone and writes:

"Connect to Windows-PC-01. Investigate why a website displays DLG_FLAGS_INVALID_CA. Check Windows certificate stores, browser settings, CryptoPro CSP, and TLS configuration. Identify the root cause and fix it safely."

The system should:

1. Establish an authenticated, encrypted connection to the authorized remote computer.
2. Collect relevant diagnostic information.
3. Examine Windows configuration and logs.
4. Identify potential root causes.
5. Research unfamiliar technical problems using available documentation and internet access.
6. Develop a troubleshooting plan.
7. Execute approved diagnostic and repair operations.
8. Interact with the Windows GUI when necessary.
9. Verify whether the problem has been resolved.
10. Produce a comprehensive report.
11. Preserve troubleshooting progress so interrupted work can resume.

The technician should not need to operate RustDesk manually.

RustDesk may be supported as an optional fallback, but it must not be required.

---

# 2. HARD REQUIREMENTS

## 2.1 No paid AI API

The primary AI reasoning engine must be Codex Cloud, accessed through an existing ChatGPT subscription.

Do not require:

- OpenAI paid API access.
- Third-party paid LLM APIs.
- Usage-based AI inference billing.
- Paid AI orchestration platforms.

Do not assume ChatGPT subscription entitlements can be used as OpenAI API credits.

Do not attempt to obtain or reuse undocumented ChatGPT authentication tokens.

Do not automate browser interactions intended to bypass subscription limits.

Use Codex Cloud's available execution environment and supported tools.

If a proposed feature cannot operate without a separately billed API, explicitly identify the limitation and implement the best available subscription-only alternative.

The software must remain useful when AI is unavailable.

For example, the Windows Agent should still be able to collect diagnostics and execute explicitly authorized predefined maintenance operations.

## 2.2 Supported operating systems

Support:

- Windows 10 x64
- Windows 11 x64
- Windows Server 2016 and newer, where technically feasible

Support Windows Server Core for command-line diagnostics where possible.

Graphical features should require an actual interactive Windows desktop.

Do not prioritize Windows 7 or Windows 8.

## 2.3 Infrastructure

Prefer an architecture that requires no VPS.

Investigate native Tailscale connectivity in Codex Cloud.

If compatible with the user's environment, use Tailscale for secure communication between Codex Cloud and Windows Agent.

The implementation must also support an alternative architecture using a privately controlled VPS.

Do not depend on Russian cloud infrastructure.

If a VPS is needed, the deployment must support common Linux servers in countries such as Germany, Finland, the Netherlands, Canada, or the United States.

Prefer open-source components, minimal dependencies, and low operating costs.

Avoid exposing RDP, SMB, WinRM, or unrestricted PowerShell endpoints directly to the public internet.

---

# 3. ARCHITECTURE

Design the application using separate components.

## Component A: Windows Agent

A lightweight application installed on the computer being repaired.

Suggested technologies:

- C#
- .NET 10 or another currently supported .NET version
- Windows Service
- PowerShell integration
- Windows Management Instrumentation / CIM
- Windows Event Log APIs
- Windows certificate management APIs

Responsibilities:

- Gather system information.
- Inspect Windows configuration.
- Execute approved diagnostic operations.
- Perform authorized maintenance tasks.
- Collect execution results.
- Capture logs.
- Manage local permissions.
- Maintain connection state.
- Communicate with the graphical desktop component.
- Support resumable operations.

The Agent must support a Windows Service mode and, where feasible, a portable interactive mode.

The service must not require an interactive desktop session for command-line diagnostics.

Use the least privileges necessary.

Privileged operations must use a separate, explicitly authorized elevation mechanism.

## Component B: Windows Desktop Controller

A graphical automation component running in the interactive user session.

Possible technologies:

- Windows UI Automation
- UIAutomationClient
- Win32 APIs
- WPF
- Appropriate mature open-source automation libraries

Capabilities:

- Capture screenshots.
- Inspect accessible UI elements.
- Identify application windows.
- Open applications.
- Click buttons.
- Enter text.
- Navigate menus.
- Interact with standard Windows dialogs.
- Read error messages.
- Provide feedback about the results.

Prefer semantic UI Automation over coordinate-based clicking.

Use screenshots and coordinate-based interaction when semantic automation is insufficient.

The controller must not attempt to bypass Windows UAC, secure desktop restrictions, authentication dialogs, or other security boundaries.

When administrator authorization or user interaction is necessary, request it explicitly.

Clearly document the limitation that GUI automation may require an active and unlocked user session.

## Component C: Codex Cloud Integration

This component is critical.

Investigate the current capabilities of Codex Cloud before selecting the final implementation.

Preferred architecture:

Codex Cloud
→ Secure network connection
→ Windows Agent API
→ Windows computer

Implement a lightweight remote administration client inside the GitHub repository.

For example:

`tools/winfix_client.py`

It should expose structured operations that Codex Cloud can execute using its supported command environment.

Suggested operations:

- list_computers
- get_computer_status
- get_system_information
- inspect_windows_updates
- inspect_event_logs
- inspect_certificate_stores
- inspect_network_configuration
- inspect_installed_software
- inspect_services
- request_screenshot
- inspect_windows
- run_approved_diagnostic
- propose_repair
- request_approval
- execute_approved_repair
- verify_repair
- generate_report

Do not expose unrestricted arbitrary command execution by default.

Use a capability-based permission model with explicit authorization for privileged actions.

If supported, investigate implementing an MCP-compatible integration so Codex can discover and use WinFix tools naturally.

However, do not assume that MCP integration works identically in Codex Cloud, Codex CLI, and the desktop application.

Verify actual compatibility.

If MCP is unsuitable for Codex Cloud, use a reliable command-line integration.

The system must remain functional without MCP.

## Component D: Web Dashboard

Create a responsive web interface.

The dashboard should work on:

- Windows computers.
- Android smartphones.
- Tablets.
- Modern browsers.

Features:

- List of registered computers.
- Online/offline status.
- Windows version and basic system information.
- Current troubleshooting session.
- Diagnostic results.
- Operation history.
- Screenshots.
- Repair proposals.
- Approval requests.
- Progress indicators.
- Final troubleshooting reports.
- Connection management.

Include a visible emergency-stop control.

The dashboard must not itself require a paid AI API.

It may display results produced by Codex Cloud tasks.

Do not claim that the dashboard can initiate new Codex Cloud tasks automatically unless a documented, authorized integration supports it.

Support Russian and English user interfaces.

---

# 4. REMOTE CONNECTION OPTIONS

Implement a transport abstraction.

## Transport 1: Tailscale — preferred

Investigate current Codex Cloud support for Tailscale networking.

Use authenticated private network connectivity whenever possible.

Requirements:

- No public administrative ports.
- Encrypted transport.
- Restricted device access.
- Device identity verification.
- Revocable access.
- Short-lived credentials where supported.
- Independent application-level authorization.

Verify how Codex Cloud connects to HTTP, HTTPS, and TCP services through its configured networking proxy.

Do not assume ordinary direct TCP connectivity.

Prepare clear setup instructions for:

1. Creating the private network.
2. Adding a Windows computer.
3. Configuring Codex Cloud.
4. Restricting access.
5. Testing connectivity.
6. Revoking access.

Review the provider's current licensing and usage limits before recommending this deployment for commercial technical support.

## Transport 2: Self-hosted relay

Design an optional relay server.

Suggested technologies:

- Go, Python, or another suitable lightweight backend.
- HTTPS or mutually authenticated encrypted communication.
- WebSocket or polling-based communications where appropriate.
- Short-lived session tokens.
- Role-based authorization.

The relay should support multiple remote Windows computers.

Windows Agents should establish outbound connections so users do not need port forwarding.

The relay must not execute AI inference.

Its purpose is secure message delivery, authentication, session management, and operational coordination.

It should run on a low-cost Linux VPS.

Provide Docker deployment where appropriate.

Avoid mandatory commercial SaaS dependencies.

## Transport 3: Local development

Provide a local test transport for development and debugging.

This should allow developers to test the Agent on a Windows computer without deploying a VPS.

---

# 5. WINDOWS TROUBLESHOOTING CAPABILITIES

Implement diagnostic and repair modules.

Each module should provide:

- Read-only diagnostics.
- Structured findings.
- Proposed remediation.
- Risk classification.
- Verification methods.
- Optional rollback procedures.

## Module A: Windows system repair

Support:

- System File Checker (SFC).
- DISM health inspection and repair.
- Component store diagnostics.
- Windows Update diagnostics.
- Windows service inspection.
- System event logs.
- Disk health diagnostics.
- Storage integrity checks.
- System configuration analysis.
- Pending reboot detection.
- Relevant Windows recovery tools.

Do not automatically run destructive storage or recovery operations.

Use system-supported recovery and backup mechanisms when available.

## Module B: Windows certificates and CryptoPro

This module is especially important.

Support troubleshooting of:

- Windows trusted root certificate stores.
- Intermediate certificate stores.
- Certificate chains.
- Certificate expiration.
- TLS validation.
- Certificate revocation checking.
- Browser certificate errors.
- CryptoPro CSP installation and configuration.
- CryptoPro certificate integration.
- CryptoPro-related browser components.
- Certificate-based authentication.
- Legacy enterprise web applications.
- Digital signature configuration.

Diagnose errors including:

`DLG_FLAGS_INVALID_CA`

Possible troubleshooting areas include:

- Incorrect system date or time.
- Missing trusted root certificates.
- Missing intermediate certificates.
- Invalid certificate chains.
- Proxy configuration.
- HTTPS inspection.
- Incorrect certificate placement.
- Browser compatibility.
- CryptoPro installation problems.
- Outdated or incompatible components.

Research the actual cause before applying changes.

Never resolve certificate errors by simply disabling certificate verification.

Do not disable HSTS.

Do not install unverified root certificates.

Require explicit confirmation before changing trusted certificate stores.

Never export private keys or store certificate passwords in logs.

Support legitimate certificate import workflows only with proper authorization.

Do not redistribute proprietary CryptoPro binaries.

## Module C: Application troubleshooting

Support:

- Installed application inventory.
- Application version detection.
- Software compatibility inspection.
- Repair of installed applications.
- Approved software installation.
- Approved software removal.
- Dependency diagnostics.
- .NET runtime troubleshooting.
- Application event log analysis.
- Relevant registry configuration inspection.

Prefer vendor-supported installers and repair procedures.

## Module D: Network troubleshooting

Support:

- DNS diagnostics.
- Network adapter inspection.
- IP configuration.
- Proxy detection.
- Route inspection.
- VPN configuration diagnostics.
- Windows Firewall inspection.
- Connectivity testing.
- TLS handshake diagnostics.
- DNS cache analysis.

Changes that might disconnect the remote computer require special safeguards.

Implement connection-preserving workflows and rollback timers where feasible.

## Module E: GUI troubleshooting

Allow Codex to inspect the Windows desktop using authorized screenshot and UI automation operations.

Example:

The AI detects a certificate warning in a legacy browser.

It should be able to:

1. Read the displayed error.
2. Inspect the relevant dialog.
3. Determine the appropriate diagnostic action.
4. Open Windows certificate management tools.
5. Inspect certificate details.
6. Propose a correction.
7. Obtain required approval.
8. Perform the correction.
9. Reopen the application.
10. Verify the result.

---

# 6. AUTONOMOUS PROBLEM INVESTIGATION

Implement an AI-assisted troubleshooting workflow.

This must be compatible with the fact that Codex Cloud tasks are finite and require supported user initiation.

The investigation process should include:

### Step 1: Collect evidence

Gather relevant information without making changes.

### Step 2: Identify likely causes

Produce hypotheses based on observable evidence.

### Step 3: Research

Use current vendor documentation, Microsoft documentation, error-code references, and trustworthy technical sources when internet access is available.

### Step 4: Develop a repair plan

Describe:

- Suspected cause.
- Supporting evidence.
- Proposed actions.
- Risk level.
- Required privileges.
- Expected outcome.
- Verification method.
- Rollback plan.

### Step 5: Execute safely

Automatically execute only operations permitted by the selected authorization policy.

Request approval for higher-risk actions.

### Step 6: Verify

Determine whether the original problem was actually resolved.

### Step 7: Learn from the case

Save a structured troubleshooting record.

The knowledge base should include:

- Problem category.
- Symptoms.
- Environment.
- Confirmed root cause.
- Successful repair procedure.
- Verification results.
- Relevant documentation.
- Anonymized diagnostic information.

Avoid storing customer passwords, private keys, personal files, or unnecessary sensitive data.

Use a searchable local knowledge base.

Do not require a paid embedding or AI API.

---

# 7. SECURITY REQUIREMENTS

This is a remote administration application and must be designed accordingly.

Security is mandatory.

Implement:

1. Explicit installation and authorization by the computer owner.
2. Visible indication when remote administration is active.
3. Strong authentication.
4. Encrypted communications.
5. Device registration and revocation.
6. Separate technician and computer identities.
7. Least-privilege execution.
8. Privileged-operation approval.
9. Comprehensive audit logs.
10. Session expiration.
11. Emergency disconnect.
12. Protection against command injection.
13. Replay protection.
14. Secure local credential storage.
15. No hardcoded passwords or tokens.
16. Optional unattended access only after explicit prior authorization.

Maintain three operational modes.

**Mode 1: Read Only**

Collect information and perform diagnostics.

**Mode 2: Assisted Repair**

Perform approved low-risk operations. Request authorization for consequential changes.

**Mode 3: Advanced Administration**

Allow broader maintenance capabilities with explicit administrator authorization, action-specific controls, and detailed auditing.

Classify operations according to risk.

Deleting files, changing trusted certificate stores, editing sensitive registry locations, disabling security controls, modifying firewall rules, and restarting remote systems must require appropriate authorization.

Do not create stealth functionality, hidden persistence, credential extraction, or security-control bypass mechanisms.

---

# 8. RECOVERY AND ROLLBACK

The system should minimize the risk of making a computer unusable.

Before significant configuration changes:

- Record the current state.
- Create relevant backups.
- Export affected registry keys when appropriate.
- Use Windows restore functionality when supported.
- Record rollback instructions.
- Check available disk space.
- Identify operations that could interrupt connectivity.

For network configuration changes, implement automatic rollback when connectivity is lost, where technically feasible.

Make high-risk operations interruptible whenever supported.

Do not promise rollback for changes that cannot reliably be reversed.

For Windows Server, take into account that ordinary System Restore functionality may not be available.

---

# 9. MULTIPLE CODEX ACCOUNTS AND GITHUB CONTINUITY

The developer has two independently subscribed ChatGPT accounts.

Both accounts can access the same GitHub repository.

The software development project must be designed so either authorized account can continue work from the repository.

Important:

Codex Cloud conversations, isolated execution environments, and subscription limits cannot be assumed to transfer between accounts.

Do not implement unauthorized account switching or mechanisms intended to circumvent usage restrictions.

Instead, implement a robust project handoff system.

## Required GitHub files

Create and maintain:

`AGENTS.md`

Project-wide development instructions for Codex.

`docs/ARCHITECTURE.md`

Current system architecture.

`docs/PROJECT_STATUS.md`

Current implementation status.

`docs/HANDOFF.md`

Instructions for resuming development in a new Codex task or account.

`docs/DECISIONS.md`

Important architectural decisions and their rationale.

`docs/TASK_QUEUE.md`

Prioritized development tasks.

`docs/KNOWN_ISSUES.md`

Unresolved bugs and limitations.

`docs/TEST_REPORT.md`

Tests performed and their outcomes.

`docs/SETUP.md`

Deployment and configuration instructions.

`docs/SECURITY.md`

Security model and threat analysis.

## Continuation requirements

At the completion of every meaningful development stage:

1. Commit completed changes.
2. Run available tests.
3. Update project status.
4. Update the task queue.
5. Document unresolved problems.
6. Record the exact next development step.
7. Identify the latest commit and active branch.
8. Provide instructions for continuing the work.
9. Push a branch or create a pull request when repository permissions allow.

Never assume that uncommitted Codex Cloud files are accessible from another account.

Never store API keys, session cookies, private credentials, or authentication tokens in the repository.

Use a workflow that prevents two Codex tasks from accidentally overwriting each other's changes.

Use branches and pull requests where appropriate.

## HANDOFF.md format

Include:

- Project name.
- Current development phase.
- Latest verified commit.
- Active branch.
- Completed features.
- Incomplete features.
- Current blockers.
- Test results.
- Required environment configuration.
- Next recommended task.
- Exact continuation instructions.

The handoff must be sufficiently detailed that a fresh Codex Cloud conversation can continue without relying on previous chat history.

---

# 10. APPLICATION PACKAGING

Produce usable Windows application distributions.

Preferred outputs:

- Portable executable or application package.
- Windows installer.
- Windows Service installation instructions.
- Uninstallation procedure.
- Configuration wizard.
- Source code.
- Troubleshooting documentation.

Provide a simple installation experience.

A nontechnical user should be able to:

1. Download the Windows Agent.
2. Launch the installer.
3. Approve installation.
4. Register the computer securely.
5. Grant the requested access.
6. See when the technician is connected.

Avoid requiring the end user to manually edit configuration files.

If unsigned applications trigger Windows SmartScreen warnings, document this limitation rather than bypassing security protections.

---

# 11. DEVELOPMENT STRATEGY

Do not attempt to implement the entire system at once.

Use incremental development with working milestones.

## Phase 0: Feasibility validation

Before building a large application, investigate and test:

- Current Codex Cloud network capabilities.
- Native Tailscale support.
- HTTPS access to private services.
- Authentication.
- Request and response handling.
- Windows compatibility.
- Available development and testing environments.
- Codex Cloud limitations.
- MCP compatibility, if applicable.

Build a minimal proof of concept.

The proof of concept must demonstrate that a Codex Cloud task can communicate with an authorized Windows test service.

A successful request must return structured Windows diagnostic information.

Do not claim success without a real integration test.

If the test cannot be performed because a Windows computer or external credentials are unavailable, create the runnable test and clearly identify the missing requirement.

## Phase 1: Windows Agent MVP

Implement:

- Basic Windows Agent.
- Secure connection handling.
- Computer identity.
- System information retrieval.
- Windows event log inspection.
- Service inspection.
- Read-only PowerShell diagnostics.
- Structured JSON results.
- Audit logging.

The MVP must work before proceeding to more advanced modules.

## Phase 2: Remote repair

Implement:

- Controlled execution of approved maintenance tasks.
- Approval workflow.
- Command execution monitoring.
- Error reporting.
- Rollback support.
- Remote session history.

## Phase 3: Graphical control

Implement:

- Desktop companion application.
- Window inspection.
- Screenshot capture.
- UI Automation.
- Mouse and keyboard interaction.
- GUI session lifecycle management.

## Phase 4: AI troubleshooting workflows

Create Codex-compatible workflows that:

- Gather evidence.
- Analyze diagnostic findings.
- Investigate unfamiliar problems.
- Propose repairs.
- Execute approved operations.
- Verify outcomes.
- Produce reports.

## Phase 5: Web dashboard

Implement:

- Computer management.
- Session monitoring.
- Diagnostic history.
- Screenshot viewing.
- Approval controls.
- Technician authentication.

## Phase 6: Production hardening

Implement:

- Security testing.
- Error recovery.
- Connection resilience.
- Installation improvements.
- Integration tests.
- Windows Server compatibility checks.
- Documentation.
- Release packaging.

---

# 12. TESTING

Use unit tests and integration tests.

Create mock Windows Agent implementations for development environments that do not run Windows.

Use Windows-based testing for platform-dependent functionality.

Do not claim that Windows GUI integration works merely because code compiles.

Provide reproducible tests for:

- Connection establishment.
- Authentication.
- Authorization failures.
- Diagnostic collection.
- Interrupted sessions.
- Expired credentials.
- Lost network connectivity.
- Command cancellation.
- Repair verification.
- GUI automation.
- Rollback behavior.
- Agent installation and uninstallation.

For the initial real-world test scenario, use a Windows certificate validation issue resembling:

`DLG_FLAGS_INVALID_CA`

The initial test should be diagnostic and must not install unverified certificates.

---

# 13. GITHUB AND DEVELOPMENT MANAGEMENT

Use GitHub as the authoritative source of the project.

Prefer a private repository during development.

Follow normal Git best practices.

Do not use force pushes that could overwrite another task's work.

Keep commits focused.

Use clear commit messages.

Maintain automated tests where feasible.

GitHub Actions may be used within available free quotas, but the project must not require paid CI services.

If Windows builds cannot be tested in the Codex Cloud environment, provide a reproducible Windows build workflow.

Avoid leaving the repository in an unusable state.

---

# 14. USER EXPERIENCE

Optimize for a technician who may be using Codex Cloud from an Android smartphone.

A typical workflow should look like:

Technician:

"Connect to Office-PC-03 and diagnose why Windows Update is failing."

Codex:

- Establishes the authorized connection.
- Collects relevant information.
- Investigates the failure.
- Reports findings.
- Proposes a repair.
- Executes permitted operations.
- Verifies the result.

The technician should see clear summaries instead of enormous raw logs.

Include useful operation progress messages.

The UI should show:

- Connected computer.
- Current operation.
- Progress.
- Risk level.
- Required approval.
- Operation result.

Provide detailed technical logs separately.

---

# 15. IMPORTANT TECHNICAL CONSTRAINTS

Do not assume Codex Cloud can run indefinitely.

Do not assume Codex Cloud can automatically start new tasks without a supported mechanism.

Do not assume the ChatGPT subscription provides access to the OpenAI API.

Do not assume two ChatGPT accounts share the same Codex task or conversation history.

Do not assume a cloud Linux environment can execute or validate Windows GUI automation.

Do not assume remote GUI control is possible while the Windows session is locked.

Do not require a public VPS if a supported private network solution works.

Do not invent capabilities that have not been verified.

For every significant limitation, identify the technical reason and propose a practical alternative.

---

# 16. DEVELOPMENT PRIORITIES

Prioritize features in this order:

1. Working secure remote connection.
2. Basic Windows diagnostics.
3. Reliable authorized command execution.
4. Verification and error reporting.
5. Safe Windows repair tools.
6. Certificate and CryptoPro diagnostics.
7. Graphical Windows control.
8. Autonomous troubleshooting workflows.
9. Web dashboard.
10. Advanced administration and optimization.

A functional command-line MVP is more valuable than a beautiful dashboard that cannot control a Windows computer.

---

# 17. WHAT YOU MUST DO FIRST

Start working immediately.

First:

1. Review current official Codex Cloud documentation.
2. Validate whether Tailscale can support the proposed architecture.
3. Compare the Tailscale and VPS relay approaches.
4. Select the simplest technically viable implementation.
5. Create the repository structure.
6. Create AGENTS.md.
7. Create the initial architecture documentation.
8. Implement the Phase 0 proof of concept.
9. Add automated tests.
10. Document how to test the connection with a real Windows machine.

Then proceed to the Windows Agent MVP.

Do not stop after producing only a project proposal.

Write actual working code.

If you cannot complete a development phase during the current task, commit all completed work and update HANDOFF.md with precise continuation instructions.

At the end of the task, report:

- What was implemented.
- What was tested.
- What remains unfinished.
- What requires real Windows hardware.
- Whether any paid services are required.
- How to run the current version.
- The exact next development task.

The final goal is a secure, extensible, practical AI-assisted Windows administration platform that allows authorized remote Windows troubleshooting through Codex Cloud without requiring paid LLM API access.

**Begin with Phase 0 and implementation of the first working prototype.**