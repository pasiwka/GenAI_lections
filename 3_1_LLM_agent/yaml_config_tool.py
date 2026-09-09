import yaml
import os
from typing import Any, Dict, Optional, List
from cerberus import Validator

class YAMLConfigTool:
    """
    Инструмент для чтения/записи YAML файлов с валидацией схемы.
    """

    name = "yaml_config"
    description = (
        "Читает, записывает и валидирует YAML конфигурации. "
        "Поддерживает вложенные ключи и валидацию по схеме Cerberus."
    )

    def __init__(self, schema: Optional[Dict] = None):
        """
        Инициализация инструмента.

        Args:
            schema: Схема для валидации (Cerberus формат)
        """
        self.schema = schema
        self.validator = Validator(schema) if schema else None
        self.current_config = {}
        self.last_file_path = None

    def load(self, file_path: str) -> Dict[str, Any]:
        """
        Загружает YAML файл.

        Args:
            file_path: Путь к YAML файлу

        Returns:
            Словарь с конфигурацией

        Raises:
            FileNotFoundError: Если файл не существует
            yaml.YAMLError: Если файл имеет неверный синтаксис
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не найден: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as file:
            self.current_config = yaml.safe_load(file) or {}
            self.last_file_path = file_path
            return self.current_config

    def save(self, file_path: Optional[str] = None) -> bool:
        """
        Сохраняет текущую конфигурацию в YAML файл.

        Args:
            file_path: Путь для сохранения (если None, используется последний загруженный)

        Returns:
            True если успешно, иначе False
        """
        if file_path is None:
            file_path = self.last_file_path

        if not file_path:
            raise ValueError("Не указан путь для сохранения")

        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                yaml.dump(self.current_config, file, default_flow_style=False, allow_unicode=True)
            self.last_file_path = file_path
            return True
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            return False

    def validate(self, config: Optional[Dict] = None) -> Dict[str, List[str]]:
        """
        Валидирует конфигурацию по схеме.

        Args:
            config: Конфигурация для проверки (если None, используется current_config)

        Returns:
            Словарь с ошибками валидации (пустой, если всё корректно)
        """
        if self.validator is None:
            return {"error": ["Схема не задана"]}

        data_to_validate = config if config is not None else self.current_config

        if not data_to_validate:
            return {"error": ["Конфигурация пуста"]}

        if self.validator.validate(data_to_validate):
            return {}
        else:
            return self.validator.errors

    def get(self, key: str, default: Any = None) -> Any:
        """
        Получает значение по ключу (поддерживает вложенные ключи через точку).

        Args:
            key: Ключ (например, "database.host")
            default: Значение по умолчанию

        Returns:
            Значение или default
        """
        keys = key.split('.')
        value = self.current_config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Устанавливает значение по ключу (создает вложенные ключи при необходимости).

        Args:
            key: Ключ (например, "database.host")
            value: Новое значение
        """
        keys = key.split('.')
        config = self.current_config

        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def load_and_validate(self, file_path: str) -> tuple:
        """
        Загружает и валидирует конфигурацию за один шаг.

        Args:
            file_path: Путь к YAML файлу

        Returns:
            (успех, ошибки_или_конфиг)
        """
        try:
            config = self.load(file_path)
            errors = self.validate(config)
            if errors:
                return False, errors
            return True, config
        except Exception as e:
            return False, {"error": [str(e)]}

    def create_template(self, file_path: str) -> bool:
        """
        Создает шаблон конфигурации на основе схемы.

        Args:
            file_path: Путь для сохранения шаблона

        Returns:
            True если успешно
        """
        if self.schema is None:
            return False

        template = {}
        for field, rules in self.schema.items():
            if 'default' in rules:
                template[field] = rules['default']
            elif rules.get('type') == 'dict' and 'schema' in rules:
                template[field] = {}
            elif rules.get('type') == 'list':
                template[field] = []
            elif rules.get('type') == 'string':
                template[field] = ""
            elif rules.get('type') == 'integer':
                template[field] = 0
            elif rules.get('type') == 'boolean':
                template[field] = False

        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                yaml.dump(template, file, default_flow_style=False, allow_unicode=True)
            return True
        except Exception as e:
            print(f"Ошибка создания шаблона: {e}")
            return False
