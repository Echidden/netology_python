import mmap
import os
import multiprocessing

def producer(shared_mem):
    # Данные для отправки
    data = "Привет от производителя!"
    
    # Преобразуем строку в байты
    data_bytes = data.encode('utf-8')
    
    # Записываем данные в общую память
    shared_mem.seek(0)
    shared_mem.write(data_bytes)
    shared_mem.flush()
    
    print(f"Производитель отправил: {data}")

def consumer(shared_mem):
    # Читаем данные из общей памяти
    shared_mem.seek(0)
    data_bytes = shared_mem.read(1024)  # Читаем до 1024 байт
    
    # Находим первый нулевой байт (конец строки)
    try:
        null_pos = data_bytes.index(b'\x00')
        data_bytes = data_bytes[:null_pos]
    except ValueError:
        pass
    
    # Преобразуем байты обратно в строку
    data = data_bytes.decode('utf-8').strip()
    
    print(f"Потребитель получил: {data}")

if __name__ == '__main__':
    # Создаем временный файл для общей памяти
    with open('temp_mmap', 'wb+') as f:
        # Записываем нулевые байты для инициализации файла
        f.write(b'\x00' * 1024)
        f.flush()
        
        # Создаем mmap объект
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE) as shared_mem:
            # Создаем процессы
            p_producer = multiprocessing.Process(target=producer, args=(shared_mem,))
            p_consumer = multiprocessing.Process(target=consumer, args=(shared_mem,))
            
            # Запускаем процессы
            p_producer.start()
            p_consumer.start()
            
            # Ждем завершения процессов
            p_producer.join()
            p_consumer.join()
    
    # Удаляем временный файл
    os.remove('temp_mmap')