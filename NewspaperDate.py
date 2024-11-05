from datetime import datetime

def convert_date(date_str):
    formats = [
        ("%A, %B %d, %Y", "The Moscow Times"),
        ("%A, %d.%m.%y", "The Guardian"),
        ("%A, %d %B %Y", "Daily News")
    ]
    
    for fmt, newspaper in formats:
        try:
            # Пытаемся преобразовать строку в объект datetime
            return datetime.strptime(date_str, fmt), newspaper
        except ValueError:
            continue
    return None

def main():
    print("Введите дату в формате газет или 'bye' для выхода:")
    
    while True:
        user_input = input("Введите дату: ")
        
        if user_input.lower() == 'bye':
            print("Хорошего денечка!")
            break
        
        result = convert_date(user_input)
        
        if result:
            date_obj, newspaper = result
            print(f"Дата для '{newspaper}': {date_obj}")
        else:
            print("Странный какой-то формат даты. Попробуйте еще раз.")

if __name__ == "__main__":
    main()