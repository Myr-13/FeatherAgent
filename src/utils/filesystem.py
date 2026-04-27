import os
from pathlib import Path
import pathspec


def get_ignored_spec(root_dir):
	"""Читает .gitignore и возвращает объект для фильтрации."""
	gitignore_path = Path(root_dir) / ".gitignore"
	if gitignore_path.exists():
		with open(gitignore_path, "r", encoding="utf-8") as f:
			# Создаем спецификацию на основе строк из файла
			return pathspec.PathSpec.from_lines('gitwildmatch', f)
	return None


def build_tree(directory, prefix="", root_dir=None, spec=None) -> str:
	path = Path(directory)
	if root_dir is None:
		root_dir = path
		# Загружаем spec один раз в начале
		spec = get_ignored_spec(root_dir)

	try:
		items = sorted([p for p in path.iterdir() if p.name != ".git"],
					   key=lambda x: (x.is_file(), x.name.lower()))
	except PermissionError:
		return []

	tree = []
	for i, item in enumerate(items):
		relative_path = os.path.relpath(item, root_dir)

		if spec and spec.match_file(relative_path):
			continue

		is_last = (i == len(items) - 1)
		connector = "└── " if is_last else "├── "
		tree.append(f"{prefix}{connector}{item.name}")

		if item.is_dir():
			new_prefix = prefix + ("    " if is_last else "│   ")
			# extend теперь корректно добавит список строк
			tree.extend(build_tree(item, new_prefix, root_dir, spec))

	# Если это самый верхний уровень, склеиваем всё в строку
	if prefix == "":
		return f"{root_dir.resolve().name}/\n" + "\n".join(tree)
	return tree
