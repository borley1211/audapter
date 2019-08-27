from typing import Tuple
import alsaaudio as alsa
from padasip import padasip as pa
import os
import commentjson


with open(
    os.path.join(os.path.dirname(__file__), "params.json"), 'r', encoding='UTF-8'
) as file:
    config = commentjson.load(file)

params = config["params"]
params["formatname"] = eval("alsa.PCM_FORMAT_" + params["formatname"])

filter_params = config["filter_params"]

domain = config["filter_domain"]

default_filter = eval("pa.filters.Filter" + config["filter_algo"])

dev = config["devices"]


def dump_defaults(
    puts: bool = True, description: bool = False
) -> Tuple[str, dict]:
    """
    'params.json' に設定された既定値を出力します。

    Args:
        puts (bool, optional): 標準出力に既定値を出力するかどうか。 デフォルトは True です。
        description (bool, optional): 冒頭の説明文を出力に含めるかどうか。デフォルトは False です。

    Returns:
        Tuple[str, dict]: 文字列型、辞書型の既定値を tuple として返します。
    """
    if description is False:
        del config["__description__"]
    if puts:
        print(commentjson.dumps(config, indent=4))
    return commentjson.dumps(config), config


if __name__ == '__main__':
    dump_defaults(description=True)
