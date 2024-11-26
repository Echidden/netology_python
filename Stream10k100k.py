import time
from concurrent.futures import ThreadPoolExecutor

# Формулы
def formula1(x):
    return x**x - x**x + x**4 - x**5 + x + x

def formula2(x):
    return x + x

def compute_results(iterations):
    results1 = []
    results2 = []
    
    # параллельные вычисления
    with ThreadPoolExecutor() as executor:
        futures1 = [executor.submit(formula1, x) for x in range(iterations)]
        futures2 = [executor.submit(formula2, x) for x in range(iterations)]
        
        # Получаем результаты формулы 1
        start_time1 = time.time()
        for future in futures1:
            results1.append(future.result())
        duration1 = time.time() - start_time1
        
        # Получаем результаты формулы 2
        start_time2 = time.time()
        for future in futures2:
            results2.append(future.result())
        duration2 = time.time() - start_time2
        
    # Вычисляем итоговый результат по формуле 3
    start_time3 = time.time()
    duration3 = time.time() - start_time3
    
    return duration1, duration2, duration3

# Итерации
iterations_list = [10000, 100000]

# Выполнение и вывод результатов
for iterations in iterations_list:
    print(f"Iterations: {iterations}")
    duration1, duration2, duration3 = compute_results(iterations)
    
    print(f"Duration for formula 1: {duration1:.4f} seconds")
    print(f"Duration for formula 2: {duration2:.4f} seconds")
    print(f"Duration for formula 3: {duration3:.4f} seconds")
