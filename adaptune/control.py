#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pygments.token import Token
from prompt_toolkit.styles.pygments import style_from_pygments_dict
from prompt_toolkit.styles import pygments_token_to_classname
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.dimension import LayoutDimension as D
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.layout.containers import ScrollOffsets
from prompt_toolkit.layout.containers import ConditionalContainer
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.filters import IsDone
from prompt_toolkit.application import Application
from prompt_toolkit.shortcuts import yes_no_dialog
from typing import Tuple, Union, Any
import alsaaudio as alsa
from padasip import padasip as pa
import os
import commentjson


def _get_conf(configobj: Union[str, dict]) -> Tuple[Any, list]:
    if isinstance(configobj, str):
        with open(
            os.path.join(os.path.dirname(__file__), str(configobj)), 'r', encoding='UTF-8'
        ) as file:
            config = commentjson.load(file)
    elif isinstance(configobj, dict):
        config = configobj
    else:
        return configobj, []
    keylist = list(config.keys())
    keylist = [key for key in keylist if key != '__description__']
    return config, keylist


confdict, _ = _get_conf("config.json")

finished = False
want_to_continue = False


kb = KeyBindings()


inquirer_style = style_from_pygments_dict(
    {
        Token.QuestionMark: "#5F819D",
        Token.Selected: "#FF9D00",
        Token.Instruction: "",
        Token.Answer: "#FF9D00 bold",
        Token.Question: "bold",
    }
)


class InquirerControl(FormattedTextControl):
    selected_option_index = 0
    answered = False

    def __init__(self, config, choices, **kwargs):
        self.choices = choices
        self.availables = config
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

        def append(index, label):
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
                tokens.append((Token.SetCursorPosition, ""))
            tokens.append(
                (T.Selected if selected else T, "%-24s" %
                    label, select_item)
            )
            tokens.append((T, "\n"))

        for i, choice in enumerate(self.choices):
            append(i, choice)
        tokens.pop()
        return [
            ("class:" + pygments_token_to_classname(x[0]), str(x[1])) for x in tokens
        ]

    def get_selection(self):
        key = self.choices[self.selected_option_index]
        return key, self.availables


ic_init = InquirerControl(*_get_conf(".availables.json"))
ic = ic_init


def select_item(key, availables):
    global ic

    def get_ic_child(key, availables):
        av_child = availables[key]
        return InquirerControl(*_get_conf(av_child))

    def guess():
        global want_to_continue, ic, finished
        want_to_continue = yes_no_dialog(
            title="Dialog",
            text="Do you want to configure other params?",
            style=inquirer_style
        )
        if want_to_continue:
            ic = ic_init
        else:
            finished = True

    def conf_hw_params(key, availables):
        global ic

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

        funcs = {
            "rate": conf_rate,
            "formatname": conf_format,
            "periodsize": conf_periodsize,
            "channels": conf_channels
        }

        ic = get_ic_child(key, availables)
        task = funcs[key]
        return task

    def conf_filter_params(key, availables):
        global ic

        def conf_mu(key, choices):
            print(__name__)
            guess()

        def conf_w_init(key, choices):
            print(__name__)
            guess()

        funcs = {
            "mu": conf_mu,
            "w": conf_w_init
        }

        ic = get_ic_child(key, availables)
        task = funcs[key]
        return task

    def conf_domain(key, availables):
        print(__name__)
        guess()

    def conf_algo(key, availables):
        print(__name__)
        guess()

    def select_device(key, availables):
        global ic

        def set_main(key):
            print(__name__)
            guess()

        def set_monitor(key):
            print(__name__)
            guess()

        def set_input(key):
            print(__name__)
            guess()

        funcs = {
            "main": set_main,
            "monitor": set_monitor,
            "input": set_input
        }

        ic = get_ic_child(key, availables)
        task = funcs[key]
        return task

    conffuncs = {
        "hw_params": conf_hw_params,
        "filter_params": conf_filter_params,
        "filter_domain": conf_domain,
        "filter_algo": conf_algo,
        "devices": select_device
    }

    ic = get_ic_child(key, availables)
    task = conffuncs[key]
    return task


task_func = select_item


def get_prompt_tokens():
    global ic, layout, task_func
    tokens = []
    tokens.append((Token.QuestionMark, "?"))
    tokens.append((Token.Question, " Configure about: "))
    if ic.answered:
        selected, _ = ic.get_selection()
        tokens.append((Token.Answer, " " + selected))
        tokens.append((Token, "\n"))
        task_child = task_func(*ic.get_selection())
        new_hsc = init_hs_container()
        layout = Layout(new_hsc)
        if task_child:
            task_func = task_child
    else:
        tokens.append((Token.Instruction, " (Use arrow keys)"))
    return [("class:" + pygments_token_to_classname(x[0]), str(x[1]))
            for x in tokens]


def init_hs_container():
    hsc = HSplit(
        [
            Window(
                height=D.exact(1),
                content=FormattedTextControl(
                    text=get_prompt_tokens)
            ),
            ConditionalContainer(
                Window(
                    ic,
                    width=D.exact(43),
                    height=D(min=3),
                    scroll_offsets=ScrollOffsets(top=1, bottom=1),
                ),
                filter=~IsDone(),
            ),
        ]
    )
    return hsc


HSContainer = init_hs_container()
layout = Layout(HSContainer)


@kb.add("c-q", eager=True)
@kb.add("c-c", eager=True)
def _interrupt(event):
    event.app.exit(None)


@kb.add("down", eager=True)
def move_cursor_down(event):
    ic.selected_option_index = (ic.selected_option_index + 1) % ic.choice_count


@kb.add("up", eager=True)
def move_cursor_up(event):
    ic.selected_option_index = (ic.selected_option_index - 1) % ic.choice_count


@kb.add("enter", eager=True)
def set_value(event):
    global ic
    ic.answered = True
    if not want_to_continue and finished:
        event.app.exit(None)


app = Application(
    layout=layout, key_bindings=kb, mouse_support=False, style=inquirer_style
)
app.run()
