#!/usr/bin/env python3
import os
import platform
import re
import subprocess
from typing import Dict, Tuple, Optional

# utils
# =================================================================
def run_command(cmd: str) -> Tuple[Optional[int], str]:
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )

    # FIX: Assert to Pylance that p.stdout definitely exists because we passed stdout=PIPE
    assert p.stdout is not None
    result = p.stdout.read().decode('utf-8')

    # Wait for the process to safely terminate so p.poll() is guaranteed to give an int status
    p.wait()
    status = p.poll()

    return status, result

def getIP() -> Tuple[Optional[str], Optional[str]]:
    # Modernized from os.popen to subprocess to maintain robust execution
    try:
        wlan0_raw = subprocess.check_output("ifconfig wlan0 | awk '/inet/' | awk 'NR==1 {print $2}'", shell=True)
        wlan0: Optional[str] = wlan0_raw.decode('utf-8').strip()
    except subprocess.CalledProcessError:
        wlan0 = None

    try:
        eth0_raw = subprocess.check_output("ifconfig eth0 | awk '/inet/' | awk 'NR==1 {print $2}'", shell=True)
        eth0: Optional[str] = eth0_raw.decode('utf-8').strip()
    except subprocess.CalledProcessError:
        eth0 = None

    if wlan0 == '':
        wlan0 = None
    if eth0 == '':
        eth0 = None

    return wlan0, eth0

def check_machine_type() -> Tuple[int, str]:
    machine_type = platform.machine()
    if machine_type == "armv7l":
        return 32, machine_type
    elif machine_type == "aarch64":
        return 64, machine_type
    else:
        raise ValueError(f"[{machine_type}] not supported")

def load_labels(path: str) -> Dict[int, str]:
    """Loads the labels file. Supports files with or without index numbers."""
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        labels: Dict[int, str] = {}
        for row_number, content in enumerate(lines):
            pair = re.split(r'[:\s]+', content.strip(), maxsplit=1)
            if len(pair) == 2 and pair[0].strip().isdigit():
                labels[int(pair[0])] = pair[1].strip()
            else:
                labels[row_number] = pair[0].strip()
    return labels
