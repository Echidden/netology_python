import re

def is_valid_car_number(car_id):
    
    if re.match(r'([АВЕКМНОРСТУХ]\s*\d{3}\s*[АВЕКМНОРСТУХ]{2}\s*\d{2,3})|([АВЕКМНОРСТУХ]{2}\s*\d{3}\s*\d{2,3})', car_id, re.IGNORECASE):  # Используем IGNORECASE для игнорирования регистра
        # Если номер валиден, извлекаем номер и регион
        number = car_id[:-2]  # все кроме последних двух или трех символов
        region = car_id[-2:]   # последние два символа
        return f"Номер {number} валиден. Регион: {region}."
    else:
        return "Номер не валиден."

# Запрос ввода от пользователя
car_id = input("Введите номер автомобиля для проверки: ")
result = is_valid_car_number(car_id)
print(result)
