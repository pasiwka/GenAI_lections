import pytest
#from unittest.mock import MagicMock, patch
from llm_agent.core_v2 import LLMAgent

# =====================================================================
# ИНТЕГРАЦИОННЫЕ ТЕСТЫ (Запускают реальную Ollama / API)
# =====================================================================
# Маркируем как 'integration', чтобы их можно было отключать при быстрой проверке

@pytest.mark.integration
def test_calculator_query_live():
    """Реальный запуск агента для проверки математики."""
    # Для тестов лучше использовать локальную модель, если она поднята
    agent = LLMAgent(local=True, ollama_model="qwen3.5:0.8b")
    query = "Сколько будет (5 + 3) * 2? Напиши только цифру."
    
    response = agent.process_query(query)
    
    # Проверяем, что агент смог посчитать и выдать 16
    assert "16" in response


@pytest.mark.integration
def test_football_query_live():
    """Реальный запуск агента для проверки поиска DuckDuckGo."""
    agent = LLMAgent(local=True, ollama_model="qwen3.5:0.8b")
    query = "Кто выиграл последний матч Спартак-Динамо?"
    
    response = agent.process_query(query)
    
    # Проверяем, что в реальном ответе фигурируют названия команд
    assert "Спартак" in response or "Spartak" in response
    assert "Динамо" in response or "Dynamo" in response
# =====================================================================
# ТЕСТЫ ДЛЯ YAML_CONFIG TOOL
# =====================================================================

@pytest.mark.integration
def test_yamlconfig_from_agent():
    """Тест, что агент распознает необходимость использования YAML инструмента."""
    agent = LLMAgent(local=True, ollama_model="qwen3.5:0.8b")
    
    # Запрос, который должен вызвать yaml_config
    query = "Прочитай и покажи содержимое YAML файла config.yaml"
    
    plan = agent._ask_llm_for_plan(query)
    assert len(plan) > 0, "План должен содержать хотя бы одно действие"
    # Проверяем, что в плане есть yaml_config
    yaml_actions = [step for step in plan if step.get('action') == 'yaml_config']
    assert len(yaml_actions) > 0, "Должен использоваться инструмент yaml_config"


def test_yamlconfig_tool_read():
    """Тест чтения YAML-файла."""
    from llm_agent.tool_yamlconfig import YAMLConfigTool
    import tempfile
    
    tool = YAMLConfigTool()
    
    # Создаем тестовый YAML-файл
    with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False, mode='w', encoding='utf-8') as tmp_file:
        tmp_file.write("""
app: TestApp
version: 1.0.0
debug: true
database:
  host: localhost
  port: 5432
  name: testdb
""")
        yaml_path = tmp_file.name
    
    try:
        result = tool.use("read", file_path=yaml_path)
        
        # Проверяем, что файл прочитан и содержит ожидаемые данные
        assert "TestApp" in result
        assert "1.0.0" in result
        assert "localhost" in result
        assert "5432" in result
        assert "testdb" in result
        assert "Успешно прочитан" in result
    finally:
        os.unlink(yaml_path)


def test_yamlconfig_tool_write():
    """Тест записи YAML-файла."""
    from llm_agent.tool_yamlconfig import YAMLConfigTool
    import tempfile
    
    tool = YAMLConfigTool()
    
    # Создаем временный файл
    with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as tmp_file:
        yaml_path = tmp_file.name
    
    try:
        # Данные для записи
        test_data = {
            "app": "WriteTest",
            "version": "2.0.0",
            "enabled": True,
            "settings": {
                "timeout": 30,
                "retries": 3
            }
        }
        
        result = tool.use("write", file_path=yaml_path, data=test_data)
        
        # Проверяем, что файл создан и содержит данные
        assert "Успешно записан" in result
        assert "WriteTest" in result
        assert "2.0.0" in result
        assert "timeout" in result
        
        # Проверяем, что файл действительно существует
        assert os.path.exists(yaml_path)
        
        # Читаем файл и проверяем содержимое
        import yaml
        with open(yaml_path, 'r', encoding='utf-8') as f:
            loaded_data = yaml.safe_load(f)
        
        assert loaded_data["app"] == "WriteTest"
        assert loaded_data["version"] == "2.0.0"
        assert loaded_data["settings"]["timeout"] == 30
    finally:
        if os.path.exists(yaml_path):
            os.unlink(yaml_path)


