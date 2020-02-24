from ..driver.filter_driver import FilterDriver, apply_filter
from ..driver.sound import setup_sounddevice
import sounddevice as _sd
from ..helper.config import load_settings
from typing import Dict
from queue import Queue


def run():
    STFT = None
    DATAQUEUE = Queue()
    settings = load_settings()
    DRIVER = FilterDriver()
    DOMAIN = settings.get("DOMAIN")
    if DOMAIN == "freq":
        STFT = DRIVER.filter_.stft

    def callback_with_applying(indata, outdata, frames, time, status):
        W = DRIVER.get_filter_weights()
        outdata[:] = apply_filter(W, indata, domain=DOMAIN, stftobj=STFT)

    setup_sounddevice(settings)

    devices: Dict = settings.get("SOUND.target")

    MAIN = _sd.Stream(device=(devices["system"], devices["main"]))
    OBSERVER = _sd.Stream(device=devices["observer"])
