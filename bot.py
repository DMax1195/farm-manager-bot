import os
import gspread # Новый импорт
import json
from auth import get_google_credentials # Импорт служебной функции
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from typing import List, Tuple
# ... (остальные импорты) ...

# --------------------------
# НОВЫЕ КОНСТАНТЫ
# --------------------------
# Имя листа в вашей Google Таблице, куда сохраняются алерты
SHEET_NAME = "FarmManager Alerts" 
WORKSHEET_NAME = "Лист1" # Имя листа, который содержит данные (часто "Лист1" или "Sheet1")
HEADER = ["culture", "baseline", "target", "percentage_change"]

# --------------------------
# ФУНКЦИИ БД (Полная замена логики sqlite3)
# --------------------------

def connect_to_sheets():
    """Авторизация и подключение к Google Таблице."""
    try:
        # Получаем путь к временному ключу
        creds_file = get_google_credentials()
        if not creds_file:
            return None, None
            
        # Авторизация gspread с использованием временного файла
        gc = gspread.service_account(filename=creds_file)
        
        # Открываем таблицу по имени
        spreadsheet = gc.open(SHEET_NAME)
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
        
        return worksheet
    except Exception as e:
        print(f"Ошибка подключения к Google Sheets: {e}")
        return None

def init_db():
    """Проверка заголовков в Google Таблице."""
    worksheet = connect_to_sheets()
    if worksheet:
        # Проверяем, что заголовки в таблице установлены
        if worksheet.row_values(1) != HEADER:
            print("Предупреждение: Заголовки в таблице не совпадают. Установите их вручную.")
        return True
    return False

def add_alert_to_db(culture: str, baseline: float, target: float, percentage_change: float):
    """Добавление или обновление уведомления в Google Таблице."""
    worksheet = connect_to_sheets()
    if not worksheet: return
    
    try:
        # 1. Считываем все данные для поиска существующей записи
        data = worksheet.get_all_records()
        
        new_row = [culture, baseline, target, percentage_change]
        
        # 2. Ищем существующую запись по полю 'culture'
        row_index_to_update = 0
        for i, row in enumerate(data):
            if row['culture'] == culture:
                # Индекс в gspread начинается с 1, плюс 1 строка заголовков
                row_index_to_update = i + 2 
                break
        
        if row_index_to_update:
            # Обновляем существующую строку
            worksheet.update(f'A{row_index_to_update}', [new_row])
        else:
            # Добавляем новую строку в конец
            worksheet.append_row(new_row, value_input_option='USER_ENTERED')
            
    except Exception as e:
        print(f"Ошибка добавления алерта в Google Sheets: {e}")

def get_all_alerts() -> List[Tuple[str, float, float, float]]:
    """Получение всех уведомлений из Google Таблицы."""
    worksheet = connect_to_sheets()
    if not worksheet: return []
    
    try:
        # Получаем все записи в виде списка словарей
        data = worksheet.get_all_records()
        alerts = []
        
        # Преобразуем словари в кортежи, как это делал sqlite3
        for row in data:
            alerts.append((
                row.get('culture', ''),
                float(row.get('baseline', 0)),
                float(row.get('target', 0)),
                float(row.get('percentage_change', 0))
            ))
        return alerts
        
    except Exception as e:
        print(f"Ошибка получения алертов из Google Sheets: {e}")
        return []

# --------------------------
# ЛОГИКА WEBHOOK (Меняем только запуск)
# --------------------------

# Функция init_db() теперь вызывается в on_startup в create_app()

# ... (Остальной код, включая обработчики /addalert и /showalerts, остается прежним) ...