def test_yamlconfig_tool_validate():
    """Тест валидации данных по схеме Cerberus."""
    from llm_agent.tool_yamlconfig import YAMLConfigTool
    
    tool = YAMLConfigTool()
    
    # Тестовые данные
    test_data = {
        "app_name": "MyApp",
        "version": "1.2.3",
        "debug": True,
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "mydb",
            "user": "admin",
            "password": "secret"
        }
    }
    
    # Схема валидации
    schema = {
        "app_name": {"type": "string", "required": True},
        "version": {"type": "string", "required": True, "regex": r"^\d+\.\d+\.\d+$"},
        "debug": {"type": "boolean", "required": False},
        "database": {
            "type": "dict",
            "required": True,
            "schema": {
                "host": {"type": "string", "required": True},
                "port": {"type": "integer", "required": True, "min": 1, "max": 65535},
                "name": {"type": "string", "required": True},
                "user": {"type": "string", "required": True},
                "password": {"type": "string", "required": True}
            }
        }
    }
    
    result = tool.use("validate", data=test_data, schema=schema)
    
    # Проверяем, что валидация успешна
    assert "успешна" in result or "success" in result.lower()
    assert "✅" in result or "успешна" in result
    assert "данные соответствуют схеме" in result.lower() or "соответствуют" in result


def test_yamlconfig_tool_validate_error():
    """Тест валидации с ошибками."""
    from llm_agent.tool_yamlconfig import YAMLConfigTool
    
    tool = YAMLConfigTool()
    
    # Некорректные данные
    test_data = {
        "app_name": "",  # Пустая строка (нарушает minlength)
        "version": "1.2",  # Не соответствует формату semver
        "database": {
            "host": "localhost",
            "port": 99999,  # Слишком большой порт
            "name": "mydb"
            # Отсутствуют обязательные поля user и password
        }
    }
    
    # Схема валидации
    schema = {
        "app_name": {"type": "string", "required": True, "minlength": 1},
        "version": {"type": "string", "required": True, "regex": r"^\d+\.\d+\.\d+$"},
        "database": {
            "type": "dict",
            "required": True,
            "schema": {
                "host": {"type": "string", "required": True},
                "port": {"type": "integer", "required": True, "min": 1, "max": 65535},
                "name": {"type": "string", "required": True},
                "user": {"type": "string", "required": True},
                "password": {"type": "string", "required": True}
            }
        }
    }
    
    result = tool.use("validate", data=test_data, schema=schema)
    
    # Проверяем, что валидация не прошла и найдены ошибки
    assert "ошибка" in result.lower()
    assert "❌" in result or "ошибка" in result.lower()
    assert "minlength" in result or "regex" in result or "обязательное" in result


def test_yamlconfig_tool_parse():
    """Тест парсинга YAML-строки."""
    from llm_agent.tool_yamlconfig import YAMLConfigTool
    
    tool = YAMLConfigTool()
    
    yaml_string = """
app: ParseTest
version: 3.0.0
features:
  - auth
  - logging
  - caching
settings:
  timeout: 60
  retry_count: 5
"""
    
    result = tool.use("parse", yaml_string=yaml_string)
    
    # Проверяем, что строка распарсена и данные извлечены
    assert "успешно распарсена" in result
    assert "ParseTest" in result
    assert "3.0.0" in result
    assert "auth" in result
    assert "logging" in result
    assert "caching" in result
    assert "timeout" in result
    assert "retry_count" in result


# Вспомогательная функция для объединения всех тестов
def run_all_yaml_tests():
    """Запускает все тесты для YAMLConfigTool (для удобства)."""
    print("Запуск всех тестов YAMLConfigTool...")
    test_yamlconfig_from_agent()
    test_yamlconfig_tool_read()
    test_yamlconfig_tool_write()
    test_yamlconfig_tool_validate()
    test_yamlconfig_tool_validate_error()
    test_yamlconfig_tool_parse()
    print("Все тесты пройдены!")
