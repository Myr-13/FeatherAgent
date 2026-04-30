import sys
sys.stdout.reconfigure(encoding='utf-8')

from src.utils.storage import appdata

# Чаты
appdata.chats.save("demo_chat", [{"role": "user", "content": "hi"}])
print("chats:", appdata.chats.list)
print("chat:", appdata.chats.get("demo_chat"))

# Конфиг
appdata.config.set("theme", "dark")
print("config:", appdata.config.all())

# Модели
appdata.models.save("gpt4o_mini", {"max_tokens": 8192})
print("models:", appdata.models.list)
print("model:", appdata.models.get("gpt4o_mini"))

# Чистка
appdata.delete("chats/demo_chat.json")
appdata.models.delete("gpt4o_mini")
appdata.config.reset()

print()
print("AppData:", appdata.base)
print("ALL OK")
