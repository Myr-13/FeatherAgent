import asyncio
import flet as ft
from flet import FontWeight

# Твои импорты
from src.agent.agent import Agent
from src.pipeline import Pipeline
from src.history_manager import history_manager


class FeatherCodeApp:
	def __init__(self, page: ft.Page):
		self._page = page
		self._agent = Agent()
		self._pipeline = Pipeline(self.add_message)

		# Основные элементы управления (чтобы иметь к ним доступ из любого метода)
		self._chat_list = ft.ListView(
			expand=True,
			spacing=10,
			padding=20,
			auto_scroll=True,
		)

		self._input_field = ft.TextField(
			hint_text="Напишите задачу для агента...",
			expand=True,
			border_radius=10,
			value="Добавь инструмент execute_shell в pipeline.py и agent.py",
			on_submit=self.handle_send_message
		)

	async def build(self):
		"""Настройка страницы и сборка интерфейса"""
		self._page.title = "Feather Code"
		self._page.theme_mode = ft.ThemeMode.DARK
		self._page.padding = 0
		self._page.spacing = 0

		# Собираем UI
		main_layout = ft.Row(
			[
				self._build_sidebar(),
				self._build_chat_area(),
			],
			expand=True,
		)

		self._page.add(main_layout)

	def _build_sidebar(self):
		"""Боковая панель"""
		return ft.Container(
			content=ft.Column([
				ft.Text("History", weight=FontWeight.BOLD, size=20),
				ft.Divider(),
				ft.TextButton("Task 1: Optimize SQL"),
				ft.TextButton("Task 2: Refactor UI"),
			]),
			width=250,
			bgcolor=ft.Colors.BLACK,
			padding=20,
		)

	def _build_chat_area(self):
		"""Основная зона чата"""
		return ft.Container(
			content=ft.Column([
				self._chat_list,
				ft.Row([
					self._input_field,
					ft.IconButton(
						icon=ft.Icons.SEND_ROUNDED,
						on_click=self.handle_send_message,
						icon_color=ft.Colors.BLUE_400
					)
				])
			], expand=True),
			expand=True,
			padding=10,
			bgcolor=ft.Colors.GREY_900
		)

	async def add_message(self, text: str, color: str, icon: str = ""):
		"""Вспомогательный метод для добавления сообщений в чат"""
		prefix = f"{icon} " if icon else ""
		self._chat_list.controls.append(
			ft.Text(f"{prefix}{text}", color=color, selectable=True)
		)
		self._page.update()

	async def handle_send_message(self, e):
		"""Логика отправки сообщения"""
		user_text = self._input_field.value.strip()
		if not user_text:
			return

		# Очищаем ввод и уведомляем UI
		self._input_field.value = ""
		await self.add_message(f"User: {user_text}", ft.Colors.BLUE_200, icon="👤")

		try:
			# Запускаем пайплайн (если он асинхронный — используем await)
			# Если pipeline.run не асинхронный, его лучше обернуть в run_in_executor
			self._page.run_task(
				self._pipeline.run, self._agent, user_text
			)

		except Exception as ex:
			await self.add_message(f"Error: {str(ex)}", ft.Colors.RED_400, icon="⚠️")


async def main(page: ft.Page):
	app = FeatherCodeApp(page)
	await app.build()


if __name__ == "__main__":
	ft.run(main)