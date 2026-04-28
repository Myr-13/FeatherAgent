import json

from src.agent.agent import Agent
from src.agent.prompts import main_prompt
from src.utils.filesystem import build_tree


class Pipeline:
	def __init__(self, emit_message):
		self.emit_message = emit_message

	async def _run_tool(self, tool_name: str, arguments: dict) -> str | None:
		print(tool_name, arguments)

		if tool_name == "x7a3_read":
			file_name: str = arguments["file_name"]

			await self.emit_message(f"Read {file_name}", "bluegrey", "🔨")
			with open(file_name, "r", encoding="utf-8") as f:
				return f.read()
		elif tool_name == "o93u_write":
			file_name: str = arguments["file_name"]
			old_string: str = arguments["old_string"]
			new_string: str = arguments["new_string"]

			await self.emit_message(f"Updating {file_name}", "bluegrey", "🔨")

			try:
				with open(file_name, "r", encoding="utf-8") as f:
					content = f.read()
			except FileNotFoundError:
				content = ""
				pass

			if old_string == "":
				new_content = new_string
			else:
				new_content = content.replace(old_string, new_string)

			with open(file_name, "w", encoding="utf-8") as f:
				f.write(new_content)

			return "DONE"

		elif tool_name == "execute_shell":
			command: str = arguments["command"]

			await self.emit_message(f"Executing shell command: {command}", "bluegrey", "🔨")

			import subprocess
			try:
				result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
				return f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}\nReturn Code: {result.returncode}"
			except Exception as e:
				return f"Error: {str(e)}"

		return None

	async def run(self, agent: Agent, prompt: str):
		tool_result: str | None = None

		while True:
			try:
				agent_res = await agent.process(
					user_prompt=prompt,
					tool_result=tool_result,
					system_prompt=main_prompt(build_tree("."))
				)
			except Exception as e:
				continue
			prompt = None

			agent_text: str | None = agent_res[0]
			if agent_text is not None:
				if "Tool" in agent_text and "does not exists" in agent_text:
					tool_result = "{\"error\": \"DO NOT USE NATIVE FUNCTION CALLING, ONLY <TOOL_CALLING>\"}"
					await self.emit_message("Agent tried to call native tool", "red200", "❌")
					continue

				await self.emit_message(agent_res[0], "blue200", "🤖")

			if agent_res[1] is None:
				return

			for tool in agent_res[1]:
				args: dict = json.loads(tool.function.arguments)
				try:
					tool_result = await self._run_tool(tool.function.name, args)
				except Exception as e:
					await self.emit_message(str(e), "red200", "🔨")
					tool_result = "{\"error\": \"%s\"}" % str(e)
