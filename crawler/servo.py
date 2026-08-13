#!/usr/bin/env python3
from crawler.pwm import PWM
from crawler.utils import mapping


class Servo(PWM):
    """Servo motor class"""

    MAX_PW = 2500
    MIN_PW = 500
    FREQ = 50
    PERIOD = 4095

    def __init__(self, channel, address=None, min_pw=500, max_pw=2500, *args, **kwargs):
        """
        Initialize the servo motor class.

        :param channel: PWM channel number (0–14 / P0–P14)
        """
        super().__init__(channel, address, *args, **kwargs)
        self.period(self.PERIOD)
        prescaler = self.CLOCK / self.FREQ / self.PERIOD
        self.prescaler(prescaler)
        self.MIN_PW = min_pw
        self.MAX_PW = max_pw
        self._angle = 0.0

    # ------------------------------
    # Angle property
    # ------------------------------

    @property
    def angle(self) -> float:
        """Current servo angle in degrees."""
        return self._angle

    @angle.setter
    def angle(self, value: float) -> None:
        """Set servo angle (-90 to 90 degrees)."""
        if not isinstance(value, (int, float)):
            raise ValueError(f"Angle must be int or float, not {type(value)}")

        # Clamp
        value = max(-90, min(90, value))
        self._angle = float(value)

        self._debug(f"Set angle to: {value}")

        pulse_width = mapping(value, -90, 90, self.MIN_PW, self.MAX_PW)
        self._debug(f"Pulse width: {pulse_width}")

        self._set_pulse_width_time(pulse_width)

    # ------------------------------
    # Internal pulse width handler
    # ------------------------------

    def _set_pulse_width_time(self, pulse_width_time: float) -> None:
        """Convert pulse width (µs) to PCA9685 ticks."""
        pulse_width_time = max(self.MIN_PW, min(self.MAX_PW, pulse_width_time))

        pwr = pulse_width_time / 20000
        self._debug(f"pulse width rate: {pwr}")

        value = int(pwr * self.PERIOD)
        self._debug(f"pulse width value: {value}")

        self.pulse_width(value)

"""

Product description

9g Coreless Servo Black, Full Metal Gear Micro RC Servo 4KG-CM Torque 4.8-8.4V for Arduino Fixed-wing Aircraft RC Smart Car Robotic Arm DIY Projects (180 Degree)

Products Specifcation :
Products Name: 9g micro coreless servo

Apply Environmental Conditon
Storage Temperature Range: -30°C-80°C
Operating Temperature Range: -15°C-70°C
Operating Voltage Range: 4.8-8.4V

Mechanical Specifications
Size: 24*11.8*21.9mm / 0.94x0.46x0.86 in
Weight:13g
Gear type: Full Metal
Gear ratio:410
Bearing: Double Bearing
Connector wire: 170±5mm / 6.69 ±0.19 in
Motor : 3-Pole(k)
Horn gear spline: 25T
Horn type: Plastic
Case: Engineering plastics

Electrical Specifications
Operat voltage: 4.8V-8.4V
Idle current(at stopped): 4mA(6V), 5mA(7.4V), 6mA(8.4V)
Operating speed (at no load): 0.14sec/60° (6V) , 0.12sec/60°(7.4V), 0.10sec/60°(8.4V)
Stall torque (at locked): 3.5kg-cm(6V) , 4 kg-cm(7.4V), 5 kg-cm(8.4V)
Stall current (at locked):0.6A(6V), 0.8A(7.4V), 1.0A(8.4V)

Control Specifications
Control System : PWM (Pulse width modification)
Pulse width range: 500-2500μsec
Neutral position: 1500μsec
Running degree: 180°(when 500-2500μsec) / 90°（when remote control 1000-2000μsec)
Dead band width: 3 μsec
Operating frequency: 50-330Hz
Rotating direction: Counterclockwise (when 500～2500 μsec)

"""