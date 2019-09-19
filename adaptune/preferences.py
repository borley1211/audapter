#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import pathlib
from asyncio import Task, create_task, ensure_future, get_event_loop
from asyncio import sleep as asleep
from collections import OrderedDict, defaultdict
from typing import Coroutine, DefaultDict, Dict, List, Tuple, Union

import commentjson
from prompt_toolkit import print_formatted_text, prompt
from prompt_toolkit.completion import PathCompleter
from prompt_toolkit.eventloop import (
    generator_to_async_generator,
    use_asyncio_event_loop)
from prompt_toolkit.eventloop.context import wrap_in_current_context
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.shortcuts import (
    input_dialog, radiolist_dialog,
    yes_no_dialog)
from prompt_toolkit.styles import (
    pygments_token_to_classname,
    style_from_pygments_dict)
from prompt_toolkit.validation import ValidationError, Validator
from prompt_toolkit.widgets import RadioList, MenuContainer, FormattedTextToolbar, ValidationToolbar, Dialog
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


class RadioListDialog(Dialog):
    
    def __init__(self,
                 body, title='', buttons=None, modal=True,
                 width=None, with_background=False):
        super().__init__(body, title=title, buttons=buttons, modal=modal, width=width, with_background=with_background)


class PreferenceApp(object):
    all_done = False

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

    attr_header: List = []
    root: List[KeyType] = []

    attributes: Dict = {}
    nodes: List[KeyType] = []

    current_node: KeyType

    tasks: List[Task] = []
    eventdict: DefaultDict[str, List[Task]] = defaultdict(list)

    def __init__(self):
        self.load_config()
        self.set_header()

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

    def get_prompt_tokens(self):
        tokens = []
        tokens.append((Token.QuestionMark, "?"))
        tokens.append((Token.Question, " Configure about: "))

        if self.ic.answered:
            selected = self.ic.get_selection()

            if self.breadcrumb:
                self.breadcrumb += " >"
                tokens.append((Token.Breadcrumb, self.breadcrumb))
            tokens.append((Token.Answer, " " + str(selected)))
            tokens.append((Token, "\n"))
            self.breadcrumb += " " + str(selected)
            self.select_item(selected, self.attributes)
            self.invalidate()
        else:
            if self.breadcrumb:
                tokens.append((Token.Breadcrumb, self.breadcrumb))
            tokens.append((Token.Instruction, " (Use arrow keys)"))

        return [("class:" + pygments_token_to_classname(x[0]),
                 str(x[1])) for x in tokens]

    def select_item(self, key, attributes):

        def get_child_node(key, attributes):
            attr_child = attributes[key]

            if isinstance(attr_child, dict):
                self.attributes, self.nodes = (
                    attr_child, list(attr_child.keys()))
            elif isinstance(attr_child, list):
                self.attributes = attr_child
                self.branches = attr_child

        def _work_before_node(key, attr):
            nonlocal self

            if isinstance(attr, dict):
                # if "this branch has only nodes":
                attr_child = attr[key]
                if set(attr_child) >= {'type', 'section'}:
                    notice = "Enter {}".format(attr_child["type"])
                    notice += " as {}".format(attr_child["section"])

                    def _validfunc(inputs):
                        nonlocal attr_child
                        if not attr_child["section"](inputs):
                            raise ValidationError(
                                message="This input does not meet the requirements as {}".format(
                                    attr["section"])
                            )
                        elif not isinstance(inputs, attr_child["type"]):
                            raise ValidationError(
                                message="This input does not contain the type as {}".format(
                                    attr["type"])
                            )
                        else:
                            return inputs

                    notice += ":"

                    self.current_node = key
                    self.attributes = []

                    res = None

                # else(=="this branch has some branches"):
                # special case in "device"
                elif key in ["main", "monitor", "input"]:
                    snddevs = list(sd.query_devices())
                    devlist = [devinfo["name"] for devinfo in snddevs]
                    self.current_node = key
                    self.attributes = []

                    res = False

                elif str(self.current_node) in [
                        "main", "monitor", "input"]:
                    res = key

                # other cases
                else:
                    get_child_node(key, attr)
                    self.current_node = key
                    res = False

            elif isinstance(attr, list):
                res = key

            return res

        def _setval_if_key_is_node(key_prev, selected):
            nonlocal self

            # hw_params
            if key_prev in ["rate", "periodsize", "channels"]:
                self.confdict["hw_params"][key_prev] = selected
            elif key_prev in ["alsa", "sounddevice"]:
                self.confdict["hw_params"]["formatname"] = selected

            # filter_params
            elif key_prev in ["mu", "w"]:
                self.confdict["filter_params"][key_prev] = selected

            # (as below)
            elif key_prev in ["filter_domain", "filter_algo"]:
                self.confdict[key_prev] = selected

            # devices
            elif key_prev in ["main", "monitor", "input"]:
                self.confdict["devices"][key_prev] = selected

            # [post process]
            self.current_node = str(selected)
            self.finished = True

        result = _work_before_node(key, attributes)
        if result:
            key_prev = self.current_node
            _setval_if_key_is_node(key_prev, result)

    def _create_selection_event(self):
        self.tasks.append(create_task())

    def _create_input_event(self):
        pass

    def _create_print_event(self):
        pass

    async def _event_loop(
            self, task: Task, interval: Union[int, float] = 1):
        pass

    async def async_run(self, coro: Coroutine):
        pass

    def main(self):
        pass
