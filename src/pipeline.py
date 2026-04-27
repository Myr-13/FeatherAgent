from src.agent.agent import Agent
from src.agent.prompts import main_prompt
from src.utils.filesystem import build_tree


class Pipeline:
	def __init__(self):
		pass

	def _run_tool(self, tool_name: str, arguments: dict):
		pass

	async def run(self, agent: Agent, prompt: str):
		while True:
			agent_res = agent.process(
				user_prompt=prompt,
				system_prompt=main_prompt(build_tree("."))
			)
			prompt = None

			if agent_res is None:
				return
