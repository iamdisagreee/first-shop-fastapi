from dataclasses import dataclass

from environs import Env


@dataclass
class Site:
    postgres: str


@dataclass
class Config:
    site: Site

def load_config():
    env = Env()
    env.read_env()
    return Config(site=Site(env('DB_POSTGRES')))