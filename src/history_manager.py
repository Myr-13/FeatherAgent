class HistoryManager:
	def __init__(self) -> None:
		self._history: list[dict] = []

	def add(self, role: str, content: str) -> None:
		self._history.append({"role": role, "content": content})

	@property
	def history(self) -> list[dict]:
		return self._history
