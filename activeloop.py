# activeloop.py

import asyncio

from cortex.config import active_loop_config
from helpers.llm_message_builder import LLMMessageBuilder

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

    async def _process_audio(self, pcm_audio):
        g = self.globals
        audio_input = g["audio_input"]
        voice_recognition = g["voice_recognition"]
        preprocessor = g["preprocessor"]
        unified_server = g["unified_server"]
        indicators = g["indicators"]

        # --- SAFETY CAP ---
        MAX_AUDIO_BYTES = 5_000_000
        truncated = False
        if pcm_audio.nbytes > MAX_AUDIO_BYTES:
            max_samples = MAX_AUDIO_BYTES // 2
            pcm_audio = pcm_audio[:max_samples]
            truncated = True

        recognized_speaker = voice_recognition.recognize_speaker(pcm_audio)

        if not audio_input.respond_to_voice_input(pcm_audio, recognized_speaker):
            indicators.set_mode("idle")
            return None

        wav_bytes = preprocessor.pcm_to_16k_wav(pcm_audio)
        transcription = await unified_server.transcribe_audio(wav_bytes)

        spoken_text = transcription.get("text", "")
        if not spoken_text:
            indicators.set_mode("idle")
            return None

        return spoken_text, recognized_speaker, transcription, truncated

    def _update_perception(self, spoken_text, recognized_speaker, transcription, truncated):
        perception = self.globals["perception"]

        perception.ingest_audio_event(
            spoken_text,
            recognized_speaker,
            transcription,
            truncated
        )

        imu = self.globals["imu"]
        perception.sensor_status["imu"] = imu.read()

    def _update_perception_no_audio(self):
        imu = self.globals["imu"]
        self.globals["perception"].sensor_status["imu"] = imu.read()

    async def _send_to_server(self, event, inference_type):
        g = self.globals
        unified_server = g["unified_server"]

        payload = LLMMessageBuilder.build_messages(event, debug_reasoning=False)

        if inference_type == "tool":
            endpoint = "/api/tool"
        elif inference_type == "autonomous":
            endpoint = "/api/autonomous"
        else:
            endpoint = "/api/chat"

        return await unified_server.send_perception(payload, endpoint)

    async def _run_reflexes(self):
        reflex_engine = self.globals["reflex_engine"]

        result = await reflex_engine.check_and_execute(
            perception=self.globals["perception"].snapshot(),
            world_state=self.globals["world_state"],
            internal_state=self.globals["internal_state"],
            hardware_state=self.globals["hardware_state"],
            executor=self.globals["action_executor"],
        )

        if not result:
            return False

        return await self._handle_reflex(result)


    async def _handle_reflex(self, reflex_result):
        action = reflex_result.get("action")
        if not action:
            return

        motor = self.globals["motor_controller"]
        await motor.execute(action)
        return True


    async def _run_autonomous_behaviors(self):
        pass # stub for now to allow for autonomous behaviors in the future without blocking reflexes or speech processing

    async def loop_body(self):
        print("[ActiveLoop] Hal Listening.")
        g = self.globals
        audio_input = g["audio_input"]
        indicators = g["indicators"]
        working_memory = g["working_memory"]
        event_builder = g["event_builder"]
        cortex = g["cortex"]

        self.hotswap.process(g)

        pcm_audio = await audio_input.capture_audio()
        if pcm_audio is None or pcm_audio.size == 0:

            self._update_perception_no_audio()
            await self._run_reflexes()
            await self._run_autonomous_behaviors()  # stub for now
            return

        # --- Valid speech, set as Busy ---
        indicators.set_mode("busy")

        processed = await self._process_audio(pcm_audio)
        if processed is None:
            return

        spoken_text, recognized_speaker, transcription, truncated = processed

        # --- Command phrase detection ---
        lower = spoken_text.lower().strip()
        inference_type = "chat"
        for phrase in COMMAND_PHRASES:
            if lower.startswith(phrase):
                inference_type = COMMAND_PHRASES[phrase]
                break

        working_memory.add("user", spoken_text)

        # --- Build Perception ---
        self._update_perception(
            spoken_text,
            recognized_speaker,
            transcription,
            truncated
        )

        # --- REFLEX PASS ---
        reflex_fired = await self._run_reflexes()
        if reflex_fired:
            # reflex took over → skip cognition
            return

        # --- Build Event ---
        event = event_builder.build_event(
            perception=g["perception"].snapshot(),
            working_memory=working_memory.turns,
        )
        print(f"[ActiveLoop] Built Event: {event}")  # Debug print to verify event structure
        # --- Send to Server & Get Response ---
        server_json = await self._send_to_server(event, inference_type)
        print(f"[ActiveLoop] Server Response: {server_json}")  # Debug print to verify server response structure
        # --- Speech + decision layer ---
        hal_speech = server_json.get("speech", [])
        if hal_speech:
            text = " ".join(seg.get("text", "") for seg in hal_speech if isinstance(seg, dict))
            if text:
                working_memory.add("hal", text)
        print(f"[ActiveLoop] working_memory: {working_memory.turns}")  # Debug print to verify speech extraction
        # --- Send to Cortex for processing ---
        await cortex.tick(server_json)
        indicators.set_mode("idle")
