from __future__ import annotations

import asyncio
import base64
import binascii
import os
import re
import shutil
import subprocess
import tempfile
from functools import lru_cache
from pathlib import Path

from app.config import Settings, get_settings
from app.services.llm.base import LLMProviderError

DATA_URL_RE = re.compile(r"^data:(?P<mime>[^;]+);base64,(?P<data>.+)$", re.IGNORECASE | re.DOTALL)


def _decode_data_url(payload: str) -> bytes:
    text = payload.strip()
    if text.startswith("data:"):
        match = DATA_URL_RE.match(text)
        if not match:
            raise LLMProviderError("Invalid audio payload.")
        text = match.group("data")
    try:
        return base64.b64decode(text, validate=False)
    except (binascii.Error, ValueError) as exc:
        raise LLMProviderError("Invalid audio payload.") from exc


class SpeechService:
    def __init__(self, settings: Settings):
        self.settings = settings

    @staticmethod
    def _whisper_ready(settings: Settings) -> bool:
        model = Path(settings.whisper_cpp_model).expanduser()
        return bool(shutil.which(settings.whisper_cpp_bin) and settings.whisper_cpp_model and model.exists())

    @staticmethod
    def _piper_ready(settings: Settings) -> bool:
        model = Path(settings.piper_tts_model).expanduser()
        config = Path(settings.piper_tts_config).expanduser() if settings.piper_tts_config else None
        if not shutil.which(settings.piper_tts_bin):
            return False
        if not settings.piper_tts_model or not model.exists():
            return False
        if config is not None and not config.exists():
            return False
        return True

    @staticmethod
    def supports_text_to_speech(settings: Settings | None = None) -> bool:
        current = settings or get_settings()
        return SpeechService._piper_ready(current) or shutil.which("espeak-ng") is not None

    @staticmethod
    def supports_transcription(settings: Settings | None = None) -> bool:
        current = settings or get_settings()
        return SpeechService._whisper_ready(current)

    @staticmethod
    def voice_input_engine(settings: Settings | None = None) -> str:
        current = settings or get_settings()
        return "whisper.cpp" if SpeechService._whisper_ready(current) else "unavailable"

    @staticmethod
    def voice_output_engine(settings: Settings | None = None) -> str:
        current = settings or get_settings()
        if SpeechService._piper_ready(current):
            return "piper"
        if shutil.which("espeak-ng") is not None:
            return "espeak-ng"
        return "unavailable"

    async def transcribe(self, audio_payload: str) -> str:
        if not self.supports_transcription(self.settings):
            raise LLMProviderError(
                "Local voice input requires whisper.cpp. Set WHISPER_CPP_BIN and WHISPER_CPP_MODEL to local files."
            )

        audio_bytes = _decode_data_url(audio_payload)
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            raw_audio = temp_path / "input.webm"
            wav_audio = temp_path / "input.wav"
            output_prefix = temp_path / "transcript"
            raw_audio.write_bytes(audio_bytes)

            try:
                await asyncio.to_thread(
                    subprocess.run,
                    [
                        "ffmpeg",
                        "-y",
                        "-i",
                        str(raw_audio),
                        "-ar",
                        "16000",
                        "-ac",
                        "1",
                        "-c:a",
                        "pcm_s16le",
                        str(wav_audio),
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
            except FileNotFoundError as exc:
                raise LLMProviderError("Local audio conversion requires ffmpeg.") from exc
            except subprocess.CalledProcessError as exc:
                raise LLMProviderError("Audio conversion failed.") from exc

            command = [
                shutil.which(self.settings.whisper_cpp_bin) or self.settings.whisper_cpp_bin,
                "-m",
                str(Path(self.settings.whisper_cpp_model).expanduser()),
                "-f",
                str(wav_audio),
                "-t",
                str(self.settings.whisper_cpp_threads),
                "-np",
                "-nt",
                "-of",
                str(output_prefix),
            ]
            language = self.settings.whisper_cpp_language.strip()
            if language and language.lower() != "auto":
                command.extend(["-l", language])

            try:
                await asyncio.to_thread(
                    subprocess.run,
                    command,
                    check=True,
                    capture_output=True,
                    text=True,
                )
            except FileNotFoundError as exc:
                raise LLMProviderError("Local voice input requires the whisper.cpp CLI binary.") from exc
            except subprocess.CalledProcessError as exc:
                raise LLMProviderError("Local voice transcription failed.") from exc

            transcript_path = output_prefix.with_suffix(".txt")
            if not transcript_path.exists():
                raise LLMProviderError("Speech transcription returned no text.")
            transcript = transcript_path.read_text(encoding="utf-8").strip()

        if not transcript:
            raise LLMProviderError("Speech transcription returned no text.")
        return re.sub(r"\s+", " ", transcript)

    async def synthesize(self, text: str) -> bytes:
        content = text.strip()
        if not content:
            raise LLMProviderError("Speech text cannot be empty.")

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as handle:
            output_path = handle.name

        try:
            if self._piper_ready(self.settings):
                command = [
                    shutil.which(self.settings.piper_tts_bin) or self.settings.piper_tts_bin,
                    "--model",
                    str(Path(self.settings.piper_tts_model).expanduser()),
                    "--output_file",
                    output_path,
                ]
                config = self.settings.piper_tts_config.strip()
                if config:
                    command.extend(["--config", str(Path(config).expanduser())])

                try:
                    completed = await asyncio.to_thread(
                        subprocess.run,
                        command,
                        input=content,
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                except FileNotFoundError as exc:
                    raise LLMProviderError("Local text-to-speech requires the Piper binary.") from exc
                except subprocess.CalledProcessError as exc:
                    raise LLMProviderError("Local Piper text-to-speech failed.") from exc
            elif shutil.which("espeak-ng") is not None:
                try:
                    completed = await asyncio.to_thread(
                        subprocess.run,
                        ["espeak-ng", "-w", output_path, content],
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                except FileNotFoundError as exc:
                    raise LLMProviderError("Local text-to-speech requires the espeak-ng command.") from exc
                if completed.returncode != 0:
                    raise LLMProviderError("Local text-to-speech failed.")
            else:
                raise LLMProviderError("Local text-to-speech requires Piper or espeak-ng.")

            with open(output_path, "rb") as handle:
                return handle.read()
        finally:
            try:
                os.unlink(output_path)
            except OSError:
                pass


@lru_cache
def get_speech_service() -> SpeechService:
    return SpeechService(get_settings())
