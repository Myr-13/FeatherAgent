import openai
from openai.types.chat import ChatCompletionMessageFunctionToolCall, ChatCompletionMessageCustomToolCall


class Agent:
	def __init__(self):
		self.model = "qwen3.5-flash"
		self.base_url = "http://localhost:8000/"
		self.api_key = "qw-owfcvEfUE2jRy2qv2gwbCdtQwwhajJuYh1cfxykH0gd70IYSWF1qJyPAZQurpc6e"

		self._client = openai.AsyncOpenAI(
			api_key=self.api_key,
			base_url=self.base_url
		)

	async def process(self, *,
				user_prompt: str | None = None,
				tool_result: str | None = None,
				system_prompt: str | None = None
				) -> tuple[str, list[ChatCompletionMessageFunctionToolCall | ChatCompletionMessageCustomToolCall]]:
		if user_prompt is None and tool_result is None:
			raise ValueError("You must provide either user_prompt or tool_result")

		role: str = "user" if user_prompt is not None else "tool"
		content: str = user_prompt if user_prompt is not None else tool_result

		res = await self._client.chat.completions.create(
			model=self.model,
			messages=[
				{"role": "system", "content": system_prompt},
				{"role": role, "content": content}
			],
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
				}
			]
		)

		return res.choices[0].message.content, res.choices[0].message.tool_calls
