#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
env_file="${repo_root}/.env"

whisper_bin="${WHISPER_CPP_BIN:-whisper-cli}"
whisper_model="${WHISPER_CPP_MODEL:-}"
piper_bin="${PIPER_TTS_BIN:-piper}"
piper_model="${PIPER_TTS_MODEL:-}"
piper_config="${PIPER_TTS_CONFIG:-}"

echo "Local voice check"
echo

if command -v ffmpeg >/dev/null 2>&1; then
  echo "ffmpeg: found"
else
  echo "ffmpeg: missing"
fi

if command -v espeak-ng >/dev/null 2>&1; then
  echo "espeak-ng: found"
else
  echo "espeak-ng: missing"
fi

if command -v "$whisper_bin" >/dev/null 2>&1 && [[ -n "$whisper_model" && -f "$whisper_model" ]]; then
  echo "whisper.cpp: ready"
else
  echo "whisper.cpp: not ready"
  echo "  set WHISPER_CPP_BIN to the whisper.cpp CLI binary"
  echo "  set WHISPER_CPP_MODEL to a local Whisper model file"
fi

if command -v "$piper_bin" >/dev/null 2>&1 && [[ -n "$piper_model" && -f "$piper_model" ]]; then
  echo "piper: ready"
else
  echo "piper: not ready"
  echo "  set PIPER_TTS_BIN to the Piper binary"
  echo "  set PIPER_TTS_MODEL to a local Piper voice .onnx file"
  echo "  set PIPER_TTS_CONFIG if your voice ships with a separate JSON config"
fi

if [[ -f "$env_file" ]]; then
  echo
  echo ".env exists at: $env_file"
else
  echo
  echo ".env not found"
fi
