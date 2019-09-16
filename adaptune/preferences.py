#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from collections import OrderedDict, defaultdict
import pathlib
from asyncio import get_event_loop, create_task, ensure_future, Task
from asyncio import sleep as asleep
from typing import Dict, List, Tuple, Union, DefaultDict
import commentjson

from prompt_toolkit import print_formatted_text, prompt
from prompt_toolkit.completion import PathCompleter
from prompt_toolkit.eventloop import generator_to_async_generator, use_asyncio_event_loop
from prompt_toolkit.eventloop.context import wrap_in_current_context
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.shortcuts import input_dialog, radiolist_dialog, yes_no_dialog
from prompt_toolkit.styles import pygments_token_to_classname, style_from_pygments_dict
from prompt_toolkit.validation import ValidationError, Validator
from pygments.lexers.python import Python3Lexer
from pygments.token import Token, _TokenType
from yaspin import yaspin
from yaspin.termcolor import colored

with yaspin(text=colored(
    "Preparing. Wait a minute...",
    color="cyan", attrs=["bold"]
)):
    import sounddevice as sd

use_asyncio_event_loop()


KeyType = Union[str, int, float]
PathStr = str


class PreferenceApp(object):

    breadcrumb = ""
    inquirer_style = style_from_pygments_dict(
        {
            Token.QuestionMark: "#5F819D",
            Token.Selected: "#FF9D00",
            Token.Instruction: "",
            Token.Answer: "#FF9D00 bold",
            Token.Question: "bold",
            Token.Breadcrumb: "#eeeeee",
        }
    )
    
    confdict: Dict = {}
    attributes: Dict = {}
    attr_header: List = []
    
    root: List[KeyType] = []
    nodes: List[KeyType] = []

    tasks: List[Task] = []
    eventdict: DefaultDict[str, List[Task]] = defaultdict(list)

    def __init__(self):
        pass

    def load_config(self):
        self.confdict, _choices = self._get_conf("config.json")
        self.attr_header, self.root = self._get_conf(
            ".attributes.json")
    
    def set_header(self):
        self.attributes = self.attr_header
        self.nodes = self.root

    def _get_conf(
            self, configobj: Union[
                str, Dict, List]) -> Tuple[Dict, List]:
        _config: Dict = dict()
        keylist: List = []

        def _eval_values(dictionary: Dict) -> Dict:
            newd = {}

            for key, val in dictionary.items():

                if isinstance(val, dict):
                    val = _eval_values(val)     # process recursively
                else:
                    pass

                if key == "type":
                    newd[key] = eval(val)
                elif key == "section":
                    newval = None
                    exec("newval = {}".format(val))
                    newd.update(section=newval)
                else:
                    newd[key] = val

            return newd

        if isinstance(configobj, str):
            with open(
                os.path.join(os.path.dirname(__file__), str(configobj)),
                'r',
                encoding='UTF-8'
            ) as file:
                _config = commentjson.load(file)
        elif isinstance(configobj, dict):
            _config = configobj
        elif isinstance(configobj, list):
            keylist = configobj
        else:
            pass

        config = _config

        if isinstance(config, dict):
            keylist = list(config.keys())
            keylist = [key for key in keylist if key != '__description__']
            config = _eval_values(config)

        return config, keylist
