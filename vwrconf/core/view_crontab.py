# vwrconf/core/view_crontab.py

from vwrconf.models.config_model import Config
from vwrconf.models.Crontab.Crontab import Crontab

def fetch_all_crontabs(config: Config) -> dict[str, list[str]]:
    return Crontab(config).fetch()
