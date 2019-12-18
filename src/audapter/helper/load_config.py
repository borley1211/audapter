from dynaconf import settings
import sounddevice as sd


# set samplerate
settings.set('SOUND.SYSTEM.RATE', sd.default.samplerate)
