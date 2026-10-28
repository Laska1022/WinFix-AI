#!/usr/bin/env bash
set -euo pipefail
cd /workspace/WinFix-AI
export DOTNET_CLI_HOME=/workspace/.dotnet-home
export DOTNET_CLI_TELEMETRY_OPTOUT=1
export DOTNET_GENERATE_ASPNET_CERTIFICATE=false
export NUGET_PACKAGES=/workspace/.nuget/packages
export DOTNET=/workspace/.dotnet/dotnet
if [[ ! -x "$DOTNET" ]]; then
  python3 scripts/install_sdk.py
fi
"$DOTNET" build src/WinFix.Agent/WinFix.Agent.csproj -c Release --nologo
python3 -m unittest discover -s tests -v
