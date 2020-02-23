from typer import Typer

from ..command import config, run

app = Typer()

app.command(config)

if __name__ == "__main__":
    app()
