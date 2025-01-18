from bot.stygia_logging import logger
# usage: logger.debug(f"The value of my_variable is: {my_variable}") / logger.info(" |Stygia connected to Discord")
import ephem
from datetime import datetime


class LunarEffects:
    @staticmethod
    def calculate_moon_phase():
        try:
            moon = ephem.Moon()
            moon.compute(datetime.utcnow())
            moon_phase = moon.phase / 100  # Normalize moon phase to be between 0 and 1
            rounded_moon_phase = round(moon_phase, 4)  # Round to 4 places
            return rounded_moon_phase
        except Exception as e:
            logger.error(f"\nError calculating moon phase: {e}")
            return None

    @staticmethod
    def is_new_moon(moon_phase):
        return moon_phase <= 0.035  # New Moon threshold

    @staticmethod
    def is_full_moon(moon_phase):
        return moon_phase >= 0.983125  # Full Moon threshold

    @staticmethod
    def moon_phase_name(moon_phase):
        # Define moon phase names and their corresponding percentage ranges
        phase_names = {
            "New Moon. Time to sulk. We hate everyone. Leave us alone.": (0.0, 0.0349),
            "Crescent": (0.035, 0.333),
            "Half": (0.333, 0.666),
            "Gibbous": (0.666, 0.983125),
            "Full Moon. Let's demonstrate the origin of the word LUNATIC.": (0.983125, 1.0),
        }

        # Find the moon phase name based on the percentage
        for phase, (lower, upper) in phase_names.items():
            if lower <= moon_phase < upper:
                return phase

        # If the moon phase is not in the defined ranges, return "Unknown"
        return "OMG THE MOON IS MADE OF CHEESE"


"""
# Other lunar phase-related methods can be added here as needed
# Full Moon 0.983125 is 12 hours before and after, 24 hours total.
# New Moon.  48 hours = 0.0675, 24 hours before and after
# 1 hour is 0.0014124, 12 hour is .016875
"""

# Testing the class
if __name__ == "__main__":
    luna = ephem.Moon(datetime.utcnow())
    lunar_effects = LunarEffects()
    lunar_phase = lunar_effects.calculate_moon_phase()
    lunar_phase_name = lunar_effects.moon_phase_name(lunar_phase)
    constell = ephem.constellation(luna)
    print("Moon Phase:", lunar_phase)
    print("Moon Phase Name:", lunar_phase_name)
    print("Moon in the constellation of:", constell[1])
    print("Is New Moon:", lunar_effects.is_new_moon(lunar_phase))
    print("Is Full Moon:", lunar_effects.is_full_moon(lunar_phase))
