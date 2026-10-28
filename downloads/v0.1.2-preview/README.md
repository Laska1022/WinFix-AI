# WinFix AI 0.1.2 Preview — Windows x64

[Download setup EXE](https://github.com/Laska1022/WinFix-AI/raw/refs/tags/v0.1.2-preview/downloads/v0.1.2-preview/WinFixAI-Setup-0.1.2-preview.exe)

Run setup as your normal user, then open WinFix AI from Start or the desktop.
Choose English/Russian, then 1 for basic local diagnostics. Option 2 creates a
local HTTPS test session after consent; press Enter to stop. Remote access still
needs technician setup. No separate Python, .NET install, or paid AI API required.

The installer provides an uninstaller and preserves private reports/session data.
Read [quick start](../../packaging/QUICK-START.txt) and [setup](../../docs/SETUP.md).

Unsigned preview; Windows installation, shortcuts and runtime execution have not
been tested on Windows. Linux tests cover the protocol and console flow with mock
diagnostics. No service, automatic startup, repair or GUI control is included.

SHA256SUMS.txt verifies the installer. build-manifest.json records the source commit
and hashes of both installer and bundled app. windowsExecutionTested remains false.
This directory is distributed through Git because the current environment's GitHub
Release API is blocked. It is not a GitHub Release. Future builds should use Release
assets when that supported access is available, avoiding repeated binaries in Git.

This update fixes shutdown with unwritable state, corrupt audit recovery, malformed
HTTP handling and premature readiness reporting. 37 Linux tests pass. See
[review findings](../../docs/REVIEW.md). Previous 0.1.1 downloads are preserved.
