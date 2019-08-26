import alsaaudio as alsa

params = {
    "rate": 48000,
    "format": alsa.PCM_FORMAT_S16_LE,
    "period_size": 1024,
    "channels": 2
}
