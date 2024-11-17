import json

if __name__ == '__main__':
    purchase_log = {}
    with open('purchase_log.txt', 'r') as file:
        for line in file:
            some_line = json.loads(line)
            user_id_category = some_line['user_id']
            category = some_line['category']
            purchase_log[user_id_category] = category
    with open('funnel.csv', 'w') as result_file:
        with open('visit_log__1___2_.csv', 'r') as visit_file:
            for visit_line in visit_file:
                user_id, from_order = visit_line.split(',')
                category = purchase_log.get(user_id)
                if category:
                    result_file.write(f'{user_id},{from_order.strip()},{category}' + '\n')
                else:
                    print(f'Пропускаем {user_id}, нет в базе')