import sounddevice as sd
from dynaconf import settings


def _set_samplerate():
    settings.load_file()
    settings.set('SOUND.SYSTEM.RATE', sd.default.samplerate)
