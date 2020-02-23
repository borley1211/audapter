from dynaconf import LazySettings, settings

__all__ = ["load_settings"]


# default values
CONFPATH = settings.get("CONFPATH")


def load_settings(confpath: str = CONFPATH):
    settings_local = LazySettings(INCLUDES_FOR_DYNACONF=str(CONFPATH))
    return settings_local
