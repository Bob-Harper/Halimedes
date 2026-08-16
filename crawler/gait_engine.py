# crawler/gait_engine.py
import time
from crawler.halcrawler_v2 import HalCrawler

class CreepGait:
    def __init__(self, robot: HalCrawler):
        self.bot = robot

        # 1. Standardize your proven, world-aligned baseline home coordinates
        self.BASE_X = 120.0
        self.BASE_Y = 120.0

        # 2. FIXED: Aligned variables with your physical real-world layout
        self.STAND_Z = 25.0    # Positive Z drives the feet DOWN below his body to support weight
        self.LIFT_Z = -40.0    # Negative Z explicitly pulls the foot UP into the air to step

        # 3. Gait stroke size
        self.STRIDE = 40.0

    def execute_forward_cycle(self, loops: int = 1):
        s = self.STRIDE
        bx = self.BASE_X
        by = self.BASE_Y
        z = self.STAND_Z
        lift = self.LIFT_Z

        print(f"Initiating true static-tripod crawl loop for {loops} cycles...")

        for i in range(loops):
            print(f"--- Stride Cycle {i+1} ---")

            # =================================================================
            # STEP 1: LEFT REAR (LR) SWING PHASE
            # Three stance legs lock level at 25.0 to carry weight.
            # LR lifts UP to -40.0 and steps forward.
            # =================================================================
            step_1 = {
                "LF": {"dx":  bx,     "dy":   by, "dz": z},     # Supporting Ground
                "RF": {"dx":  bx,     "dy":  -by, "dz": z},     # Supporting Ground
                "RR": {"dx": -bx,     "dy":  -by, "dz": z},     # Supporting Ground
                "LR": {"dx": -bx + s, "dy":   by, "dz": lift}   # LIFTS UP & STEPS FORWARD
            }
            self.bot.execute_local_step(step_1, speed=40)
            time.sleep(0.3)

            # Plant LR firmly back down to the supporting floor plane
            step_1["LR"]["dz"] = z
            self.bot.execute_local_step(step_1, speed=30)
            time.sleep(0.2)

            # =================================================================
            # STEP 2: LEFT FRONT (LF) SWING PHASE
            # Three stance legs lock level at 25.0. LF lifts UP to -40.0 and steps.
            # =================================================================
            step_2 = {
                "LF": {"dx":  bx + s, "dy":   by, "dz": lift},  # LIFTS UP & STEPS FORWARD
                "RF": {"dx":  bx,     "dy":  -by, "dz": z},     # Supporting Ground
                "RR": {"dx": -bx,     "dy":  -by, "dz": z},     # Supporting Ground
                "LR": {"dx": -bx + s, "dy":   by, "dz": z}      # Supporting Ground
            }
            self.bot.execute_local_step(step_2, speed=40)
            time.sleep(0.3)

            step_2["LF"]["dz"] = z
            self.bot.execute_local_step(step_2, speed=30)
            time.sleep(0.2)

            # =================================================================
            # STEP 3: THE BODY CREEP TRANSITION
            # All 4 feet are supporting on the ground. The body twists/shifts
            # forward, resetting the stance for the right-side sequence.
            # =================================================================
            body_shift = {
                "LF": {"dx":  bx,     "dy":   by, "dz": z},
                "RF": {"dx":  bx - s, "dy":  -by, "dz": z},
                "RR": {"dx": -bx - s, "dy":  -by, "dz": z},
                "LR": {"dx": -bx,     "dy":   by, "dz": z}
            }
            self.bot.execute_local_step(body_shift, speed=25)
            time.sleep(0.3)

            # =================================================================
            # STEP 4: RIGHT REAR (RR) SWING PHASE
            # Three stance legs lock level at 25.0. RR lifts UP to -40.0 and steps.
            # =================================================================
            step_3 = {
                "LF": {"dx":  bx,     "dy":   by, "dz": z},     # Supporting Ground
                "RF": {"dx":  bx - s, "dy":  -by, "dz": z},     # Supporting Ground
                "RR": {"dx": -bx + s, "dy":  -by, "dz": lift},  # LIFTS UP & STEPS FORWARD
                "LR": {"dx": -bx,     "dy":   by, "dz": z}      # Supporting Ground
            }
            self.bot.execute_local_step(step_3, speed=40)
            time.sleep(0.3)

            step_3["RR"]["dz"] = z
            self.bot.execute_local_step(step_3, speed=30)
            time.sleep(0.2)

            # =================================================================
            # STEP 5: RIGHT FRONT (RF) SWING PHASE
            # Three stance legs lock level at 25.0. RF lifts UP to -40.0 and steps.
            # =================================================================
            step_4 = {
                "LF": {"dx":  bx,     "dy":   by, "dz": z},     # Supporting Ground
                "RF": {"dx":  bx + s, "dy":  -by, "dz": lift},  # LIFTS UP & STEPS FORWARD
                "RR": {"dx": -bx + s, "dy":  -by, "dz": z},     # Supporting Ground
                "LR": {"dx": -bx,     "dy":   by, "dz": z}      # Supporting Ground
            }
            self.bot.execute_local_step(step_4, speed=40)
            time.sleep(0.3)

            step_4["RF"]["dz"] = z
            self.bot.execute_local_step(step_4, speed=30)
            time.sleep(0.2)
