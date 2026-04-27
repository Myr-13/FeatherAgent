import asyncio
import json

import flet as ft
from flet import FontWeight

from src.agent.agent import Agent
from src.utils.filesystem import build_tree
from src.agent.prompts import main_prompt


async def test(page: ft.Page, chat_list):
	await asyncio.sleep(3)
	chat_list.controls.append(ft.Text(f"Done", color=ft.Colors.BLUE_200))
	page.update()


def main(page: ft.Page):
	page.title = "Feather Code"
	page.theme_mode = ft.ThemeMode.DARK
	page.padding = 0
	page.spacing = 0

	# Список для хранения сообщений чата
	chat_list = ft.ListView(
		expand=True,
		spacing=10,
		padding=20,
		auto_scroll=True,
	)

	# Поле ввода текста
	input_field = ft.TextField(
		hint_text="Напишите задачу для агента...",
		expand=True,
		border_radius=10,
		value="src/app.py че там",
		on_submit=lambda e: send_message(e)
	)

	agent: Agent = Agent()

	def send_message(e):
		if not input_field.value:
			return

		user_text = input_field.value
		input_field.value = ""

		# Добавляем сообщение пользователя
		chat_list.controls.append(
			ft.Text(f"👤 User: {user_text}", color=ft.Colors.BLUE_200)
		)

		# Имитация работы агента (typing status)
		try:
			agent_res = agent.process(
				user_prompt=user_text,
				system_prompt=main_prompt(build_tree("."))
			)
		except Exception as e:
			chat_list.controls.append(f"{e}")
			page.update()
			return

		if agent_res[1] is not None:
			for tool in agent_res[1]:
				args = json.loads(tool.function.arguments)
				if tool.function.name == "read":
					with open(args["name"], "r", encoding="utf-8") as f:
						content: str = f.read()
						agent_res = agent.process(
							tool_result=content,
							system_prompt=main_prompt(build_tree("."))
						)

		bot_message = ft.Text(f"🤖 Agent: {agent_res[0]}", selectable=True, color=ft.Colors.GREEN_200)
		chat_list.controls.append(bot_message)
		page.update()

	# Боковая панель (Sidebar)
	sidebar = ft.Container(
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

	# Основная область чата
	chat_container = ft.Container(
		content=ft.Column([
			chat_list,
			ft.Row([
				input_field,
				ft.IconButton(
					icon=ft.Icons.SEND_ROUNDED,
					on_click=send_message,
					icon_color=ft.Colors.BLUE_400
				)
			])
		]),
		expand=True,
		padding=10,
		bgcolor=ft.Colors.GREY_900
	)

	# Собираем всё в главное окно
	page.add(
		ft.Row(
			[
				sidebar,
				chat_container,
			],
			expand=True,
		)
	)


if __name__ == "__main__":
	ft.run(main)
