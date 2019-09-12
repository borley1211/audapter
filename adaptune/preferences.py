#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import pathlib
import sys
from asyncio import get_event_loop, create_task
from asyncio import sleep as asleep
from typing import Dict, List, Tuple, Union

import commentjson
from prompt_toolkit import Application, print_formatted_text, prompt
from prompt_toolkit.completion import PathCompleter
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.filters import Condition, IsDone
from prompt_toolkit.formatted_text import to_formatted_text
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import (ConditionalContainer, D,
                                   DummyControl, FormattedTextControl, HSplit,
                                   Layout, ScrollOffsets, Window)
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import yes_no_dialog
from prompt_toolkit.styles import (pygments_token_to_classname,
                                   style_from_pygments_dict)
from prompt_toolkit.validation import ValidationError, Validator
from pygments.token import Token
from pygments.lexers.python import Python3Lexer
from yaspin import yaspin
from yaspin.termcolor import colored

with yaspin(text=colored(
    "Preparing. Wait a minute...",
    color="cyan", attrs=["bold"]
)):
    import sounddevice as sd

# Measure for RecursionError
sys.setrecursionlimit(2000)


class InquirerControl(FormattedTextControl):
    selected_option_index = 0
    answered = False

    def __init__(self, branches, **kwargs):
        self.branches = branches
        super(
            InquirerControl,
            self).__init__(
            self._get_choiced_tokens,
            **kwargs)

    @property
    def choice_count(self):
        return len(self.branches)

    def _get_choiced_tokens(self) -> List:
        tokens = []
        T = Token

        def _append(index, label):
            nonlocal self
            selected = index == self.selected_option_index

            def _select_item(app, mouse_event):
                self.selected_option_index = index
                self.answered = True

            _ = T.Selected if selected else T
            tokens.append(
                (T.Selected if selected else T,
                    " > " if selected else "   ")
            )
            if selected:
                tokens.append(
                    (Token.SetCursorPosition, "")
                )
            tokens.append(
                (T.Selected if selected else T, "%-24s" %
                 label, _select_item)
            )
            tokens.append((T, "\n"))

        for i, choice in enumerate(self.branches):
            _append(i, choice)

        tokens.pop()

        return [
            ("class:" + pygments_token_to_classname(x[0]),
             str(x[1])) for x in tokens
        ]

    def get_selection(self):
        key = self.branches[self.selected_option_index]
        return key


