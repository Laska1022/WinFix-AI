# WinFix AI

An open-source, subscription-independent Windows diagnostics prototype for use
from Codex Cloud or a terminal. No LLM API or AI service is called by this code.

**[Download the Windows setup EXE](https://github.com/Laska1022/WinFix-AI/raw/refs/tags/v0.1.2-preview/downloads/v0.1.2-preview/WinFixAI-Setup-0.1.2-preview.exe)**
— unsigned preview, Windows x64. [Checksums and build details](downloads/v0.1.2-preview/README.md).

Run the installer using your normal account, then open **WinFix AI** from the
desktop or Start menu. Choose English or Russian, then **1** for basic local
diagnostics. **2** creates an explicitly authorized local test session; Enter stops
it. Python and a separate .NET installation are not needed on the Windows PC.
Remote connectivity still needs technician configuration. Windows installation and
execution have not yet been validated; see [quick start](packaging/QUICK-START.txt).

**Phase 0: implemented and tested locally; real Windows/private-network acceptance
is pending. This is not a production remote administration agent.**

Included: .NET 10 read-only HTTPS agent, Python standard-library client,
owner-created one-hour credentials, explicit device identity, durable replay
protection, audit journal, local emergency stop, tests, and unsigned Windows
portable build and per-user installer. No command execution or repairs are exposed.

Build and test from this directory with .NET SDK 10.0.403 and Python 3.12+:

```sh
dotnet build src/WinFix.Agent/WinFix.Agent.csproj -c Release
python -m unittest discover -s tests -v
```

The tests launch temporary HTTPS instances and clean them up. Linux results are
explicitly synthetic; Windows runs use the Windows information collector.

Start with [setup and Windows acceptance](docs/SETUP.md),
[security boundaries](docs/SECURITY.md), and [handoff](docs/HANDOFF.md).
See [task queue](docs/TASK_QUEUE.md) for the next development task and
[specification](docs/SPECIFICATION.md) for the full phased product requirements.
