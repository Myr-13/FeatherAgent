import flet as ft
import openai

client = openai.OpenAI(
	api_key="qw-owfcvEfUE2jRy2qv2gwbCdtQwwhajJuYh1cfxykH0gd70IYSWF1qJyPAZQurpc6e",
	base_url="http://localhost:8000/"
)


def client_wrapper(content: str) -> tuple[str, dict | None]:
	res = client.chat.completions.create(
		model="qwen3.5-flash",
		messages=[
			{"role": "user", "content": content}
		],
		tools=[
			{
				"type": "function",
				"function": {
					"name": "read",
					"description": "Read file",
					"parameters": {
						"type": "object",
						"properties": {
							"name": {"type": "string", "description": "File name"}
						},
						"required": ["name"]
					}
				}
			}
		]
	)

	return res.choices[0].message.content, res.choices[0].message.tool_calls


async def main(page: ft.Page):
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
		value="src/main.py че там",
		on_submit=lambda e: send_message(e)
	)

	def send_message(e):
		if not input_field.value:
			print(input_field.value)
			return

		user_text = input_field.value
		input_field.value = ""

		# Добавляем сообщение пользователя
		chat_list.controls.append(
			ft.Text(f"👤 User: {user_text}", color=ft.Colors.BLUE_200)
		)

		# Имитация работы агента (typing status)
		try:
			agent_text: str = client_wrapper(user_text)
		except Exception as e:
			chat_list.controls.append(f"{e}")
			page.update()
			return
		bot_message = ft.Text(f"🤖 Agent: {agent_text}", color=ft.Colors.GREEN_200)
		chat_list.controls.append(bot_message)
		page.update()

	# Боковая панель (Sidebar)
	sidebar = ft.Container(
		content=ft.Column([
			ft.Text("History", weight="bold", size=20),
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
