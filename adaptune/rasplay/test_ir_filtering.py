#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
This is app for playing WAV/FLAC audio.
'''
import argparse

import sounddevice as sd
import soundfile as sf

import tools
from player import AudioPlayer
import impulse_response as ir


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser()
    tools.add_arg_for_player(PARSER)
    ARGS = PARSER.parse_args()

    DEV = AudioPlayer(
        filename=ARGS.filename,
        device=ARGS.output_device,
        blocksize=ARGS.blocksize,
        bufsize=ARGS.buffersize
    )

    try:
        DEV.main()

    except KeyboardInterrupt:
        exit('\nInterrupted by user')

