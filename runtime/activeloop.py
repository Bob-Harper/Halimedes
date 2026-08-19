# activeloop.py
import json
import asyncio
import time
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
        self.log_data = False  # False by default, flip it True to enabe logging to file

    async def run(self):
        # start concurrent loops
        asyncio.create_task(self._sensor_loop())
        # asyncio.create_task(self._audio_loop())  # Disabled to test reflex loop

        while True:
            # 1. Hot‑swap first
            self.hotswap.process(self.globals)

            # 2. Tick pacing
            await asyncio.sleep(active_loop_config["tick_rate"])

    # ------------------------------
    # REFLEX LOOP BEGIN

    async def _sensor_loop(self):
        g = self.globals
        sensor_state = g["sensor_state"]
        while True:

            await sensor_state.update()

            snapshot = sensor_state.snapshot()
            if self.log_data:
                with open("data/sensor_snapshot.log", "a") as f:
                    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + f".{int(time.time() * 1000) % 1000:03d}"
                    f.write("\n\n==================== BEGIN SENSOR SNAPSHOT ====================\n")
                    f.write(f"{ts}\n")
                    # f.write(json.dumps(snapshot, indent=4))  # FOR ENTIRE SNAPSHOT.  for FILTERED use the following
                    # START FILTERED OUTPUT
                    filtered = {
                        "gravity": snapshot.get("gravity"),
                        "linear_acceleration": snapshot.get("linear_acceleration"),
                    }
                    f.write(json.dumps(filtered, indent=4))
                    # END FILTERED OUTPUT
                    f.write("\n==================== END SENSOR SNAPSHOT ====================\n")

            # Perception can still store a copy
            # but reflexes should NOT depend on perception anymore.
            # g["perception"].sensor_status.update(snapshot)

            reflex_fired = await self._run_reflexes(snapshot)
            # if reflex_fired:
            #     print(f"[Reflex Plan Performed] {reflex_fired}")

            await asyncio.sleep(0.05)

    async def _run_reflexes(self, sensor_snapshot):
        reflex_engine = self.globals["reflex_engine"]
        result = await reflex_engine.check_and_plan(
            sensor_state=sensor_snapshot,
            world_state=self.globals["world_state"],
            hardware_state=self.globals["hardware_state"],
            executor=self.globals["action_executor"],
        )

        if not result:
            return False
        return await self._handle_reflex(result)


    async def _handle_reflex(self, reflex_plan):
        executor = self.globals["action_executor"]
        executor.execute_reflex(reflex_plan)
        return reflex_plan # return plan after executing allows to store the event and related data in longterm memories.

    # REFLEX LOOP END
    # ------------------------------

    async def _run_autonomous_behaviors(self):
        pass # stub for now to allow for autonomous behaviors in the future without blocking reflexes or speech processing

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
        sensor_state = self.globals["sensor_state"]
        snapshot = sensor_state.snapshot()
        self.globals["perception"].sensor_status["imu"] = snapshot["imu"]

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


    async def _audio_loop(self):
        print("[ActiveLoop] Hal Listening.")
        g = self.globals
        audio_input = g["audio_input"]
        indicators = g["indicators"]
        working_memory = g["working_memory"]
        event_builder = g["event_builder"]
        cortex = g["cortex"]

        self.hotswap.process(g)

        pcm_audio = await audio_input.capture_audio()
        # if pcm_audio is None or pcm_audio.size == 0: # Audio loop should not determine if any other loop should be running.
        #     self._update_perception_no_audio()
        #     await self._run_reflexes()
        #     await self._run_autonomous_behaviors()
        #     return

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

        # --- Build Event ---
        event = event_builder.build_event(
            perception=g["perception"].snapshot(),
            working_memory=working_memory.turns,
        )
        # --- Send to Server & Get Response ---
        server_json = await self._send_to_server(event, inference_type)
        # --- Speech + decision layer ---
        hal_speech = server_json.get("speech", [])
        if hal_speech:
            text = " ".join(seg.get("text", "") for seg in hal_speech if isinstance(seg, dict))
            if text:
                working_memory.add("hal", text)
        # --- Send to Cortex for processing ---
        await cortex.tick(server_json)
        indicators.set_mode("idle")
