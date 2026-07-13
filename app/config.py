import os
from functools import cached_property
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    bot_token: str = Field(default="", validation_alias="BOT_TOKEN")
    admin_telegram_ids: str = Field(default="", validation_alias="ADMIN_TELEGRAM_IDS")
    manager_url: str = Field(default="", validation_alias="MANAGER_URL")
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/bot.db",
        validation_alias="DATABASE_URL"
    )
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")

    @cached_property
    def admin_ids(self) -> list[int]:
        if not self.admin_telegram_ids:
            return []
        try:
            return [int(id.strip()) for id in self.admin_telegram_ids.split(",") if id.strip()]
        except ValueError:
            raise ValueError(
                "Некорректный формат ADMIN_TELEGRAM_IDS. "
                "Укажите ID через запятую без пробелов: 123456789,987654321"
            )

    def validate(self) -> None:
        if not self.bot_token:
            raise ValueError("BOT_TOKEN не задан. Добавьте токен Telegram-бота в переменные окружения.")


def get_settings() -> Settings:
    return Settings()


settings = get_settings()
