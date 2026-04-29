from typing import Literal, Optional

from src.utils.storage import appdata

type HistoryRole = Literal["system", "user", "tool", "assistant"]


class HistoryManager:
	def __init__(self) -> None:
		self._history: list[dict] = []
		self._system_prompt: dict | None = None
		self._chat_id: str | None = None

	# ── Управление чатами ─────────────────────────

	@property
	def chat_id(self) -> str | None:
		return self._chat_id

	def switch_chat(self, chat_id: str) -> None:
		"""Переключиться на другой чат (автосохранение текущего + загрузка нового)."""
		self._save_current()
		self._chat_id = chat_id
		self._history = appdata.chats.get(chat_id, default=[])
		self._system_prompt = None

	def create_chat(self, chat_id: Optional[str] = None) -> str:
		"""Создать новый чат со случайным ID."""
		import uuid
		if chat_id is None:
			chat_id = str(uuid.uuid4())[:8]
		self._save_current()
		self._chat_id = chat_id
		self._history = []
		self._system_prompt = None
		return chat_id

	@property
	def available_chats(self) -> list[str]:
		"""Список всех сохранённых чатов."""
		return appdata.chats.list

	# ── История ───────────────────────────────────

	def set_system_prompt(self, content: str) -> None:
		self._system_prompt = {"role": "system", "content": content}

	def add(self, role: HistoryRole, content: str, tool_call_id: str | None = None) -> None:
		if role == "system":
			self.set_system_prompt(content)
			return

		message = {"role": role, "content": content}

		if role == "tool":
			if tool_call_id is None:
				raise ValueError("For role 'tool' you must pass tool_call_id")
			message["tool_call_id"] = tool_call_id

		self._history.append(message)
		self._save_current()

	def add_assistant(self, content: str | None, tool_calls: list | None) -> None:
		message = {"role": "assistant", "content": content}
		if tool_calls:
			message["tool_calls"] = [t.model_dump() for t in tool_calls]
		self._history.append(message)
		self._save_current()

	@property
	def history(self) -> list[dict]:
		if self._system_prompt:
			return [self._system_prompt] + self._history
		return self._history

	@property
	def have_system_prompt(self) -> bool:
		return self._system_prompt is not None

	# ── Сохранение ────────────────────────────────

	def _save_current(self) -> None:
		"""Сохранить текущую историю в AppData."""
		if self._chat_id is not None and self._history:
			appdata.chats.save(self._chat_id, self._history)

	def save_as(self, filename: str) -> None:
		"""Сохранить историю в произвольный файл внутри AppData."""
		appdata.save_json(filename, self._history)


history_manager = HistoryManager()
