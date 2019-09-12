#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
This is app for playing WAV/FLAC audio.
'''
import argparse

import sounddevice as sd
import soundfile as sf

from adaptune.inpulseres import tools


class AudioPlayer:
    '''
    audio player
    '''
    DATATYPE = 'float32'

    def __init__(self, filename, device, blocksize, bufsize):
        self.file = filename
        print(sd.query_devices())
        self.device = tools.int_or_str(input()) if device < 0 else device
        self.blksize = blocksize
        self.bufsize = bufsize

    def main(self):
        '''
        main-func
        '''
        data, f_s = sf.read(self.file, dtype=sd.default.dtype[1])
        sd.play(data, f_s, device=self.device)

        if sd.wait():
            exit('Error while playing   : ' + str(sd.wait()))

    def shutdown(self):
        '''
        shutdown this device
        '''


class AudioPlayRec:
    '''
    audio player and recorder
    '''
    DATATYPE = 'float32'

    def __init__(self, filename, devices, blocksize, bufsize, channels=2):
        self.file = filename
        print(sd.query_devices())
        self.device = [
            tools.int_or_str(input()) if dev < 0 else dev for dev in devices]
        self.blksize = blocksize
        self.bufsize = bufsize
        self.channels = channels

    def main(self):
        '''
        main-func
        '''
        data, f_s = sf.read(self.file, dtype=sd.default.dtype[1])
        recdata = sd.playrec(
            data,
            f_s,
            device=self.device,
            channels=self.channels,
            dtype=self.DATATYPE,
            blocksize=self.blksize)

        if sd.wait():
            exit('Error while playing   : ' + str(sd.wait()))

        return recdata, f_s

    def shutdown(self):
        '''
        shutdown this device
        '''


if __name__ == '__main__':

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
