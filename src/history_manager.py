from typing import Literal

type HistoryRole = Literal["system", "user", "tool", "assistant"]


class HistoryManager:
	def __init__(self) -> None:
		self._history: list[dict] = []
		self._system_prompt: dict | None = None

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

	def add_assistant(self, content: str | None, tool_calls: list | None) -> None:
		message = {"role": "assistant", "content": content}
		if tool_calls:
			message["tool_calls"] = [t.model_dump() for t in tool_calls]
		self._history.append(message)

	@property
	def history(self) -> list[dict]:
		if self._system_prompt:
			return [self._system_prompt] + self._history
		return self._history

	@property
	def have_system_prompt(self) -> bool:
		return self._system_prompt is not None


history_manager = HistoryManager()
