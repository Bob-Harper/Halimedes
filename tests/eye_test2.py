# STARTUP.PY AUTOSTART SERVICE IS DISABLED, HAL WILL BOOT STRAIGHT INTO WORK MODE
import asyncio
import time
import random
import warnings
warnings.simplefilter('ignore')
from helpers.global_config import OLLAMALAPTOP
""" 
Import the Picrawler class from the picrawler module first 
to pass through to all helper classes that use it.  This
prevents multiple initializations of the Picrawler class.
"""
from body.picrawler import Picrawler 
# Create a single instance of Picrawler to pass through
picrawler_instance = Picrawler()
from helpers.response_manager import Response_Manager
from helpers.passive_actions_manager import PassiveActionsManager
from eyes.eye_animator import EyeAnimator
from eyes.eye_loader import load_eye_profile
# from eyes.core.blink_engine import BlinkEngine
from sequencers.behaviour_sequencer  import BehaviorSequencer
# from sequencers.blink_channel import BlinkChannel
from sequencers.expression_channel import ExpressionChannel
from sequencers.gaze_channel import GazeChannel
from sequencers.speech_channel import SpeechChannel


async def main():
    print("Entered main()")
    # Initialize everything at module level
    eye_profile = load_eye_profile("vector03")
    eye_animator = EyeAnimator(eye_profile)
    actions_manager = PassiveActionsManager(picrawler_instance)
    response_manager = Response_Manager(picrawler_instance, actions_manager, eye_animator)  # Set once
    speech_chan = SpeechChannel(response_manager)
    gaze_chan  = GazeChannel(eye_animator, tracker=None)
    expr_chan  = ExpressionChannel(eye_animator)
    # blinker = BlinkEngine(eye_animator)
    # blink_chan = BlinkChannel(eye_animator)    # fire & forget blink loop
   # asyncio.create_task(blinker.idle_blink_loop())  # kick off its loop
    # ——— SEQUENCER ———
    seq = BehaviorSequencer({
        "gaze":       gaze_chan,
        "expression": expr_chan,
        #"blink":      blink_chan,
        "speech":     speech_chan,
        })
    DIRECTIONS = {
        "center": (10,10),
        "left":   ( 0,10),
        "right":  (20,10),
        "up":     (10, 0),
        "down":   (10,20),
        "wander": (
            random.randint(0, 20),
            random.randint(0, 20)
        )    }

            
    t =0
    seq.schedule(t, "expression", lambda ch: ch.set_mood("skeptical"))

    t += 0.5
    seq.schedule(t, "speech", lambda c: c.trigger(
        "Beginning startup procedure and status check.",
        emotion="neutral"
    ))

    t += 1.5
    seq.schedule(t, "speech", lambda c: c.trigger(
        "Servos powered. Camera online. Interactive visual display initiating."
    ))

    t += 1.5
    seq.schedule(t, "speech", lambda c: c.trigger(
        "Gaze tracking initiated. Eye animation system online."
    ))

    t += 1.5
    seq.schedule(t, "expression", lambda ch: ch.set_mood("skeptical"))

    t += 0.5
    seq.schedule(t, "speech", lambda c: c.trigger(
        "This is so exciting! I can hardly wait to see what happens!  " \
        "get it?  See what happens?  Eye test.  well It was funny to me.  Moving along now."
    ))

    # 2) Starting at t=1s, blast through a pupil sweep via gaze channel
    t += 3.0
    for size in [3, .05, 3.2, .01, 2, .033, 1]:
        # we assume GazeChannel has a method `set_gaze(x,y,pupil)`
        seq.schedule(t, "gaze", lambda ch, s=size: ch.set_gaze(10, 10, s))
        t += 0.1
    t += 1.0

    # 3) Then do your expression→gaze choreography
    for mood in ["happy","sad","angry","focused","skeptical","surprised","test2","neutral"]:
        # expression change
        seq.schedule(t, "expression", lambda ch, m=mood: ch.set_mood(m))
        t += 2.0

        # a little five-step gaze dance
        for look in ["center","left","center","right","center","up","center","down","wander"]:
            if look == "wander":
                seq.schedule(t, "gaze", lambda ch: 
                    ch.set_gaze(
                        random.randint(0,20), 
                        random.randint(0,20), 
                        1.0
                    )
                )
            else:
                x,y = DIRECTIONS[look]
                seq.schedule(t, "gaze", 
                            lambda ch, x=x, y=y: ch.set_gaze(x, y, 1.0))
            t += 1.0

    # kick it off
    seq.start()
    # for when, key, _ in seq.timeline:
    #     print(f"   {when:5.2f}s → {key}")

    # initialize your clock exactly once:
    prev = time.time()

    try:
        while True:
            now = time.time()
            dt  = now - prev
            prev = now

            seq.update(dt)
            await asyncio.sleep(0.016)

    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    asyncio.run(main())
