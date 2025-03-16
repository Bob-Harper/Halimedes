from helpers.db_helper import HalDBHelper

async def get_system_prompt(recognized_speaker, user_emotion):
    """Dynamically fetches system prompts from the database, including system-level instructions."""

    db_helper = HalDBHelper()
    await db_helper.init_db()

    # Fetch user-specific prompt
    base_prompt = await db_helper.fetch_prompt(recognized_speaker)

    # Fetch system-wide instruction set (system01)
    system_instruction = await db_helper.fetch_prompt("system01")

    # Fallbacks in case any are missing
    if not base_prompt:
        base_prompt = "You are a quirky four-legged crawler robot. Multiple humans may speak; keep track of them by their names. This speaker is Unknown. Be friendly and neutral."
    if not system_instruction:
        system_instruction = "Standard instruction block missing! Default behavior engaged."

    # Standard emotional context
    emotional_tone = f"User emotion detected: {user_emotion}."

    # Combine everything
    full_prompt = f"{base_prompt} {system_instruction} {emotional_tone}"

    return full_prompt
