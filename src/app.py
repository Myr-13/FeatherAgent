import asyncio
import flet as ft
from flet import FontWeight

from src.agent.agent import Agent
from src.pipeline import Pipeline
from src.history_manager import history_manager
from src.utils.storage import appdata


class FeatherCodeApp:
	def __init__(self, page: ft.Page):
		self._page = page
		self._agent = Agent()
		self._pipeline = Pipeline(self.add_message)

		# Основные элементы
		self._chat_list_view = ft.ListView(
			expand=True,
			spacing=10,
			padding=20,
			auto_scroll=True,
		)

		self._input_field = ft.TextField(
			hint_text="Напишите задачу для агента...",
			expand=True,
			border_radius=10,
			on_submit=self.handle_send_message
		)

		# Сайдбар: список чатов
		self._sidebar_chats = ft.Column(spacing=5, scroll=ft.ScrollMode.AUTO)

		# Создаём первый чат, если нет ни одного
		if not history_manager.available_chats:
			history_manager.create_chat("Чат 1")
		else:
			history_manager.switch_chat(history_manager.available_chats[0])

	async def build(self):
		self._page.title = "Feather Code"
		self._page.theme_mode = ft.ThemeMode.DARK
		self._page.padding = 0
		self._page.spacing = 0

		main_layout = ft.Row(
			[self._build_sidebar(), self._build_chat_area()],
			expand=True,
		)
		self._page.add(main_layout)
		self._refresh_sidebar()

	# ── Sidebar ───────────────────────────────────

	def _build_sidebar(self):
		header = ft.Row([
			ft.Text("Чаты", weight=FontWeight.BOLD, size=20, expand=True),
			ft.IconButton(
				icon=ft.Icons.ADD_CIRCLE_OUTLINE,
				icon_color=ft.Colors.BLUE_400,
				tooltip="Новый чат",
				on_click=self._handle_new_chat,
			),
			ft.IconButton(
				icon=ft.Icons.SETTINGS_OUTLINED,
				icon_color=ft.Colors.GREY_400,
				tooltip="Настройки",
				on_click=self._handle_open_settings,
			),
		])

		return ft.Container(
			content=ft.Column([header, ft.Divider(), self._sidebar_chats], expand=True),
			width=260,
			bgcolor=ft.Colors.BLACK,
			padding=ft.padding.only(top=20, left=10, right=10, bottom=10),
		)

	def _refresh_sidebar(self):
		self._sidebar_chats.controls.clear()
		for chat_id in history_manager.available_chats:
			is_active = chat_id == history_manager.chat_id
			bg = ft.Colors.BLUE_GREY_800 if is_active else ft.Colors.TRANSPARENT

			btn = ft.Container(
				content=ft.Row([
					ft.Icon(ft.Icons.CHAT_OUTLINED, size=18, color=ft.Colors.BLUE_200 if is_active else ft.Colors.GREY_400),
					ft.Text(chat_id, expand=True, color=ft.Colors.WHITE if is_active else ft.Colors.GREY_300),
					ft.IconButton(
						icon=ft.Icons.DELETE_OUTLINE,
						icon_size=16,
						icon_color=ft.Colors.RED_200,
						tooltip="Удалить чат",
						on_click=lambda _, cid=chat_id: self._handle_delete_chat(cid),
					),
				]),
				bgcolor=bg,
				border_radius=8,
				padding=5,
				ink=True,
				on_click=lambda _, cid=chat_id: self._handle_switch_chat(cid),
			)
			self._sidebar_chats.controls.append(btn)

		self._page.update()

	# ── Chat area ─────────────────────────────────

	def _build_chat_area(self):
		return ft.Container(
			content=ft.Column([
				self._chat_list_view,
				ft.Row([
					self._input_field,
					ft.IconButton(
						icon=ft.Icons.SEND_ROUNDED,
						on_click=self.handle_send_message,
						icon_color=ft.Colors.BLUE_400,
					),
				]),
			], expand=True),
			expand=True,
			padding=10,
			bgcolor=ft.Colors.GREY_900,
		)

	async def add_message(self, text: str, color: str, icon: str = ""):
		prefix = f"{icon} " if icon else ""
		self._chat_list_view.controls.append(
			ft.Text(f"{prefix}{text}", color=color, selectable=True)
		)
		self._page.update()

	# ── Handlers ──────────────────────────────────

	async def handle_send_message(self, e):
		user_text = self._input_field.value.strip()
		if not user_text:
			return

		self._input_field.value = ""
		await self.add_message(f"👤 User: {user_text}", ft.Colors.BLUE_200)

		try:
			self._page.run_task(self._pipeline.run, self._agent, user_text)
		except Exception as ex:
			await self.add_message(f"⚠️ Error: {str(ex)}", ft.Colors.RED_400)

	async def _handle_new_chat(self, e):
		"""Создать новый чат."""
		history_manager.create_chat()
		self._chat_list_view.controls.clear()
		self._refresh_sidebar()

	async def _handle_switch_chat(self, chat_id: str):
		"""Переключиться на существующий чат."""
		self._chat_list_view.controls.clear()
		history_manager.switch_chat(chat_id)

		# Показываем последние сообщения из истории
		for msg in history_manager.history:
			role = msg.get("role", "")
			content = msg.get("content", "")
			if content:
				icon = {"user": "👤", "assistant": "🤖", "tool": "🔨"}.get(role, "")
				await self.add_message(f"{icon} {content}", ft.Colors.WHITE)

		self._refresh_sidebar()

	async def _handle_delete_chat(self, chat_id: str):
		"""Удалить чат."""
		appdata.chats.delete(chat_id)

		# Если удалили текущий — переключаемся на первый доступный
		if chat_id == history_manager.chat_id:
			self._chat_list_view.controls.clear()
			available = history_manager.available_chats
			if available:
				history_manager.switch_chat(available[0])
			else:
				history_manager.create_chat("Чат 1")

		self._refresh_sidebar()

	# ── Settings dialog ───────────────────────────

	async def _handle_open_settings(self, e):
		"""Открыть диалог настроек модели."""
		api_key_field = ft.TextField(
			label="API Key",
			value=self._agent.api_key,
			password=True,
			can_reveal_password=True,
			width=400,
		)
		base_url_field = ft.TextField(
			label="Base URL",
			value=self._agent.base_url,
			width=400,
		)
		model_field = ft.TextField(
			label="Model",
			value=self._agent.model,
			width=400,
		)

		def save_settings(e):
			self._agent.configure(
				api_key=api_key_field.value.strip() or None,
				base_url=base_url_field.value.strip() or None,
				model=model_field.value.strip() or None,
			)
			dialog.open = False
			self._page.update()

		dialog = ft.AlertDialog(
			title=ft.Text("Настройки модели"),
			content=ft.Column([
				api_key_field,
				base_url_field,
				model_field,
			], tight=True, spacing=10),
			actions=[
				ft.TextButton("Отмена", on_click=lambda e: setattr(dialog, 'open', False) or self._page.update()),
				ft.FilledButton("Сохранить", on_click=save_settings),
			],
		)

		self._page.dialog = dialog
		dialog.open = True
		self._page.update()


async def main(page: ft.Page):
	app = FeatherCodeApp(page)
	await app.build()


if __name__ == "__main__":
	ft.run(main)