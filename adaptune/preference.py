#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
from typing import Any, Tuple, Union, Dict, List

import alsaaudio as alsa
import commentjson
import numpy as np
import sounddevice as sd
from padasip import padasip as pa
from prompt_toolkit import Application, print_formatted_text, prompt
from prompt_toolkit.application import get_app
from prompt_toolkit.completion import PathCompleter
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.filters import Condition, IsDone
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import (ConditionalContainer, D,
                                   FormattedTextControl, HSplit, Layout,
                                   ScrollOffsets, Window)
from prompt_toolkit.shortcuts import yes_no_dialog
from prompt_toolkit.styles import (pygments_token_to_classname,
                                   style_from_pygments_dict)
from prompt_toolkit.validation import ValidationError, Validator
from pygments.token import Token

# Measure for RecursionError
sys.setrecursionlimit(10 ** 4)


class InquirerControl(FormattedTextControl):
    selected_option_index = 0
    answered = False

    def __init__(self, choices, **kwargs):
        self.choices = choices
        super(
            InquirerControl,
            self).__init__(
            self._get_choiced_tokens,
            **kwargs)

    @property
    def choice_count(self):
        return len(self.choices)

    def _get_choiced_tokens(self):
        tokens = []
        T = Token

        def _append(index, label):
            selected = index == self.selected_option_index

            def select_item(app, mouse_event):
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
                (T.Selected if selected else T,
                 "%-24s" % label,
                 select_item)
            )
            tokens.append((T, "\n"))

        for i, choice in enumerate(self.choices):
            _append(i, choice)

        tokens.pop()

        return [
            ("class:" + pygments_token_to_classname(x[0]),
             str(x[1])) for x in tokens
        ]

    def get_selection(self):
        key = self.choices[self.selected_option_index]
        return key


