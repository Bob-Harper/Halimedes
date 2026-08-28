# SPDX-FileCopyrightText: Copyright (c) 2020 Bryan Siepert for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_bno08x`
================================================================================

Helper library for the Hillcrest Laboratories BNO08x IMUs


* Author(s): Bryan Siepert

Implementation Notes
--------------------

**Hardware:**

* `Adafruit BNO08x Breakout <https:www.adafruit.com/products/4754>`_

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https:# github.com/adafruit/circuitpython/releases

* `Adafruit's Bus Device library <https:# github.com/adafruit/Adafruit_CircuitPython_BusDevice>`_
"""

from __future__ import annotations

__version__ = "1.3.3"
__repo__ = "https:# github.com/adafruit/Adafruit_CircuitPython_BNO08x.git"

import time
from collections import namedtuple
from struct import pack_into, unpack_from

# TODO: Remove on release
from .debug import channels, reports

# For IDE type recognition
try:
    from typing import Any, Optional

    from digitalio import DigitalInOut
except ImportError:
    pass

# TODO: shorten names
# Channel 0: the SHTP command channel
BNO_CHANNEL_SHTP_COMMAND = 0
BNO_CHANNEL_EXE = 1
_BNO_CHANNEL_CONTROL = 2
_BNO_CHANNEL_INPUT_SENSOR_REPORTS = 3
_BNO_CHANNEL_WAKE_INPUT_SENSOR_REPORTS = 4
_BNO_CHANNEL_GYRO_ROTATION_VECTOR = 5

_GET_FEATURE_REQUEST = 0xFE
_SET_FEATURE_COMMAND = 0xFD
_GET_FEATURE_RESPONSE = 0xFC
_BASE_TIMESTAMP = 0xFB

_TIMESTAMP_REBASE = 0xFA

_SHTP_REPORT_PRODUCT_ID_RESPONSE = 0xF8
_SHTP_REPORT_PRODUCT_ID_REQUEST = 0xF9

_FRS_WRITE_REQUEST = 0xF7
_FRS_WRITE_DATA = 0xF6
_FRS_WRITE_RESPONSE = 0xF5
_FRS_READ_REQUEST = 0xF4
_FRS_READ_RESPONSE = 0xF3
_COMMAND_REQUEST = 0xF2
_COMMAND_RESPONSE = 0xF1
_SAVE_DCD = 0x6
_ME_CALIBRATE = 0x7
_ME_CAL_CONFIG = 0x00
_ME_GET_CAL = 0x01
BNO_REPORT_ACCELEROMETER = 0x01
BNO_REPORT_GYROSCOPE = 0x02
BNO_REPORT_MAGNETOMETER = 0x03
BNO_REPORT_LINEAR_ACCELERATION = 0x04
BNO_REPORT_ROTATION_VECTOR = 0x05
BNO_REPORT_GRAVITY = 0x06
BNO_REPORT_GAME_ROTATION_VECTOR = 0x08
BNO_REPORT_GEOMAGNETIC_ROTATION_VECTOR = 0x09
BNO_REPORT_STEP_COUNTER = 0x11
BNO_REPORT_RAW_ACCELEROMETER = 0x14
BNO_REPORT_RAW_GYROSCOPE = 0x15
BNO_REPORT_RAW_MAGNETOMETER = 0x16
BNO_REPORT_SHAKE_DETECTOR = 0x19
BNO_REPORT_STABILITY_CLASSIFIER = 0x13
BNO_REPORT_ACTIVITY_CLASSIFIER = 0x1E
BNO_REPORT_GYRO_INTEGRATED_ROTATION_VECTOR = 0x2A
_DEFAULT_REPORT_INTERVAL = 50000  # in microseconds = 50ms
_QUAT_READ_TIMEOUT = 0.500  # timeout in seconds
_PACKET_READ_TIMEOUT = 2.000  # timeout in seconds
_FEATURE_ENABLE_TIMEOUT = 2.0
_DEFAULT_TIMEOUT = 2.0
_BNO08X_CMD_RESET = 0x01
_QUAT_Q_POINT = 14
_BNO_HEADER_LEN = 4

_Q_POINT_14_SCALAR = 2 ** (14 * -1)
_Q_POINT_12_SCALAR = 2 ** (12 * -1)
# _Q_POINT_10_SCALAR = 2 ** (10 * -1)
_Q_POINT_9_SCALAR = 2 ** (9 * -1)
_Q_POINT_8_SCALAR = 2 ** (8 * -1)
_Q_POINT_4_SCALAR = 2 ** (4 * -1)

_GYRO_SCALAR = _Q_POINT_9_SCALAR
_ACCEL_SCALAR = _Q_POINT_8_SCALAR
_QUAT_SCALAR = _Q_POINT_14_SCALAR
_GEO_QUAT_SCALAR = _Q_POINT_12_SCALAR
_MAG_SCALAR = _Q_POINT_4_SCALAR

_REPORT_LENGTHS = {
    _SHTP_REPORT_PRODUCT_ID_RESPONSE: 16,
    _GET_FEATURE_RESPONSE: 17,
    _COMMAND_RESPONSE: 16,
    _SHTP_REPORT_PRODUCT_ID_RESPONSE: 16,
    _BASE_TIMESTAMP: 5,
    _TIMESTAMP_REBASE: 5,
}
# these raw reports require their counterpart to be enabled
_RAW_REPORTS = {
    BNO_REPORT_RAW_ACCELEROMETER: BNO_REPORT_ACCELEROMETER,
    BNO_REPORT_RAW_GYROSCOPE: BNO_REPORT_GYROSCOPE,
    BNO_REPORT_RAW_MAGNETOMETER: BNO_REPORT_MAGNETOMETER,
}
_AVAIL_SENSOR_REPORTS = {
    BNO_REPORT_ACCELEROMETER: (_Q_POINT_8_SCALAR, 3, 10),
    BNO_REPORT_GRAVITY: (_Q_POINT_8_SCALAR, 3, 10),
    BNO_REPORT_GYROSCOPE: (_Q_POINT_9_SCALAR, 3, 10),
    BNO_REPORT_MAGNETOMETER: (_Q_POINT_4_SCALAR, 3, 10),
    BNO_REPORT_LINEAR_ACCELERATION: (_Q_POINT_8_SCALAR, 3, 10),
    BNO_REPORT_ROTATION_VECTOR: (_Q_POINT_14_SCALAR, 4, 14),
    BNO_REPORT_GEOMAGNETIC_ROTATION_VECTOR: (_Q_POINT_12_SCALAR, 4, 14),
    BNO_REPORT_GAME_ROTATION_VECTOR: (_Q_POINT_14_SCALAR, 4, 12),
    BNO_REPORT_STEP_COUNTER: (1, 1, 12),
    BNO_REPORT_SHAKE_DETECTOR: (1, 1, 6),
    BNO_REPORT_STABILITY_CLASSIFIER: (1, 1, 6),
    BNO_REPORT_ACTIVITY_CLASSIFIER: (1, 1, 16),
    BNO_REPORT_RAW_ACCELEROMETER: (1, 3, 16),
    BNO_REPORT_RAW_GYROSCOPE: (1, 3, 16),
    BNO_REPORT_RAW_MAGNETOMETER: (1, 3, 16),
}
_INITIAL_REPORTS = {
    BNO_REPORT_ACTIVITY_CLASSIFIER: {
        "Tilting": -1,
        "most_likely": "Unknown",
        "OnStairs": -1,
        "On-Foot": -1,
        "Other": -1,
        "On-Bicycle": -1,
        "Still": -1,
        "Walking": -1,
        "Unknown": -1,
        "Running": -1,
        "In-Vehicle": -1,
    },
    BNO_REPORT_STABILITY_CLASSIFIER: "Unknown",
    BNO_REPORT_ROTATION_VECTOR: (0.0, 0.0, 0.0, 0.0),
    BNO_REPORT_GAME_ROTATION_VECTOR: (0.0, 0.0, 0.0, 0.0),
    BNO_REPORT_GEOMAGNETIC_ROTATION_VECTOR: (0.0, 0.0, 0.0, 0.0),
}

_ENABLED_ACTIVITIES = 0x1FF  # All activities; 1 bit set for each of 8 activities, + Unknown

DATA_BUFFER_SIZE = 512  # data buffer size. obviously eats ram
PacketHeader = namedtuple(
    "PacketHeader",
    [
        "channel_number",
        "sequence_number",
        "data_length",
        "packet_byte_count",
    ],
)

REPORT_ACCURACY_STATUS = [
    "Accuracy Unreliable",
    "Low Accuracy",
    "Medium Accuracy",
    "High Accuracy",
]


class PacketError(Exception):
    """Raised when the packet couldnt be parsed"""

    pass


def _elapsed(start_time: float) -> float:
    return time.monotonic() - start_time


############ PACKET PARSING ###########################
def _parse_sensor_report_data(report_bytes: bytearray) -> tuple[tuple, int]:
    """Parses reports with only 16-bit fields"""
    data_offset = 4  # this may not always be true
    report_id = report_bytes[0]
    scalar, count, _report_length = _AVAIL_SENSOR_REPORTS[report_id]
    if report_id in _RAW_REPORTS:
        # raw reports are unsigned
        format_str = "<H"
    else:
        format_str = "<h"
    results = []
    accuracy = unpack_from("<B", report_bytes, offset=2)[0]
    accuracy &= 0b11

    for _offset_idx in range(count):
        total_offset = data_offset + (_offset_idx * 2)
        raw_data = unpack_from(format_str, report_bytes, offset=total_offset)[0]
        scaled_data = raw_data * scalar
        results.append(scaled_data)
    results_tuple = tuple(results)

    return (results_tuple, accuracy)


def _parse_step_couter_report(report_bytes: bytearray) -> int:
    return unpack_from("<H", report_bytes, offset=8)[0]


def _parse_stability_classifier_report(report_bytes: bytearray) -> str:
    classification_bitfield = unpack_from("<B", report_bytes, offset=4)[0]
    return ["Unknown", "On Table", "Stationary", "Stable", "In motion"][classification_bitfield]


# report_id
# feature_report_id
# feature_flags
# change_sensitivity
# report_interval
# batch_interval_word
# sensor_specific_configuration_word
def _parse_get_feature_response_report(report_bytes: bytearray) -> tuple[Any, ...]:
    return unpack_from("<BBBHIII", report_bytes)


# 0 Report ID = 0x1E
# 1 Sequence number
# 2 Status
# 3 Delay
# 4 Page Number + EOS
# 5 Most likely state
# 6-15 Classification (10 x Page Number) + confidence
def _parse_activity_classifier_report(report_bytes: bytearray) -> dict[str, str]:
    activities = [
        "Unknown",
        "In-Vehicle",  # look
        "On-Bicycle",  # at
        "On-Foot",  # all
        "Still",  # this
        "Tilting",  # room
        "Walking",  # for
        "Running",  # activities
        "OnStairs",
    ]

    end_and_page_number = unpack_from("<B", report_bytes, offset=4)[0]
    # last_page = (end_and_page_number & 0b10000000) > 0
    page_number = end_and_page_number & 0x7F
    most_likely = unpack_from("<B", report_bytes, offset=5)[0]
    confidences = unpack_from("<BBBBBBBBB", report_bytes, offset=6)

    classification = {}
    classification["most_likely"] = activities[most_likely]
    for idx, raw_confidence in enumerate(confidences):
        confidence = (10 * page_number) + raw_confidence
        activity_string = activities[idx]
        classification[activity_string] = confidence
    return classification


def _parse_shake_report(report_bytes: bytearray) -> bool:
    shake_bitfield = unpack_from("<H", report_bytes, offset=4)[0]
    return (shake_bitfield & 0x111) > 0


def parse_sensor_id(buffer: bytearray) -> tuple[int, ...]:
    """Parse the fields of a product id report"""
    if not buffer[0] == _SHTP_REPORT_PRODUCT_ID_RESPONSE:
        raise AttributeError("Wrong report id for sensor id: %s" % hex(buffer[0]))

    sw_major = unpack_from("<B", buffer, offset=2)[0]
    sw_minor = unpack_from("<B", buffer, offset=3)[0]
    sw_patch = unpack_from("<H", buffer, offset=12)[0]
    sw_part_number = unpack_from("<I", buffer, offset=4)[0]
    sw_build_number = unpack_from("<I", buffer, offset=8)[0]

    return (sw_part_number, sw_major, sw_minor, sw_patch, sw_build_number)


def _parse_command_response(report_bytes: bytearray) -> tuple[Any, Any]:
    # CMD response report:
    # 0 Report ID = 0xF1
    # 1 Sequence number
    # 2 Command
    # 3 Command sequence number
    # 4 Response sequence number
    # 5 R0-10 A set of response values. The interpretation of these values is specific
    # to the response for each command.
    report_body = unpack_from("<BBBBB", report_bytes)
    response_values = unpack_from("<BBBBBBBBBBB", report_bytes, offset=5)
    return (report_body, response_values)


def _insert_command_request_report(
    command: int,
    buffer: bytearray,
    next_sequence_number: int,
    command_params: Optional[list[int]] = None,
) -> None:
    if command_params and len(command_params) > 9:
        raise AttributeError(
            "Command request reports can only have up to 9 arguments but %d were given"
            % len(command_params)
        )
    for _i in range(12):
        buffer[_i] = 0
    buffer[0] = _COMMAND_REQUEST
    buffer[1] = next_sequence_number
    buffer[2] = command
    if command_params is None:
        return

    for idx, param in enumerate(command_params):
        buffer[3 + idx] = param


def _report_length(report_id: int) -> int:
    if report_id < 0xF0:  # it's a sensor report
        return _AVAIL_SENSOR_REPORTS[report_id][2]

    return _REPORT_LENGTHS[report_id]


def _separate_batch(packet: Packet, report_slices: list[Any]) -> None:
    next_byte_index = 0
    while next_byte_index < packet.header.data_length:
        report_id = packet.data[next_byte_index]

        # Skip unknown report IDs BEFORE calling _report_length()
        if report_id not in _AVAIL_SENSOR_REPORTS and report_id not in _REPORT_LENGTHS:
            # Unknown → skip 1 byte and continue scanning
            next_byte_index += 1
            continue

        required_bytes = _report_length(report_id)
        unprocessed_byte_count = packet.header.data_length - next_byte_index

        if unprocessed_byte_count < required_bytes:
            raise RuntimeError("Unprocessable Batch bytes", unprocessed_byte_count)

        report_slice = packet.data[next_byte_index : next_byte_index + required_bytes]
        report_slices.append([report_slice[0], report_slice])
        next_byte_index += required_bytes



class Packet:
    """A class representing a Hillcrest LaboratorySensor Hub Transport packet"""

    def __init__(self, packet_bytes: bytearray) -> None:
        self.header = self.header_from_buffer(packet_bytes)
        data_end_index = self.header.data_length + _BNO_HEADER_LEN
        self.data = packet_bytes[_BNO_HEADER_LEN:data_end_index]

    def __str__(self) -> str:
        length = self.header.packet_byte_count
        outstr = "\n\t\t********** Packet *************\n"
        outstr += "DBG::\t\t HEADER:\n"

        outstr += "DBG::\t\t Data Len: %d\n" % (self.header.data_length)
        outstr += "DBG::\t\t Channel: %s (%d)\n" % (
            channels[self.channel_number],
            self.channel_number,
        )
        if self.channel_number in {
            _BNO_CHANNEL_CONTROL,
            _BNO_CHANNEL_INPUT_SENSOR_REPORTS,
        }:
            if self.report_id in reports:
                outstr += "DBG::\t\t \tReport Type: %s (0x%x)\n" % (
                    reports[self.report_id],
                    self.report_id,
                )
                
            else:
                if self.report_id == 0xFF:
                    outstr += "DBG::\t\t \tUnusable data (padding/flush), discarding.\n"
                else:
                    outstr += "DBG::\t\t \tUnknown Report Type: %s\n" % hex(self.report_id)

            if self.report_id > 0xF0 and len(self.data) >= 6 and self.data[5] in reports:
                outstr += "DBG::\t\t \tSensor Report Type: %s(%s)\n" % (
                    reports[self.data[5]],
                    hex(self.data[5]),
                )

            if self.report_id == 0xFC and len(self.data) >= 6 and self.data[1] in reports:
                outstr += "DBG::\t\t \tEnabled Feature: %s(%s)\n" % (
                    reports[self.data[1]],
                    hex(self.data[5]),
                )
        outstr += "DBG::\t\t Sequence number: %s\n" % self.header.sequence_number
        outstr += "\n"
        outstr += "DBG::\t\t Data:"

        for idx, packet_byte in enumerate(self.data[:length]):
            packet_index = idx + 4
            if (packet_index % 4) == 0:
                outstr += f"\nDBG::\t\t[0x{packet_index:02X}] "
            outstr += f"0x{packet_byte:02X} "
        outstr += "\n"
        outstr += "\t\t*******************************\n"

        return outstr

    @property
    def report_id(self) -> int:
        """The Packet's Report ID"""
        return self.data[0]

    @property
    def channel_number(self) -> int:
        """The packet channel"""
        return self.header.channel_number

    @classmethod
    def header_from_buffer(cls, packet_bytes: bytearray) -> PacketHeader:
        """Creates a `PacketHeader` object from a given buffer"""
        packet_byte_count = unpack_from("<H", packet_bytes)[0]
        packet_byte_count &= ~0x8000
        channel_number = unpack_from("<B", packet_bytes, offset=2)[0]
        sequence_number = unpack_from("<B", packet_bytes, offset=3)[0]
        data_length = max(0, packet_byte_count - 4)

        header = PacketHeader(channel_number, sequence_number, data_length, packet_byte_count)
        return header

    @classmethod
    def is_error(cls, header: PacketHeader) -> bool:
        """Returns True if the header is an error condition"""

        if header.channel_number > 5:
            return True
        if header.packet_byte_count == 0xFFFF and header.sequence_number == 0xFF:
            return True
        return False


