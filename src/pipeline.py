import json

from src.agent.agent import Agent
from src.agent.prompts import main_prompt
from src.utils.filesystem import build_tree


class Pipeline:
	def __init__(self, emit_message):
		self.emit_message = emit_message

	async def _run_tool(self, tool_name: str, arguments: dict) -> str | None:
		print(tool_name, arguments)

		if tool_name == "read":
			file_name: str = arguments["file_name"]

			await self.emit_message(f"Read {file_name}", "bluegrey", "🔨")
			with open(file_name, "r", encoding="utf-8") as f:
				return f.read()
		elif tool_name == "write":
			file_name: str = arguments["file_name"]
			old_string: str = arguments["old_string"]
			new_string: str = arguments["new_string"]

			await self.emit_message(f"Updating {file_name}", "bluegrey", "🔨")

			try:
				with open(file_name, "r", encoding="utf-8") as f:
					content = f.read()
			except FileNotFoundError:
				pass

			new_content = content.replace(old_string, new_string)

			with open(file_name, "w", encoding="utf-8") as f:
				f.write(new_content)

		return None

	async def run(self, agent: Agent, prompt: str):
		tool_result: str | None = None

		while True:
			agent_res = await agent.process(
				user_prompt=prompt,
				tool_result=tool_result,
				system_prompt=main_prompt(build_tree("."))
			)
			prompt = None

			if agent_res[0] is not None:
				await self.emit_message(agent_res[0], "blue200", "🤖")

			if agent_res[1] is None:
				return

			for tool in agent_res[1]:
				args: dict = json.loads(tool.function.arguments)
				tool_result = await self._run_tool(tool.function.name, args)
