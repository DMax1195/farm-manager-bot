import os
import json
import tempfile

def get_google_credentials():
    """Считывает учетные данные из переменной окружения Vercel и сохраняет их во временный файл."""
    
    # 1. Получаем JSON-строку из переменной окружения Vercel
    credentials_json = os.getenv("GSPREAD_CREDENTIALS")
    
    if not credentials_json:
        print("Ошибка: Переменная GSPREAD_CREDENTIALS не найдена.")
        return None

    # 2. Создаем временный файл, так как gspread не может работать напрямую со строкой
    try:
        # json.loads преобразует строку JSON в словарь Python
        credentials_dict = json.loads(credentials_json) 
        
        # Создаем временный файл
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        
        # Записываем данные в этот файл
        json.dump(credentials_dict, temp_file)
        temp_file.close()
        
        # 3. Возвращаем путь к временному файлу
        return temp_file.name
        
    except json.JSONDecodeError:
        print("Ошибка: Неверный формат JSON в GSPREAD_CREDENTIALS.")
        return None