class ConfigurationApp(Application):
    want_to_continue = False
    finished = False
    kb = KeyBindings()
    breadcrumb = ""
    tasks = None
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

    def __init__(
        self,
        include_default_pygments_style=True,
        style_transformation=None,
        clipboard=None,
        full_screen=False,
        color_depth=None,
        mouse_support=False,
        enable_page_navigation_bindings=None,
        paste_mode=False,
        editing_mode=EditingMode.VI,
        erase_when_done=False,
        reverse_vi_search_direction=False,
        min_redraw_interval=None,
        max_render_postpone_time=0,
        on_reset=None,
        on_invalidate=None,
        before_render=None,
        after_render=None,
        input_method=None,
        output_method=None
    ):
        self.confdict, _ = self._get_conf("config.json")
        self.attributes, self.choices_init = self._get_conf(".attributes.json")
        self.choices = self.choices_init

        self._conf_kb()

        self.ic_init = InquirerControl(self.choices)
        self.ic = self.ic_init

        self._set_layout()

        super().__init__(
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

    def _get_conf(self, configobj: Union[str, Dict, List]) -> Tuple[Dict, List]:
        _config: Dict = dict()
        keylist: List = []

        def _eval_values(dictionary: Dict) -> Dict:
            newd = {}

            for key, val in dictionary.items():
                print_formatted_text(val)

                if isinstance(val, dict):
                    val = _eval_values(val)     # process recursively
                else:
                    pass

                if key == "type" or "section":
                    newd[key] = eval(str(val))
                elif newd[key] == "(/path/to/file)":
                    newd[key] = {
                        "name": newd[key],
                        "method": PathCompleter()
                    }
                else:
                    newd[key] = val

            return newd

        if isinstance(configobj, str):
            with open(
                os.path.join(os.path.dirname(__file__), configobj),
                'r',
                encoding='UTF-8'
            ) as file:
                _config = commentjson.load(file)
        elif isinstance(configobj, dict):
            _config = configobj
            keylist = list(_config.keys())
        elif isinstance(configobj, list):
            keylist = configobj
        else:
            pass

        config = _config

        if isinstance(config, dict):
            keylist = [key for key in keylist if key != '__description__']

        if isinstance(_config, dict):
            config = _eval_values(config)

        return config, keylist

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

        @kb.add("enter", eager=True)
        def set_value(event):
            self.ic.answered = True
            if not self.want_to_continue and self.finished:
                event.app.exit(None)
            else:
                self._set_layout()

        self.kb = kb

    def _set_layout(self):
        self._conf_hs_container()
        self.layout = Layout(self.hs_container)

    def _conf_hs_container(self):
        self.hs_container = HSplit(
            [
                Window(
                    height=D.exact(1),
                    content=FormattedTextControl(
                        self.get_prompt_tokens()
                    )
                ),
                ConditionalContainer(
                    Window(
                        self.ic,
                        width=D.exact(43),
                        height=D(min=3),
                        scroll_offsets=ScrollOffsets(top=1, bottom=1),
                    ),
                    filter=~IsDone(),
                ),
            ]
        )

    def get_prompt_tokens(self):
        tokens = []
        tokens.append((Token.QuestionMark, "?"))
        tokens.append((Token.Question, " Configure about: "))
        if self.ic.answered:
            selected = self.ic.get_selection()
            if self.breadcrumb:
                self.breadcrumb += " >"
                tokens.append((Token.Breadcrumb, self.breadcrumb))
            tokens.append((Token.Answer, " " + selected))
            tokens.append((Token, "\n"))
            self.breadcrumb += " " + selected
            self.select_item(selected, self.attributes)
        else:
            tokens.append((Token.Instruction, " (Use arrow keys)"))
        return [("class:" + pygments_token_to_classname(x[0]), str(x[1]))
                for x in tokens]

    def select_item(self, key, attributes):

        def get_ic_child(key, attributes):
            attr_child = attributes[key]
            self.attributes, self.choices = self._get_conf(attr_child)
            return InquirerControl(self.choices)

        def guess():
            self.want_to_continue = yes_no_dialog(
                title="Dialog",
                text="Do you want to configure other params?",
                style=self.inquirer_style
            )
            if self.want_to_continue:
                self.ic = self.ic_init
            else:
                self.finished = True

        def conf_hw_params(key, attributes):

            def conf_rate(key, choices):
                print(__name__)
                guess()

            def conf_format(key, choices):
                print(__name__)
                guess()

            def conf_periodsize(key, choices):
                print(__name__)
                guess()

            def conf_channels(key, choices):
                print(__name__)
                guess()

            cfuncdict = {
                "rate": conf_rate,
                "formatname": conf_format,
                "periodsize": conf_periodsize,
                "channels": conf_channels
            }

            if self.tasks is cfuncdict:
                self.tasks[self.current_choice](
                    key,
                    attributes)
            else:
                self.ic = get_ic_child(key, attributes)
                self.current_choice = key
                self.tasks = cfuncdict

        def conf_filter_params(key, attributes):

            def conf_mu(key, choices):
                print(__name__)
                guess()

            def conf_w_init(key, choices):
                print(__name__)
                guess()

            cfuncdict = {
                "mu": conf_mu,
                "w": conf_w_init
            }

            if self.tasks is cfuncdict:
                self.tasks[self.current_choice](
                    key,
                    attributes)
            else:
                self.ic = get_ic_child(key, attributes)
                self.current_choice = key
                self.tasks = cfuncdict

        def conf_domain(key, attributes):
            print(__name__)
            guess()

        def conf_algo(key, attributes):
            print(__name__)
            guess()

        def select_device(key, attributes):

            def set_main(key):
                print(__name__)
                guess()

            def set_monitor(key):
                print(__name__)
                guess()

            def set_input(key):
                print(__name__)
                guess()

            cfuncdict = {
                "main": set_main,
                "monitor": set_monitor,
                "input": set_input
            }

            if self.tasks is cfuncdict:
                self.tasks[self.current_choice](
                    key,
                    attributes)
            else:
                self.ic = get_ic_child(key, attributes)
                self.current_choice = key
                self.tasks = cfuncdict

        funcdict = {
            "hw_params": conf_hw_params,
            "filter_params": conf_filter_params,
            "filter_domain": conf_domain,
            "filter_algo": conf_algo,
            "devices": select_device
        }

        if self.tasks is funcdict:
            self.tasks[self.current_choice](
                key,
                attributes)
        else:
            self.ic = get_ic_child(key, attributes)
            self.current_choice = key
            self.tasks = funcdict


if __name__ == "__main__":
    app = ConfigurationApp()
    app.run()
