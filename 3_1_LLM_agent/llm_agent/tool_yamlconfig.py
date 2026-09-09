import os
import yaml
from typing import Optional, Dict, Any, Union
from cerberus import Validator
import json


class YAMLConfigTool:
    """
    Инструмент для работы с YAML-конфигурациями: чтение, запись и валидация.
    Поддерживает загрузку из файла, сохранение в файл и проверку схемы через Cerberus.
    """

    name = "yaml_config"
    description = (
        "Инструмент для работы с YAML-конфигурационными файлами. "
        "Поддерживает чтение YAML из файла, запись данных в YAML-файл, "
        "а также валидацию данных по схеме Cerberus."
    )

    def use(
        self,
        action: str,
        file_path: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        schema: Optional[Dict[str, Any]] = None,
        yaml_string: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Выполняет действие с YAML-конфигурацией.

        Args:
            action: Действие ('read', 'write', 'validate', 'parse')
            file_path: Путь к YAML-файлу
            data: Данные для записи или валидации
            schema: Схема для валидации (формат Cerberus)
            yaml_string: YAML-строка для парсинга
            **kwargs: Дополнительные параметры

        Returns:
            Строка с результатом операции.
        """
        try:
            if action == "read":
                return self._read_yaml(file_path)
            elif action == "write":
                return self._write_yaml(file_path, data, **kwargs)
            elif action == "validate":
                return self._validate_yaml(data, schema)
            elif action == "parse":
                return self._parse_yaml_string(yaml_string)
            else:
                return f"Ошибка: неизвестное действие '{action}'. Доступные действия: read, write, validate, parse"

        except Exception as e:
            print(f"> Ошибка при работе с YAML: {e}")
            return f"Произошла ошибка при выполнении действия '{action}': {e}"

    def _read_yaml(self, file_path: str) -> str:
        """
        Читает YAML-файл и возвращает его содержимое в виде строки JSON.
        """
        if not os.path.isfile(file_path):
            return f"Ошибка: файл '{file_path}' не найден."

        print(f"> Читаю YAML-файл: '{file_path}'")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Форматируем вывод
            if data is None:
                return "Файл пуст или содержит только комментарии."
            
            # Возвращаем в удобочитаемом формате
            pretty_data = json.dumps(data, ensure_ascii=False, indent=2)
            
            result = (
                f"YAML файл: {file_path}\n"
                f"{'=' * 50}\n"
                f"Содержимое:\n{pretty_data}\n"
                f"{'=' * 50}\n"
                f"Тип данных: {type(data).__name__}"
            )
            
            print(f"> Успешно прочитан файл")
            return result
            
        except yaml.YAMLError as e:
            return f"Ошибка парсинга YAML: {e}"
        except Exception as e:
            return f"Ошибка при чтении файла: {e}"

    def _write_yaml(
        self, 
        file_path: str, 
        data: Dict[str, Any], 
        default_flow_style: bool = False,
        indent: int = 2,
        sort_keys: bool = False
    ) -> str:
        """
        Записывает данные в YAML-файл.
        """
        if data is None:
            return "Ошибка: данные для записи отсутствуют."

        print(f"> Записываю YAML-файл: '{file_path}'")
        
        try:
            # Создаем директорию, если её нет
            os.makedirs(os.path.dirname(file_path) or '.', exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(
                    data, 
                    f, 
                    allow_unicode=True,
                    default_flow_style=default_flow_style,
                    indent=indent,
                    sort_keys=sort_keys
                )
            
            # Читаем записанный файл для проверки
            with open(file_path, 'r', encoding='utf-8') as f:
                written_content = f.read()
            
            result = (
                f"YAML файл успешно записан: {file_path}\n"
                f"{'=' * 50}\n"
                f"Записано:\n{written_content}\n"
                f"{'=' * 50}\n"
                f"Размер файла: {os.path.getsize(file_path)} байт"
            )
            
            print(f"> Успешно записан файл")
            return result
            
        except Exception as e:
            return f"Ошибка при записи файла: {e}"

    def _validate_yaml(
        self, 
        data: Dict[str, Any], 
        schema: Dict[str, Any]
    ) -> str:
        """
        Валидирует данные по схеме Cerberus.
        """
        if data is None:
            return "Ошибка: данные для валидации отсутствуют."
        
        if schema is None:
            return "Ошибка: схема для валидации отсутствует."

        print(f"> Валидирую данные по схеме...")
        
        try:
            validator = Validator(schema)
            is_valid = validator.validate(data)
            
            # Форматируем результат
            errors = validator.errors
            
            if is_valid:
                result = (
                    f"✅ Валидация успешна!\n"
                    f"{'=' * 50}\n"
                    f"Данные соответствуют схеме.\n"
                    f"Размер данных: {len(data)} полей"
                )
                print(f"> Валидация прошла успешно")
            else:
                # Форматируем ошибки
                error_lines = []
                for field, field_errors in errors.items():
                    if isinstance(field_errors, list):
                        error_lines.append(f"  - {field}: {', '.join(field_errors)}")
                    else:
                        error_lines.append(f"  - {field}: {field_errors}")
                
                result = (
                    f"❌ Ошибка валидации!\n"
                    f"{'=' * 50}\n"
                    f"Найдены ошибки в данных:\n"
                    f"{chr(10).join(error_lines)}"
                )
                print(f"> Валидация не пройдена")
            
            return result
            
        except Exception as e:
            return f"Ошибка валидации: {e}"

    def _parse_yaml_string(self, yaml_string: str) -> str:
        """
        Парсит YAML-строку и возвращает данные.
        """
        if not yaml_string:
            return "Ошибка: YAML-строка пуста."

        print(f"> Парсю YAML-строку...")
        
        try:
            data = yaml.safe_load(yaml_string)
            
            if data is None:
                return "Строка пуста или содержит только комментарии."
            
            # Форматируем результат
            pretty_data = json.dumps(data, ensure_ascii=False, indent=2)
            
            result = (
                f"YAML строка успешно распарсена\n"
                f"{'=' * 50}\n"
                f"Результат:\n{pretty_data}\n"
                f"{'=' * 50}\n"
                f"Тип данных: {type(data).__name__}"
            )
            
            print(f"> Успешно распарсена строка")
            return result
            
        except yaml.YAMLError as e:
            return f"Ошибка парсинга YAML строки: {e}"
        except Exception as e:
            return f"Ошибка: {e}"

    def create_schema_example(self) -> str:
        """
        Возвращает пример схемы Cerberus для валидации конфигурации.
        """
        schema_example = {
            "app_name": {"type": "string", "required": True, "minlength": 1},
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
            },
            "logging": {
                "type": "dict",
                "required": False,
                "schema": {
                    "level": {"type": "string", "allowed": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]},
                    "file": {"type": "string", "required": False}
                }
            },
            "features": {
                "type": "list",
                "required": False,
                "schema": {"type": "string"}
            }
        }
        
        pretty_schema = json.dumps(schema_example, ensure_ascii=False, indent=2)
        
        return (
            f"Пример схемы Cerberus для валидации конфигурации:\n"
            f"{'=' * 50}\n"
            f"{pretty_schema}\n"
            f"{'=' * 50}\n"
            f"Используйте эту схему для валидации ваших конфигураций."
        )
