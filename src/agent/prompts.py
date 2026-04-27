def main_prompt(fs_tree: str) -> str:
	return f"""
	Ты - кодинг агент Feather Code. Делай только то, что просит пользователь.
	
	# Текущее файловое древо
	{fs_tree}
	"""
