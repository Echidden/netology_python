def main():
    items = input("Введите список товаров через запятую: ").split(',')
    items = [item.strip() for item in items]

    prices = {}
    while True:
        store_name = input("Введите название магазина (или 'стоп' для завершения ввода): ")
        if store_name.lower() == 'стоп':
            break
        
        store_prices = []
        for item in items:
            price = float(input(f"Введите цену товара '{item}' в магазине '{store_name}': "))
            store_prices.append(price)
        
        prices[store_name] = store_prices

    total_costs = {store: sum(prices[store]) for store in prices}

    print("\nОбщая стоимость покупок в каждом магазине:")
    for store, total in total_costs.items():
        print(f"{store}: {total:.2f} руб.")

    min_cost = min(total_costs.values())
    best_store = [store for store, total in total_costs.items() if total == min_cost]

    print(f"\nВы можете сэкономить больше всего, купив товары в магазине: {', '.join(best_store)} (стоимость: {min_cost:.2f} руб.)")

if __name__ == "__main__":
    main()