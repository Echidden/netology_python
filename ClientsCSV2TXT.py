"""Перевод клиентов из csv в формат TXT"""

"""Определяем функцию, формирующую строку с информацией о пользователе и создаем словарик"""
def get_str_to_write(name, device, user_agent, sex, age, money, region):
    mapping = {"female": "женского", "male": "мужского",
               "mobile": "мобильного", "desktop": "ПКшного", "tablet": "планшетного"}
    formatted_sex = mapping.get(sex, "неизвестного")
    formatted_device = mapping.get(device, "неизвестного")
    return ("Пользователем {name} {formatted_sex} пола, {age} лет была совершена покупка на {money} у.е. "
     "с {formatted_device} браузера {user_agent}. Регион, из которого совершалась покупка: {region}.\n\n").format(
        name=name, formatted_device=formatted_device, user_agent=user_agent,
        formatted_sex=formatted_sex, age=age, money=money, region=region)

"""функция конвертации из CSV в TXT"""
def main():
    print('Запуск перевода .csv в .txt')
    with open('web_clients_correct.csv') as raw_file, open ('ClientsConverted.txt', 'w') as result_file:
        for line in raw_file:
            try:
                name, device, user_agent, sex, age, money, region = line.strip().split(',')
            except Exception as exception:
                print(f'Что-то пошло не так, пропускаем строчку {line.strip()}. Ошибка: {exception}')

            result_file.write(get_str_to_write(name, device, user_agent, sex, age, money, region))
    print('Конвертация файла успешно завершена!')

if __name__ == '__main__':
    main()