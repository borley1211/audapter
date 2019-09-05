#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
This is app for playing WAV/FLAC audio.
'''
import argparse


def int_or_str(text):
    '''
    Try to return 'text' as int
    '''
    try:
        return int(text)
    except ValueError:
        return text


def add_arg_for_player(parser):
    '''
    add args for using AudioPlayer
    '''
    parser.add_argument(
        'filename',
        nargs='?',
        help='audio file that you want to play')
    parser.add_argument(
        '--input-device', '-i',
        type=int_or_str,
        default=1,
        help='intput device (ID or string)')
    parser.add_argument(
        '--output-device', '-o',
        type=int_or_str,
        default=1,
        help='output device (ID or string)')
    parser.add_argument(
        '--blocksize', '-b',
        type=int,
        default=2048,
        help='block size (default: %(default)s)'
    )
    parser.add_argument(
        '--buffersize', '-q',
        type=int,
        default=10,
        help='number of blocks for buffering(>0) (default: %(default)s)'
    )
    parser.add_argument(
        '--output-file', '-O',
        type=str,
        nargs='?',
        help='file that you want to record data'
    )
    return parser


if __name__ == '__main__':

    PARSER = argparse.ArgumentParser()
    add_arg_for_player(PARSER)
