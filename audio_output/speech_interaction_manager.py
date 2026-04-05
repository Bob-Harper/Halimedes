# mind/speech_interaction_manager.py

from dsl.macro_player import TagToDSL

class SpeechInteractionManager:
    def __init__(self, emotion_categorizer, macro_player,
                 voiceprint_manager, llm_client):
        self.emotion_categorizer = emotion_categorizer
        self.macro_player = macro_player
        self.voiceprint_manager = voiceprint_manager
        self.llm_client = llm_client

    async def handle_speech(self, spoken_text, raw_audio):
        # User emotion
        user_emotion = self.emotion_categorizer.analyze_text_emotion(spoken_text)
        await self.macro_player.run(f"sound {user_emotion}")

        # Speaker identity
        recognized_speaker = self.voiceprint_manager.recognize_speaker(raw_audio)
        print(f"{recognized_speaker}: emotion: {user_emotion}\n{spoken_text}")

        # LLM response
        self.llm_client.set_speaker(recognized_speaker)
        user_input_for_llm = f"{recognized_speaker}: {spoken_text}"
        response_text = await self.llm_client.send_message_async(user_input_for_llm)

        # Hal’s emotion + expressive macro
        hal_emotion = self.emotion_categorizer.analyze_text_emotion(response_text)
        await self.macro_player.run(f"""
            expression set mood {hal_emotion}
            sound {hal_emotion}
            action expressive
        """)

        # Response sequence
        macro_script = TagToDSL.parse(response_text)
        await self.macro_player.run(macro_script)
