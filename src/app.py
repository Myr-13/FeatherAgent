import flet as ft
import openai


async def main(page: ft.Page):
	client = openai.OpenAI(
		api_key="qw-owfcvEfUE2jRy2qv2gwbCdtQwwhajJuYh1cfxykH0gd70IYSWF1qJyPAZQurpc6e",
		base_url="http://localhost:8000/"
	)

	res = client.chat.completions.create(
		model="qwen3.5-flash",
		messages=[
			{"role": "user", "content": "Дарова. прочитай файл src/app.py и скажи че в нем"}
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

	print(res.choices[0].message)

	page.title = "AI Coding Agent"
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
		on_submit=lambda e: send_message(e)
	)

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
		bot_message = ft.Text("🤖 Agent: ", color=ft.Colors.GREEN_200)
		chat_list.controls.append(bot_message)
		page.update()

		# Имитация стриминга ответа
		response_text = "Я проанализировал ваш код. Вот решение...\n```python\nprint('Hello World')\n```"
		for i in range(len(response_text)):
			bot_message.value += response_text[i]
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