class Preferences(object):
    finished = False
    want_to_continue = True

    kb = KeyBindings()
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
    branches: List = []
    hs_container = DummyControl()
    current_node = None

    loop = get_event_loop()

    def __init__(
        self,
        include_default_pygments_style=True,
        style_transformation=None, clipboard=None, full_screen=False,
        color_depth=None, mouse_support=False,
        enable_page_navigation_bindings=None, paste_mode=False,
        editing_mode=EditingMode.VI, erase_when_done=False,
        reverse_vi_search_direction=False, min_redraw_interval=0.1,
        max_render_postpone_time=0, on_reset=None, on_invalidate=None,
        before_render=None, after_render=None,
        input_method=None, output_method=None
    ):
        self.confdict, _choices = self._get_conf("config.json")
        self.attributes, self.branches = self._get_conf(
            ".attributes.json")

        self._conf_kb()

        self.ic = InquirerControl(self.branches)
        self._set_layout()

        self.app = Application(
            layout=self.layout,
            style=self.inquirer_style,
            include_default_pygments_style=include_default_pygments_style,
            style_transformation=style_transformation,
            key_bindings=self.kb,
            clipboard=clipboard,
            full_screen=full_screen,
            color_depth=color_depth,
            mouse_support=mouse_support,
            enable_page_navigation_bindings=enable_page_navigation_bindings,
            paste_mode=paste_mode,
            editing_mode=editing_mode,
            erase_when_done=erase_when_done,
            reverse_vi_search_direction=reverse_vi_search_direction,
            min_redraw_interval=min_redraw_interval,
            max_render_postpone_time=max_render_postpone_time,
            on_reset=on_reset,
            on_invalidate=on_invalidate,
            before_render=before_render,
            after_render=after_render,
            input=input_method,
            output=output_method)

    def _set_app(self,
                 include_default_pygments_style,
                 style_transformation, clipboard, full_screen,
                 color_depth, mouse_support,
                 enable_page_navigation_bindings, paste_mode,
                 editing_mode, erase_when_done,
                 reverse_vi_search_direction, min_redraw_interval,
                 max_render_postpone_time, on_reset, on_invalidate,
                 before_render, after_render,
                 input_method, output_method
                 ):
        self._set_layout()
        self.app = Application(
            layout=self.layout,
            style=self.inquirer_style,
            key_bindings=self.kb)

    def _conf_kb(self):
        kb = self.kb

        @kb.add("c-q", eager=True)
        @kb.add("c-c", eager=True)
        def _interrupt(event):
            event.app.exit(None)

        @kb.add("down", eager=True)
        def move_cursor_down(event):
            self.ic.selected_option_index = (
                self.ic.selected_option_index + 1) % self.ic.choice_count

        @kb.add("up", eager=True)
        def move_cursor_up(event):
            self.ic.selected_option_index = (
                self.ic.selected_option_index - 1) % self.ic.choice_count

        @kb.add(
            "enter",
            eager=True,
            filter=~Condition(lambda: self.finished))
        def set_value(event):
            nonlocal self
            self.ic.answered = True
            event.app.invalidate()

        @kb.add(
            "enter",
            eager=True,
            filter=Condition(lambda: self.finished))
        def _exit(event):
            self.ic = InquirerControl([""])
            self.reset()
            self._set_layout()
            event.app.exit(None)

        self.kb = kb

    def _set_layout(self, additional=Window(DummyControl())):
        self._conf_hs_container(additional)
        self.layout = Layout(self.hs_container)

    def _conf_hs_container(self, additional=Window(DummyControl())):
        self.hs_container = HSplit(
            [
                Window(
                    height=D.exact(1),
                    content=FormattedTextControl(
                        self.get_prompt_tokens
                    )
                ),
                ConditionalContainer(
                    Window(
                        self.ic,
                        width=D.exact(43),
                        height=D(min=3),
                        scroll_offsets=ScrollOffsets(top=1, bottom=1),
                    ),
                    filter=~IsDone() | ~Condition(lambda: self.finished),
                ),
                additional
            ]
        )

    def _get_conf(
            self, configobj: Union[str, Dict, List]) -> Tuple[Dict, List]:
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

        return [("class:" + pygments_token_to_classname(x[0]), str(x[1]))
                for x in tokens]

    def select_item(self, key, attributes):

        def get_ic_child(key, attributes):
            if isinstance(attributes, dict):
                attr_child = attributes[key]

                if isinstance(attr_child, dict):
                    self.attributes, self.branches = (
                        attr_child, list(attr_child.keys()))
                elif isinstance(attr_child, list):
                    self.attributes = self.branches = attr_child
            else:
                pass

            return InquirerControl(self.branches)

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

                    self.ic = InquirerControl([""])
                    self.reset()
                    self._set_layout()
                    res = None

                    async def interactive_shell():
                        nonlocal res
                        res = await prompt(
                            notice,
                            validator=Validator.from_callable(_validfunc),
                            lexer=PygmentsLexer(Python3Lexer),
                            async_=True
                        )
                        return

                    self.loop.create_task(interactive_shell())

                # else(=="this branch has some branches"):
                # special case in "device"
                elif key in ["main", "monitor", "input"]:
                    snddevs = list(sd.query_devices())
                    devlist = [devinfo["name"] for devinfo in snddevs]
                    self.ic = InquirerControl(devlist)
                    self.current_node = key
                    self.attributes = []

                    _additional = Window(
                        height=D(min=3),
                        content=FormattedTextControl(
                            to_formatted_text(
                                sd.query_devices(),
                                auto_convert=True)
                        )
                    )
                    self._set_layout(additional=_additional)
                    res = False

                elif str(self.current_node) in ["main", "monitor", "input"]:
                    res = key

                # other cases
                else:
                    self.ic = get_ic_child(key, attr)
                    self.current_node = key
                    self._set_layout()
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

    async def operate_loop(self):
        while not self.finished:
            await asleep(0.01)

    def main(self):
        want_to_save = True

        while self.want_to_continue:
            self.app.run()

            want_to_save = yes_no_dialog(
                title="",
                text="Do you want to (over)write the configuration file?\n[Press ENTER to decide]")
            if want_to_save:
                with open(
                    os.path.join(os.path.dirname(__file__), "config.json"),
                    'w',
                    encoding='UTF-8'
                ) as file:
                    commentjson.dump(self.confdict, file, indent=4)

            self.want_to_continue = yes_no_dialog(
                title="",
                text="Do you want to configure more params?\n[Press ENTER to decide]")

        print_formatted_text("Done!")
