from dataclasses import dataclass

from environs import Env


@dataclass
class Site:
    postgres: str


@dataclass
class JwtAuth:
    secret_key: str
    algorithm: str


@dataclass
class Config:
    site: Site
    jwt_auth: JwtAuth


def load_config():
    env = Env()
    env.read_env()
    return Config(
        site=Site(env('DB_POSTGRES')),
        jwt_auth=JwtAuth(
            secret_key=env('SECRET_KEY_JWT'),
            algorithm=env("ALGORYTHM_JWT")
        )
    )
