import openai
from openai.types.chat import ChatCompletionMessageFunctionToolCall, ChatCompletionMessageCustomToolCall, ChatCompletion


class Agent:
	def __init__(self):
		self.model = "deepseek/deepseek-v4-flash"
		self.base_url = "https://routerai.ru/api/v1"
		self.api_key = "sk-5RWx2FkY_1tCFnuKFctKRycaDDcEpTEX"

		self._client = openai.AsyncOpenAI(
			api_key=self.api_key,
			base_url=self.base_url
		)

	async def process(self, history: list[dict]) -> tuple[str, list[ChatCompletionMessageFunctionToolCall | ChatCompletionMessageCustomToolCall]]:
		res = await self._client.chat.completions.create(
			model=self.model,
			messages=history,
			tools=[
				{
					"type": "function",
					"function": {
						"name": "read",
						"description": "Read file by file_name (path)",
						"parameters": {
							"type": "object",
							"properties": {
								"file_name": {"type": "string", "description": "File name or path"}
							},
							"required": ["file_name"]
						}
					}
				},
				{
					"type": "function",
					"function": {
						"name": "write",
						"description": "Replaces EXACTLY old_string with new_string in file_name (path)",
						"parameters": {
							"type": "object",
							"properties": {
								"old_string": {"type": "string", "description": "Old string in file to replace with new_string"},
								"new_string": {"type": "string", "description": "New string"},
								"file_name": {"type": "string", "description": "File name or path"}
							},
							"required": ["old_string", "new_string", "file_name"]
						}
					}
				},
				{
					"type": "function",
					"function": {
						"name": "execute_shell",
						"description": "Execute a shell command on the system",
						"parameters": {
							"type": "object",
							"properties": {
								"command": {"type": "string", "description": "Shell command to execute"}
							},
							"required": ["command"]
						}
					}
				}
			]
		)

		if res.choices is None and res.status_code == 400:
			raise Exception(res.detail)
		return res.choices[0].message.content, res.choices[0].message.tool_calls
