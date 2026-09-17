# main.py
from llm_agent.core_v2 import LLMAgent
import tempfile
import os


def main():
    """Основная функция для запуска агента."""
    print("LLM-агент с инструментами ('Калькулятор', 'Поиск', 'PDF', 'YAML Config')")
    print("-" * 70)

    agent = LLMAgent(local=True, ollama_model="llama3.2:3b")

    # =================================================================
    # Демонстрация 1: YAMLConfigTool — чтение + валидация
    # =================================================================
    print("\n[Демонстрация 1] Работа с YAML-конфигурацией")
    print("-" * 70)

    # Создаём временный YAML-файл для демонстрации
    with tempfile.NamedTemporaryFile(
        suffix='.yaml', delete=False, mode='w', encoding='utf-8'
    ) as tmp_file:
        tmp_file.write("""
app_name: MyApp
version: 1.2.3
debug: true
database:
  host: localhost
  port: 5432
  name: mydb
  user: admin
  password: secret
""")
        yaml_path = tmp_file.name

    try:
        query = f"Используй инструмент yaml_config с действием read для файла {yaml_path}"

        print(f"Ваш запрос: {query}")
        print("-" * 70)

        response = agent.process_query(query)

        print("\n" + "=" * 70)
        print("Финальный ответ агента:\n")
        print(response)
        print("=" * 70)

    finally:
        if os.path.exists(yaml_path):
            os.unlink(yaml_path)

    # =================================================================
    # Демонстрация 2: YAMLConfigTool — парсинг строки
    # =================================================================
    print("\n[Демонстрация 2] Парсинг YAML-строки")
    print("-" * 70)

    yaml_string = """
app: ParseDemo
version: 3.0.0
features:
  - auth
  - logging
settings:
  timeout: 60
"""

    query2 = f"Распарси YAML-строку:\n{yaml_string}"

    print(f"Ваш запрос: Распарси YAML-строку")
    print("-" * 70)

    response2 = agent.process_query(query2)

    print("\n" + "=" * 70)
    print("Финальный ответ агента:\n")
    print(response2)
    print("=" * 70)


if __name__ == "__main__":
    main()
