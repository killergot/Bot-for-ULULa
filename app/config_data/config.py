from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str
    ID_admin: int

@dataclass
class DB:
    name: str
    host: str
    user: str
    password: str


@dataclass
class Config:
    database: DB
    tg_bot: TgBot


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('BOT_TOKEN'),
                               ID_admin=int(env('ID_ADMIN'))),
                  database=DB(name=env('DB_NAME'),
                              host=env('DB_HOST'),
                              user=env('DB_USER'),
                              password=str(env('DB_PASS')))
                  )

