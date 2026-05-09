# activeloop.py

import asyncio
import json
from cortex.config import active_loop_config

COMMAND_PHRASES = {
    "diagnostic mode": "tool",
    "news fetch": "tool",
    "forecast fetch": "tool",
    "wikipedia fetch": "tool",
}


class ActiveLoop:
    def __init__(self, hotswap, globals_dict):
        self.hotswap = hotswap
        self.globals = globals_dict

    async def run(self):
        while True:
            # 1. Hot‑swap first
            self.hotswap.process(self.globals)

            # 2. Run the loop body (speech, vision, sensors, etc.)
            await self.loop_body()

            # 3. Tick pacing
            await asyncio.sleep(active_loop_config["tick_rate"])


    async def loop_body(self):
        g = self.globals
        audio_input = g["audio_input"]
        voice_recognition = g["voice_recognition"]
        preprocessor = g["preprocessor"]
        unified_server = g["unified_server"]
        event_builder = g["event_builder"]
        perception = g["perception"]
        internal_state = g["internal_state"]
        cortex = g["cortex"]
        indicators = g["indicators"]
        parse_server_intent = g["parse_server_intent"]
        DEBUG_REASONING = g["DEBUG_REASONING"]

        # Check for Module Reload Flag ------------------------------------------------------
        self.hotswap.process(g)

        # AUDIO INPUT ------------------------------------------------------
        print("[Hal] Listening.")
        pcm_audio = await audio_input.capture_audio()
        if pcm_audio is None or len(pcm_audio) == 0:
            return # No audio captured, skip this loop iteration

        # --- AUDIO SAFETY CAP --------------------------------------------
        MAX_AUDIO_BYTES = 5_000_000  # ~5 MB cap
        truncated = False

        # pcm_audio is int16 → 2 bytes per sample
        if pcm_audio.nbytes > MAX_AUDIO_BYTES:
            print(f"[Audio] Oversized capture ({pcm_audio.nbytes} bytes). Truncating.")
            max_samples = MAX_AUDIO_BYTES // 2
            pcm_audio = pcm_audio[:max_samples]
            truncated = True

        print(f"[Audio] Captured {pcm_audio.nbytes} bytes")

        indicators.set_mode("busy")

        recognized_speaker = voice_recognition.recognize_speaker(pcm_audio)

        # Hal will attempt to determine if the detected speech requires a response
        # call to stubbed voice analysis method will default boolean TRUE during testing
        if audio_input.respond_to_voice_input(pcm_audio, recognized_speaker):
            print("[Voice Analysis] Positive response. Proceeding with cognition loop.")

        if recognized_speaker != "Unknown":
            print(f"[Speaker Recognition] Identified speaker: {recognized_speaker}")
        else:
            print("[Speaker Recognition] Speaker is Unknown.")

        wav_bytes = preprocessor.pcm_to_16k_wav(pcm_audio)
        transcription = await unified_server.transcribe_audio(wav_bytes)
        # print(f"[Transcription RAW] {transcription}")

        spoken_text = transcription.get("text", "")
        if not spoken_text:
            indicators.set_mode("idle")
            return

        # COMMAND PHRASE CHECK
        lower = spoken_text.lower().strip()
        inference_type = "chat"
        for phrase in COMMAND_PHRASES:
            if lower.startswith(phrase):
                inference_type = COMMAND_PHRASES[phrase]
                break

        perception.ingest_audio_event(
            spoken_text,
            recognized_speaker,
            transcription,
            truncated
        )

        # SEND TO UNIFIED SERVER (COGNITION) -------------------------------
        event = event_builder.build_event(
            self,
            perception=perception.snapshot(),
            last_intent=internal_state.last_intent
        )

        # DEBUG OUTPUT ------------------------------------------------------
        print("[Cognition] Sending event to server…")
        print("----- BEGIN EVENT -----")
        print(event)
        print("------ END EVENT ------")
        # END DEBUG OUTPUT --------------------------------------------------

        if DEBUG_REASONING:
            # Allow chain-of-thought (no /nothink)
            prompt_str = json.dumps(event, indent=2)
        else:
            # Standard operation: suppress CoT
            prompt_str = "/nothink\n" + json.dumps(event, indent=2)

        payload = { "prompt": prompt_str }

        if inference_type == "tool":
            endpoint = "/api/tool"
        elif inference_type == "autonomous":
            endpoint = "/api/autonomous"
        else:
            endpoint = "/api/chat"

        server_json = await unified_server.send_perception(payload, endpoint)
        print(f"\n[Cognition] Returned from the server, before processing:: \n{server_json}\n\n")
        try:
            server_intent = parse_server_intent(server_json)
            print(f"[Cognition] Server intent: {server_intent}")
        except Exception as e:
            print(f"[Server Error] {e}")
            server_intent = {"intent": "experience entropy"}

        # RESET PERCEPTION -------------------------------------------------
        perception.reset()

        # DECISION LAYER ---------------------------------------------------
        cortex.tick(server_intent)
        print(f"[Decision] Executed plan for intent '{server_intent.get('intent')}'")
        # LOOP --------------------------------------------------------------
        indicators.set_mode("idle")
        await asyncio.sleep(active_loop_config["tick_rate"])

