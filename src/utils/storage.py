"""
Feather Agent — удобное и расширяемое хранилище в AppData.

Базовый путь: %APPDATA%/FeatherAgent/ (Windows)
              ~/.local/share/FeatherAgent/ (Linux/Mac)

Структура:
  FeatherAgent/
  ├── chats/        # История чатов (chat_id.json)
  ├── config/       # Настройки приложения (settings.json)
  ├── models/       # Конфиги моделей (model_id.json)
  └── ...           # Всё что угодно — методом save/load

Использование:
    from src.utils.storage import appdata

    # Глобальный синглтон
    appdata.save_json("my_data.json", {...})
    data = appdata.load_json("my_data.json", default=[])

    # Чаты
    appdata.chats.save("chat_1", history_list)
    appdata.chats.get("chat_1")

    # Конфиг
    appdata.config.set("theme", "dark")
    appdata.config.get("theme")

    # Модели
    appdata.models.save("gpt4", {...})
    appdata.models.list
"""

import json
import os
import shutil
from pathlib import Path
from typing import Any, Optional


class AppData:
    """Удобный и расширяемый интерфейс для хранения данных в AppData."""

    def __init__(self, app_name: str = "FeatherAgent"):
        # Определяем базовую папку: Windows → %APPDATA%, иначе ~/.local/share
        if os.name == "nt":
            base_path = Path(os.environ["APPDATA"])
        else:
            base_path = Path.home() / ".local" / "share"

        self._base = base_path / app_name
        self._base.mkdir(parents=True, exist_ok=True)

        # Pre-create стандартные подпапки
        self._chats_dir = self._base / "chats"
        self._chats_dir.mkdir(exist_ok=True)

        self._models_dir = self._base / "models"
        self._models_dir.mkdir(exist_ok=True)

        self._config_dir = self._base / "config"
        self._config_dir.mkdir(exist_ok=True)

    # ──────────────────────────────────────────────
    #  Свойства
    # ──────────────────────────────────────────────

    @property
    def base(self) -> Path:
        """Корневая папка AppData."""
        return self._base

    # ──────────────────────────────────────────────
    #  Универсальные методы (save/load куда угодно)
    # ──────────────────────────────────────────────

    def save_json(self, path: str | Path, data: Any) -> None:
        """Сохранить JSON-данные в файл внутри AppData.

        Пример:
            appdata.save_json("config/settings.json", {"theme": "dark"})
            appdata.save_json("chats/my_chat.json", [...])
        """
        full_path = self._resolve(path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_json(self, path: str | Path, default: Any = None) -> Any:
        """Загрузить JSON из файла внутри AppData.

        Если файла нет — вернёт default.
        """
        full_path = self._resolve(path)
        if not full_path.exists():
            return default
        with open(full_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def delete(self, path: str | Path) -> bool:
        """Удалить файл или папку внутри AppData. True — если удалено."""
        full_path = self._resolve(path)
        if not full_path.exists():
            return False
        if full_path.is_dir():
            shutil.rmtree(full_path)
        else:
            full_path.unlink()
        return True

    def exists(self, path: str | Path) -> bool:
        """Проверить, существует ли файл/папка внутри AppData."""
        return self._resolve(path).exists()

    def list_dir(self, path: str | Path = "") -> list[Path]:
        """Вернуть содержимое папки внутри AppData."""
        full_path = self._resolve(path)
        if not full_path.exists():
            return []
        return sorted(full_path.iterdir())

    # ──────────────────────────────────────────────
    #  Специализированные доступы
    # ──────────────────────────────────────────────

    @property
    def chats(self) -> "ChatsStorage":
        return ChatsStorage(self)

    @property
    def config(self) -> "ConfigStorage":
        return ConfigStorage(self)

    @property
    def models(self) -> "ModelsStorage":
        return ModelsStorage(self)

    # ──────────────────────────────────────────────
    #  Внутреннее
    # ──────────────────────────────────────────────

    def _resolve(self, path: str | Path) -> Path:
        """Превращает относительный путь в абсолютный внутри _base."""
        p = Path(path)
        if p.is_absolute():
            return p
        return self._base / p


# ──────────────────────────────────────────────
#  ChatsStorage — история чатов по ID
# ──────────────────────────────────────────────

class ChatsStorage:
    """Управление историей чатов."""

    def __init__(self, appdata: AppData):
        self._app = appdata
        self._dir = appdata._chats_dir

    @property
    def list(self) -> list[str]:
        """Список ID чатов (имена файлов без .json)."""
        return sorted(p.stem for p in self._dir.glob("*.json"))

    def get(self, chat_id: str, default: Optional[list] = None) -> list[dict]:
        """Загрузить историю чата по ID."""
        return self._app.load_json(f"chats/{chat_id}.json", default or [])

    def save(self, chat_id: str, history: list[dict]) -> None:
        """Сохранить историю чата по ID."""
        self._app.save_json(f"chats/{chat_id}.json", history)

    def delete(self, chat_id: str) -> bool:
        """Удалить чат."""
        return self._app.delete(f"chats/{chat_id}.json")

    def rename(self, old_id: str, new_id: str) -> bool:
        """Переименовать чат."""
        old_path = self._dir / f"{old_id}.json"
        new_path = self._dir / f"{new_id}.json"
        if not old_path.exists():
            return False
        old_path.rename(new_path)
        return True


# ──────────────────────────────────────────────
#  ConfigStorage — настройки приложения
# ──────────────────────────────────────────────

class ConfigStorage:
    """Управление настройками приложения (ключ-значение)."""

    def __init__(self, appdata: AppData):
        self._app = appdata
        self._file = "config/settings.json"

    def get(self, key: str, default: Any = None) -> Any:
        """Получить значение настройки по ключу."""
        config = self._app.load_json(self._file, {})
        return config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Установить значение настройки."""
        config = self._app.load_json(self._file, {})
        config[key] = value
        self._app.save_json(self._file, config)

    def all(self) -> dict:
        """Все настройки одним словарём."""
        return self._app.load_json(self._file, {})

    def reset(self) -> None:
        """Сбросить все настройки."""
        self._app.save_json(self._file, {})


# ──────────────────────────────────────────────
#  ModelsStorage — конфиги моделей
# ──────────────────────────────────────────────

class ModelsStorage:
    """Управление конфигурациями LLM-моделей."""

    def __init__(self, appdata: AppData):
        self._app = appdata
        self._dir = appdata._models_dir

    @property
    def list(self) -> list[str]:
        """Список ID доступных моделей."""
        return sorted(p.stem for p in self._dir.glob("*.json"))

    def get(self, model_id: str) -> Optional[dict]:
        """Загрузить конфиг модели."""
        return self._app.load_json(f"models/{model_id}.json")

    def save(self, model_id: str, config: dict) -> None:
        """Сохранить/обновить конфиг модели."""
        self._app.save_json(f"models/{model_id}.json", config)

    def delete(self, model_id: str) -> bool:
        """Удалить конфиг модели."""
        return self._app.delete(f"models/{model_id}.json")


# ──────────────────────────────────────────────
#  Глобальный синглтон для удобного импорта
# ──────────────────────────────────────────────

appdata = AppData()