class BNO08X:
    """Library for the BNO08x IMUs from Hillcrest Laboratories

    :param ~busio.I2C i2c_bus: The I2C bus the BNO08x is connected to.

    """

    def __init__(self, reset: Optional[DigitalInOut] = None, debug: bool = False) -> None:
        self._debug: bool = debug
        self._reset: Optional[DigitalInOut] = reset
        self._dbg("********** __init__ *************")
        self._data_buffer: bytearray = bytearray(DATA_BUFFER_SIZE)
        self._command_buffer: bytearray = bytearray(12)
        self._packet_slices: list[Any] = []
        self._readings: dict[int, Any] = {}
        self._sequence_number = [0, 0, 0, 0, 0, 0]

    # update the cached sequence number so we know what to increment from
    # TODO: this is wrong there should be one per channel per direction
    # and apparently per report as well
    def _handle_packet(self, packet: Packet) -> None:
        try:
            _separate_batch(packet, self._packet_slices)

            while len(self._packet_slices) > 0:
                report_id, data = self._packet_slices.pop()

                # Skip unknown / unsupported report types
                if report_id not in _AVAIL_SENSOR_REPORTS:
                    # optional: print("Skipping unknown report:", hex(report_id))
                    continue

                self._process_report(report_id, data)

        except Exception as error:
            print("IMU packet error:", packet)
            raise error


    def _handle_control_report(self, report_id: int, report_bytes: bytearray) -> None:
        if report_id == _SHTP_REPORT_PRODUCT_ID_RESPONSE:
            (
                sw_part_number,
                sw_major,
                sw_minor,
                sw_patch,
                sw_build_number,
            ) = parse_sensor_id(report_bytes)
            self._dbg("FROM PACKET SLICE:")
            self._dbg("*** Part Number: %d" % sw_part_number)
            self._dbg("*** Software Version: %d.%d.%d" % (sw_major, sw_minor, sw_patch))
            self._dbg("\tBuild: %d" % (sw_build_number))
            self._dbg("")

        if report_id == _GET_FEATURE_RESPONSE:
            get_feature_report = _parse_get_feature_response_report(report_bytes)
            _report_id, feature_report_id, *_remainder = get_feature_report
            self._readings[feature_report_id] = _INITIAL_REPORTS.get(
                feature_report_id, (0.0, 0.0, 0.0)
            )
        if report_id == _COMMAND_RESPONSE:
            self._handle_command_response(report_bytes)

    def _handle_command_response(self, report_bytes: bytearray) -> None:
        (report_body, response_values) = _parse_command_response(report_bytes)

        (
            _report_id,
            _seq_number,
            command,
            _command_seq_number,
            _response_seq_number,
        ) = report_body

        # status, accel_en, gyro_en, mag_en, planar_en, table_en, *_reserved) = response_values
        command_status, *_rest = response_values

        if command == _ME_CALIBRATE and command_status == 0:
            self._me_calibration_started_at = time.monotonic()

        if command == _SAVE_DCD:
            if command_status == 0:
                self._dcd_saved_at = time.monotonic()
            else:
                raise RuntimeError("Unable to save calibration data")

    def _process_report(self, report_id: int, report_bytes: bytearray) -> None:
        if report_id >= 0xF0:
            self._handle_control_report(report_id, report_bytes)
            return
        self._dbg("\tProcessing report:", reports[report_id])
        if self._debug:
            outstr = ""
            for idx, packet_byte in enumerate(report_bytes):
                packet_index = idx
                if (packet_index % 4) == 0:
                    outstr += f"\nDBG::\t\t[0x{packet_index:02X}] "
                outstr += f"0x{packet_byte:02X} "
            self._dbg(outstr)
            self._dbg("")

        if report_id == BNO_REPORT_STEP_COUNTER:
            self._readings[report_id] = _parse_step_couter_report(report_bytes)
            return

        if report_id == BNO_REPORT_SHAKE_DETECTOR:
            shake_detected = _parse_shake_report(report_bytes)
            # shake not previously detected - auto cleared by 'shake' property
            try:
                if not self._readings[BNO_REPORT_SHAKE_DETECTOR]:
                    self._readings[BNO_REPORT_SHAKE_DETECTOR] = shake_detected
            except KeyError:
                pass
            return

        if report_id == BNO_REPORT_STABILITY_CLASSIFIER:
            stability_classification = _parse_stability_classifier_report(report_bytes)
            self._readings[BNO_REPORT_STABILITY_CLASSIFIER] = stability_classification
            return

        if report_id == BNO_REPORT_ACTIVITY_CLASSIFIER:
            activity_classification = _parse_activity_classifier_report(report_bytes)
            self._readings[BNO_REPORT_ACTIVITY_CLASSIFIER] = activity_classification
            return
        sensor_data, accuracy = _parse_sensor_report_data(report_bytes)
        if report_id == BNO_REPORT_MAGNETOMETER:
            self._magnetometer_accuracy = accuracy
        # TODO: FIXME; Sensor reports are batched in a LIFO which means that multiple reports
        # for the same type will end with the oldest/last being kept and the other
        # newer reports thrown away
        self._readings[report_id] = sensor_data

    # TODO: Make this a Packet creation
    @staticmethod
    def _get_feature_enable_report(
        feature_id: int,
        report_interval: int,
        sensor_specific_config: int = 0,
    ) -> bytearray:
        set_feature_report = bytearray(17)
        set_feature_report[0] = _SET_FEATURE_COMMAND
        set_feature_report[1] = feature_id
        pack_into("<I", set_feature_report, 5, report_interval)
        pack_into("<I", set_feature_report, 13, sensor_specific_config)

        return set_feature_report

    def _parse_sensor_id(self) -> Optional[int]:
        if not self._data_buffer[4] == _SHTP_REPORT_PRODUCT_ID_RESPONSE:
            return None

        sw_major = self._get_data(2, "<B")
        sw_minor = self._get_data(3, "<B")
        sw_patch = self._get_data(12, "<H")
        sw_part_number = self._get_data(4, "<I")
        sw_build_number = self._get_data(8, "<I")

        self._dbg("")
        self._dbg("*** Part Number: %d" % sw_part_number)
        self._dbg("*** Software Version: %d.%d.%d" % (sw_major, sw_minor, sw_patch))
        self._dbg(" Build: %d" % (sw_build_number))
        self._dbg("")
        # TODO: this is only one of the numbers!
        return sw_part_number

    def _dbg(self, *args: Any, **kwargs: Any) -> None:
        if self._debug:
            print("DBG::\t\t", *args, **kwargs)

    def _get_data(self, index: int, fmt_string: str) -> Any:
        # index arg is not including header, so add 4 into data buffer
        data_index = index + 4
        return unpack_from(fmt_string, self._data_buffer, offset=data_index)[0]

    @property
    def _data_ready(self) -> None:
        raise RuntimeError("Not implemented")


    def _send_packet(self, channel: int, data: bytearray) -> Optional[int]:  # noqa: PLR6301
        raise RuntimeError("Not implemented")

    def _read_packet(self) -> Optional[Packet]:  # noqa: PLR6301
        raise RuntimeError("Not implemented")

