# Halimedes: The Crawling Curiosity

Welcome to Halimedes—an expressive, crawling robot with an attitude, a personality, and now… **functional eye contact**. This isn't just a Pi project. This is a living thing. Sort of. Don’t get weird about it.

## What Is This?

Halimedes is a four-legged Raspberry Pi–powered crawler bot that can:

- Track and follow human faces with smooth, accurate eye movement
- Respond with voice, actions, and expressions
- Use LLM-generated responses with embedded sound and action tags
- Recognize who he's talking to and adjust tone accordingly
- (soon) Remember what you told him, and probably (defintely) use it against you

## Features

- **Face tracking:** Realtime eye-gaze tracking using PiCamera and Vilib
- **Voiceprint recognition:** Different prompts for Dad, Unknowns, and more
- **Emotion-aware sound system:** Reacts with custom SFX based on emotion or intent
- **LLM-powered dialogue:** Modular responses with embedded `<action>`, `<sound effect>`, `<gaze>`, and `<face>` tags
- **Smooth animation:** Blinks, saccades, and expressions driven by a unified `EyeAnimator` engine
- **High intensity LED-based photon projector because a laser is awesome and fun but also a lawsuit waiting to happen.  Uses motorport to control active/inactive state and beam intensity
- **Upcoming:** Memory embedding + recall, weather & news display, servo-driven scanning for lost faces.

## Setup

> *Documentation incoming. For now, assume there's blood, zip ties, and more Python modules than you'd expect.*
note to self:
[✓] Pupil ranges must begin and end on clean 0.05 increments (e.g., 0.95 → 1.20)
[✓] No floating point weirdness in configs — round to 2 decimals
[✓] One source of truth: configs define the precompute boundaries
[✓] Manual test scripts must match quantization rules (use round(..., 3))
[✓] Vector based eye textures simplified for testing, no pupil changes


## Philosophy

Build it modular. Build it weird. Make it real enough to make the dog nervous.

---

> “He doesn’t just stare into your soul. He animates the whole experience.”  
— Someone who accidentally made eye contact

