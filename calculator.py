# coding: utf-8
get_ipython().run_cell_magic('writefile', 'calculator.py', '')
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Union
import re
import operator

app = FastAPI(title="Калькулятор", description="Калькулятор с поддержкой сложных выражений")

current_expression = {
    "expression": "",
    "result": None
}

class SimpleOperation(BaseModel):
    a: Union[int, float]
    op: str  # +, -, *, /
    b: Union[int, float]

class ExpressionRequest(BaseModel):
    expression: str

operations = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv
}

def evaluate_simple_operation(a: Union[int, float], op: str, b: Union[int, float]) -> float:
    """Выполняет простую операцию над двумя числами"""
    if op not in operations:
        raise HTTPException(status_code=400, detail=f"Неподдерживаемая операция: {op}. Доступны: +, -, *, /")

    if op == '/' and b == 0:
        raise HTTPException(status_code=400, detail="Деление на ноль невозможно")

    result = operations[op](a, b)
    return result

def evaluate_complex_expression(expression: str) -> float:
    """
    Вычисляет сложное выражение с учетом приоритета операций
    Поддерживает: +, -, *, /, скобки
    """
    # Очищаем строку от пробелов
    expression = expression.replace(' ', '')

    if not expression:
        raise HTTPException(status_code=400, detail="Выражение не может быть пустым")

    def apply_operator(operators, values):
        """Применяет оператор к двум значениям"""
        operator_func = operators.pop()
        right = values.pop()
        left = values.pop()

        if operator_func == '+':
            values.append(left + right)
        elif operator_func == '-':
            values.append(left - right)
        elif operator_func == '*':
            values.append(left * right)
        elif operator_func == '/':
            if right == 0:
                raise HTTPException(status_code=400, detail="Деление на ноль невозможно")
            values.append(left / right)

    def precedence(op):
        """Возвращает приоритет операции"""
        if op in ('+', '-'):
            return 1
        if op in ('*', '/'):
            return 2
        return 0

    values = []
    operators = []
    i = 0

    while i < len(expression):
        # Обработка чисел
        if expression[i].isdigit() or expression[i] == '.':
            j = i
            while j < len(expression) and (expression[j].isdigit() or expression[j] == '.'):
                j += 1
            values.append(float(expression[i:j]))
            i = j
            continue

        # Обработка операторов и скобок
        elif expression[i] in '+-*/':
            while (operators and operators[-1] != '(' and 
                   precedence(operators[-1]) >= precedence(expression[i])):
                apply_operator(operators, values)
            operators.append(expression[i])

        elif expression[i] == '(':
            operators.append(expression[i])

        elif expression[i] == ')':
            while operators and operators[-1] != '(':
                apply_operator(operators, values)
            if operators and operators[-1] == '(':
                operators.pop()

        else:
            raise HTTPException(status_code=400, 
                              detail=f"Недопустимый символ в выражении: {expression[i]}")

        i += 1

    # Применяем оставшиеся операторы
    while operators:
        apply_operator(operators, values)

    if not values:
        raise HTTPException(status_code=400, detail="Некорректное выражение")

    return values[0]

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Добро пожаловать в калькулятор!",
        "endpoints": [
            "/add",
            "/subtract", 
            "/multiply",
            "/divide",
            "/simple-operation",
            "/set-expression",
            "/current-expression",
            "/evaluate"
        ]
    }

# 1. Простые операции
@app.post("/add")
async def add(a: float, b: float):
    """Сложение двух чисел"""
    result = a + b
    return {"operation": "addition", "a": a, "b": b, "result": result}

@app.post("/subtract")
async def subtract(a: float, b: float):
    """Вычитание двух чисел"""
    result = a - b
    return {"operation": "subtraction", "a": a, "b": b, "result": result}

@app.post("/multiply")
async def multiply(a: float, b: float):
    """Умножение двух чисел"""
    result = a * b
    return {"operation": "multiplication", "a": a, "b": b, "result": result}

@app.post("/divide")
async def divide(a: float, b: float):
    """Деление двух чисел"""
    if b == 0:
        raise HTTPException(status_code=400, detail="Деление на ноль невозможно")
    result = a / b
    return {"operation": "division", "a": a, "b": b, "result": result}

# 2. Операция с a, op, b
@app.post("/simple-operation")
async def simple_operation(operation: SimpleOperation):
    """Выполняет простую операцию над двумя числами"""
    result = evaluate_simple_operation(operation.a, operation.op, operation.b)
    return {
        "expression": f"{operation.a} {operation.op} {operation.b}",
        "result": result
    }

# 3. Создание сложного выражения
@app.post("/set-expression")
async def set_expression(request: ExpressionRequest):
    """Устанавливает текущее выражение для дальнейшего вычисления"""
    # Валидируем выражение перед сохранением
    try:
        # Проверяем, что выражение можно вычислить
        evaluate_complex_expression(request.expression)
        current_expression["expression"] = request.expression
        current_expression["result"] = None
        return {
            "message": "Выражение успешно установлено",
            "expression": current_expression["expression"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Некорректное выражение: {str(e)}")

# 4. Просмотр текущего выражения
@app.get("/current-expression")
async def get_current_expression():
    """Возвращает текущее состояние выражения"""
    if not current_expression["expression"]:
        return {
            "message": "Выражение не задано",
            "expression": "не определено",
            "result": "не вычислено"
        }

    return {
        "expression": current_expression["expression"],
        "result": current_expression["result"] if current_expression["result"] is not None else "еще не вычислено"
    }

# 5. Выполнение выражения
@app.post("/evaluate")
async def evaluate_current_expression():
    """Вычисляет результат текущего выражения"""
    if not current_expression["expression"]:
        raise HTTPException(status_code=400, detail="Выражение не задано. Сначала создайте выражение через /set-expression")

    try:
        result = evaluate_complex_expression(current_expression["expression"])
        current_expression["result"] = result
        return {
            "expression": current_expression["expression"],
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при вычислении: {str(e)}")

# 6. Дополнительный метод: вычисление любого переданного выражения
@app.post("/evaluate-expression")
async def evaluate_any_expression(request: ExpressionRequest):
    """Вычисляет любое переданное выражение без сохранения"""
    try:
        result = evaluate_complex_expression(request.expression)
        return {
            "expression": request.expression,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 7. Очистка текущего выражения
@app.delete("/clear-expression")
async def clear_expression():
    """Очищает текущее выражение"""
    current_expression["expression"] = ""
    current_expression["result"] = None
    return {"message": "Выражение очищено"}

get_ipython().run_line_magic('%writefile', 'calculator.py')
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Union
import re
import operator

app = FastAPI(title="Калькулятор", description="Калькулятор с поддержкой сложных выражений")

current_expression = {
    "expression": "",
    "result": None
}

class SimpleOperation(BaseModel):
    a: Union[int, float]
    op: str  # +, -, *, /
    b: Union[int, float]

class ExpressionRequest(BaseModel):
    expression: str

operations = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv
}

def evaluate_simple_operation(a: Union[int, float], op: str, b: Union[int, float]) -> float:
    """Выполняет простую операцию над двумя числами"""
    if op not in operations:
        raise HTTPException(status_code=400, detail=f"Неподдерживаемая операция: {op}. Доступны: +, -, *, /")

    if op == '/' and b == 0:
        raise HTTPException(status_code=400, detail="Деление на ноль невозможно")

    result = operations[op](a, b)
    return result

def evaluate_complex_expression(expression: str) -> float:
    """
    Вычисляет сложное выражение с учетом приоритета операций
    Поддерживает: +, -, *, /, скобки
    """
    # Очищаем строку от пробелов
    expression = expression.replace(' ', '')

    if not expression:
        raise HTTPException(status_code=400, detail="Выражение не может быть пустым")

    def apply_operator(operators, values):
        """Применяет оператор к двум значениям"""
        operator_func = operators.pop()
        right = values.pop()
        left = values.pop()

        if operator_func == '+':
            values.append(left + right)
        elif operator_func == '-':
            values.append(left - right)
        elif operator_func == '*':
            values.append(left * right)
        elif operator_func == '/':
            if right == 0:
                raise HTTPException(status_code=400, detail="Деление на ноль невозможно")
            values.append(left / right)

    def precedence(op):
        """Возвращает приоритет операции"""
        if op in ('+', '-'):
            return 1
        if op in ('*', '/'):
            return 2
        return 0

    values = []
    operators = []
    i = 0

    while i < len(expression):
        # Обработка чисел
        if expression[i].isdigit() or expression[i] == '.':
            j = i
            while j < len(expression) and (expression[j].isdigit() or expression[j] == '.'):
                j += 1
            values.append(float(expression[i:j]))
            i = j
            continue

        # Обработка операторов и скобок
        elif expression[i] in '+-*/':
            while (operators and operators[-1] != '(' and 
                   precedence(operators[-1]) >= precedence(expression[i])):
                apply_operator(operators, values)
            operators.append(expression[i])

        elif expression[i] == '(':
            operators.append(expression[i])

        elif expression[i] == ')':
            while operators and operators[-1] != '(':
                apply_operator(operators, values)
            if operators and operators[-1] == '(':
                operators.pop()

        else:
            raise HTTPException(status_code=400, 
                              detail=f"Недопустимый символ в выражении: {expression[i]}")

        i += 1

    # Применяем оставшиеся операторы
    while operators:
        apply_operator(operators, values)

    if not values:
        raise HTTPException(status_code=400, detail="Некорректное выражение")

    return values[0]

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Добро пожаловать в калькулятор!",
        "endpoints": [
            "/add",
            "/subtract", 
            "/multiply",
            "/divide",
            "/simple-operation",
            "/set-expression",
            "/current-expression",
            "/evaluate"
        ]
    }

# 1. Простые операции
@app.post("/add")
async def add(a: float, b: float):
    """Сложение двух чисел"""
    result = a + b
    return {"operation": "addition", "a": a, "b": b, "result": result}

@app.post("/subtract")
async def subtract(a: float, b: float):
    """Вычитание двух чисел"""
    result = a - b
    return {"operation": "subtraction", "a": a, "b": b, "result": result}

@app.post("/multiply")
async def multiply(a: float, b: float):
    """Умножение двух чисел"""
    result = a * b
    return {"operation": "multiplication", "a": a, "b": b, "result": result}

@app.post("/divide")
async def divide(a: float, b: float):
    """Деление двух чисел"""
    if b == 0:
        raise HTTPException(status_code=400, detail="Деление на ноль невозможно")
    result = a / b
    return {"operation": "division", "a": a, "b": b, "result": result}

# 2. Операция с a, op, b
@app.post("/simple-operation")
async def simple_operation(operation: SimpleOperation):
    """Выполняет простую операцию над двумя числами"""
    result = evaluate_simple_operation(operation.a, operation.op, operation.b)
    return {
        "expression": f"{operation.a} {operation.op} {operation.b}",
        "result": result
    }

# 3. Создание сложного выражения
@app.post("/set-expression")
async def set_expression(request: ExpressionRequest):
    """Устанавливает текущее выражение для дальнейшего вычисления"""
    # Валидируем выражение перед сохранением
    try:
        # Проверяем, что выражение можно вычислить
        evaluate_complex_expression(request.expression)
        current_expression["expression"] = request.expression
        current_expression["result"] = None
        return {
            "message": "Выражение успешно установлено",
            "expression": current_expression["expression"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Некорректное выражение: {str(e)}")

# 4. Просмотр текущего выражения
@app.get("/current-expression")
async def get_current_expression():
    """Возвращает текущее состояние выражения"""
    if not current_expression["expression"]:
        return {
            "message": "Выражение не задано",
            "expression": "не определено",
            "result": "не вычислено"
        }

    return {
        "expression": current_expression["expression"],
        "result": current_expression["result"] if current_expression["result"] is not None else "еще не вычислено"
    }

# 5. Выполнение выражения
@app.post("/evaluate")
async def evaluate_current_expression():
    """Вычисляет результат текущего выражения"""
    if not current_expression["expression"]:
        raise HTTPException(status_code=400, detail="Выражение не задано. Сначала создайте выражение через /set-expression")

    try:
        result = evaluate_complex_expression(current_expression["expression"])
        current_expression["result"] = result
        return {
            "expression": current_expression["expression"],
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при вычислении: {str(e)}")

# 6. Дополнительный метод: вычисление любого переданного выражения
@app.post("/evaluate-expression")
async def evaluate_any_expression(request: ExpressionRequest):
    """Вычисляет любое переданное выражение без сохранения"""
    try:
        result = evaluate_complex_expression(request.expression)
        return {
            "expression": request.expression,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 7. Очистка текущего выражения
@app.delete("/clear-expression")
async def clear_expression():
    """Очищает текущее выражение"""
    current_expression["expression"] = ""
    current_expression["result"] = None
    return {"message": "Выражение очищено"}

get_ipython().run_line_magic('%writefile', 'calculator.py')
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Union
import re
import operator

app = FastAPI(title="Калькулятор", description="Калькулятор с поддержкой сложных выражений")

current_expression = {
    "expression": "",
    "result": None
}

class SimpleOperation(BaseModel):
    a: Union[int, float]
    op: str  # +, -, *, /
    b: Union[int, float]

class ExpressionRequest(BaseModel):
    expression: str

operations = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv
}

def evaluate_simple_operation(a: Union[int, float], op: str, b: Union[int, float]) -> float:
    """Выполняет простую операцию над двумя числами"""
    if op not in operations:
        raise HTTPException(status_code=400, detail=f"Неподдерживаемая операция: {op}. Доступны: +, -, *, /")

    if op == '/' and b == 0:
        raise HTTPException(status_code=400, detail="Деление на ноль невозможно")

    result = operations[op](a, b)
    return result

def evaluate_complex_expression(expression: str) -> float:
    """
    Вычисляет сложное выражение с учетом приоритета операций
    Поддерживает: +, -, *, /, скобки
    """
    # Очищаем строку от пробелов
    expression = expression.replace(' ', '')

    if not expression:
        raise HTTPException(status_code=400, detail="Выражение не может быть пустым")

    def apply_operator(operators, values):
        """Применяет оператор к двум значениям"""
        operator_func = operators.pop()
        right = values.pop()
        left = values.pop()

        if operator_func == '+':
            values.append(left + right)
        elif operator_func == '-':
            values.append(left - right)
        elif operator_func == '*':
            values.append(left * right)
        elif operator_func == '/':
            if right == 0:
                raise HTTPException(status_code=400, detail="Деление на ноль невозможно")
            values.append(left / right)

    def precedence(op):
        """Возвращает приоритет операции"""
        if op in ('+', '-'):
            return 1
        if op in ('*', '/'):
            return 2
        return 0

    values = []
    operators = []
    i = 0

    while i < len(expression):
        # Обработка чисел
        if expression[i].isdigit() or expression[i] == '.':
            j = i
            while j < len(expression) and (expression[j].isdigit() or expression[j] == '.'):
                j += 1
            values.append(float(expression[i:j]))
            i = j
            continue

        # Обработка операторов и скобок
        elif expression[i] in '+-*/':
            while (operators and operators[-1] != '(' and 
                   precedence(operators[-1]) >= precedence(expression[i])):
                apply_operator(operators, values)
            operators.append(expression[i])

        elif expression[i] == '(':
            operators.append(expression[i])

        elif expression[i] == ')':
            while operators and operators[-1] != '(':
                apply_operator(operators, values)
            if operators and operators[-1] == '(':
                operators.pop()

        else:
            raise HTTPException(status_code=400, 
                              detail=f"Недопустимый символ в выражении: {expression[i]}")

        i += 1

    # Применяем оставшиеся операторы
    while operators:
        apply_operator(operators, values)

    if not values:
        raise HTTPException(status_code=400, detail="Некорректное выражение")

    return values[0]

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Добро пожаловать в калькулятор!",
        "endpoints": [
            "/add",
            "/subtract", 
            "/multiply",
            "/divide",
            "/simple-operation",
            "/set-expression",
            "/current-expression",
            "/evaluate"
        ]
    }

# 1. Простые операции
@app.post("/add")
async def add(a: float, b: float):
    """Сложение двух чисел"""
    result = a + b
    return {"operation": "addition", "a": a, "b": b, "result": result}

@app.post("/subtract")
async def subtract(a: float, b: float):
    """Вычитание двух чисел"""
    result = a - b
    return {"operation": "subtraction", "a": a, "b": b, "result": result}

@app.post("/multiply")
async def multiply(a: float, b: float):
    """Умножение двух чисел"""
    result = a * b
    return {"operation": "multiplication", "a": a, "b": b, "result": result}

@app.post("/divide")
async def divide(a: float, b: float):
    """Деление двух чисел"""
    if b == 0:
        raise HTTPException(status_code=400, detail="Деление на ноль невозможно")
    result = a / b
    return {"operation": "division", "a": a, "b": b, "result": result}

# 2. Операция с a, op, b
@app.post("/simple-operation")
async def simple_operation(operation: SimpleOperation):
    """Выполняет простую операцию над двумя числами"""
    result = evaluate_simple_operation(operation.a, operation.op, operation.b)
    return {
        "expression": f"{operation.a} {operation.op} {operation.b}",
        "result": result
    }

# 3. Создание сложного выражения
@app.post("/set-expression")
async def set_expression(request: ExpressionRequest):
    """Устанавливает текущее выражение для дальнейшего вычисления"""
    # Валидируем выражение перед сохранением
    try:
        # Проверяем, что выражение можно вычислить
        evaluate_complex_expression(request.expression)
        current_expression["expression"] = request.expression
        current_expression["result"] = None
        return {
            "message": "Выражение успешно установлено",
            "expression": current_expression["expression"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Некорректное выражение: {str(e)}")

# 4. Просмотр текущего выражения
@app.get("/current-expression")
async def get_current_expression():
    """Возвращает текущее состояние выражения"""
    if not current_expression["expression"]:
        return {
            "message": "Выражение не задано",
            "expression": "не определено",
            "result": "не вычислено"
        }

    return {
        "expression": current_expression["expression"],
        "result": current_expression["result"] if current_expression["result"] is not None else "еще не вычислено"
    }

# 5. Выполнение выражения
@app.post("/evaluate")
async def evaluate_current_expression():
    """Вычисляет результат текущего выражения"""
    if not current_expression["expression"]:
        raise HTTPException(status_code=400, detail="Выражение не задано. Сначала создайте выражение через /set-expression")

    try:
        result = evaluate_complex_expression(current_expression["expression"])
        current_expression["result"] = result
        return {
            "expression": current_expression["expression"],
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при вычислении: {str(e)}")

# 6. Дополнительный метод: вычисление любого переданного выражения
@app.post("/evaluate-expression")
async def evaluate_any_expression(request: ExpressionRequest):
    """Вычисляет любое переданное выражение без сохранения"""
    try:
        result = evaluate_complex_expression(request.expression)
        return {
            "expression": request.expression,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 7. Очистка текущего выражения
@app.delete("/clear-expression")
async def clear_expression():
    """Очищает текущее выражение"""
    current_expression["expression"] = ""
    current_expression["result"] = None
    return {"message": "Выражение очищено"}
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Union
import re
import operator

app = FastAPI(title="Калькулятор", description="Калькулятор с поддержкой сложных выражений")

current_expression = {
    "expression": "",
    "result": None
}

class SimpleOperation(BaseModel):
    a: Union[int, float]
    op: str  # +, -, *, /
    b: Union[int, float]

class ExpressionRequest(BaseModel):
    expression: str

operations = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv
}

def evaluate_simple_operation(a: Union[int, float], op: str, b: Union[int, float]) -> float:
    """Выполняет простую операцию над двумя числами"""
    if op not in operations:
        raise HTTPException(status_code=400, detail=f"Неподдерживаемая операция: {op}. Доступны: +, -, *, /")

    if op == '/' and b == 0:
        raise HTTPException(status_code=400, detail="Деление на ноль невозможно")

    result = operations[op](a, b)
    return result

def evaluate_complex_expression(expression: str) -> float:
    """
    Вычисляет сложное выражение с учетом приоритета операций
    Поддерживает: +, -, *, /, скобки
    """
    # Очищаем строку от пробелов
    expression = expression.replace(' ', '')

    if not expression:
        raise HTTPException(status_code=400, detail="Выражение не может быть пустым")

    def apply_operator(operators, values):
        """Применяет оператор к двум значениям"""
        operator_func = operators.pop()
        right = values.pop()
        left = values.pop()

        if operator_func == '+':
            values.append(left + right)
        elif operator_func == '-':
            values.append(left - right)
        elif operator_func == '*':
            values.append(left * right)
        elif operator_func == '/':
            if right == 0:
                raise HTTPException(status_code=400, detail="Деление на ноль невозможно")
            values.append(left / right)

    def precedence(op):
        """Возвращает приоритет операции"""
        if op in ('+', '-'):
            return 1
        if op in ('*', '/'):
            return 2
        return 0

    values = []
    operators = []
    i = 0

    while i < len(expression):
        # Обработка чисел
        if expression[i].isdigit() or expression[i] == '.':
            j = i
            while j < len(expression) and (expression[j].isdigit() or expression[j] == '.'):
                j += 1
            values.append(float(expression[i:j]))
            i = j
            continue

        # Обработка операторов и скобок
        elif expression[i] in '+-*/':
            while (operators and operators[-1] != '(' and 
                   precedence(operators[-1]) >= precedence(expression[i])):
                apply_operator(operators, values)
            operators.append(expression[i])

        elif expression[i] == '(':
            operators.append(expression[i])

        elif expression[i] == ')':
            while operators and operators[-1] != '(':
                apply_operator(operators, values)
            if operators and operators[-1] == '(':
                operators.pop()

        else:
            raise HTTPException(status_code=400, 
                              detail=f"Недопустимый символ в выражении: {expression[i]}")

        i += 1

    # Применяем оставшиеся операторы
    while operators:
        apply_operator(operators, values)

    if not values:
        raise HTTPException(status_code=400, detail="Некорректное выражение")

    return values[0]

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Добро пожаловать в калькулятор!",
        "endpoints": [
            "/add",
            "/subtract", 
            "/multiply",
            "/divide",
            "/simple-operation",
            "/set-expression",
            "/current-expression",
            "/evaluate"
        ]
    }

# 1. Простые операции
@app.post("/add")
async def add(a: float, b: float):
    """Сложение двух чисел"""
    result = a + b
    return {"operation": "addition", "a": a, "b": b, "result": result}

@app.post("/subtract")
async def subtract(a: float, b: float):
    """Вычитание двух чисел"""
    result = a - b
    return {"operation": "subtraction", "a": a, "b": b, "result": result}

@app.post("/multiply")
async def multiply(a: float, b: float):
    """Умножение двух чисел"""
    result = a * b
    return {"operation": "multiplication", "a": a, "b": b, "result": result}

@app.post("/divide")
async def divide(a: float, b: float):
    """Деление двух чисел"""
    if b == 0:
        raise HTTPException(status_code=400, detail="Деление на ноль невозможно")
    result = a / b
    return {"operation": "division", "a": a, "b": b, "result": result}

# 2. Операция с a, op, b
@app.post("/simple-operation")
async def simple_operation(operation: SimpleOperation):
    """Выполняет простую операцию над двумя числами"""
    result = evaluate_simple_operation(operation.a, operation.op, operation.b)
    return {
        "expression": f"{operation.a} {operation.op} {operation.b}",
        "result": result
    }

# 3. Создание сложного выражения
@app.post("/set-expression")
async def set_expression(request: ExpressionRequest):
    """Устанавливает текущее выражение для дальнейшего вычисления"""
    # Валидируем выражение перед сохранением
    try:
        # Проверяем, что выражение можно вычислить
        evaluate_complex_expression(request.expression)
        current_expression["expression"] = request.expression
        current_expression["result"] = None
        return {
            "message": "Выражение успешно установлено",
            "expression": current_expression["expression"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Некорректное выражение: {str(e)}")

# 4. Просмотр текущего выражения
@app.get("/current-expression")
async def get_current_expression():
    """Возвращает текущее состояние выражения"""
    if not current_expression["expression"]:
        return {
            "message": "Выражение не задано",
            "expression": "не определено",
            "result": "не вычислено"
        }

    return {
        "expression": current_expression["expression"],
        "result": current_expression["result"] if current_expression["result"] is not None else "еще не вычислено"
    }

# 5. Выполнение выражения
@app.post("/evaluate")
async def evaluate_current_expression():
    """Вычисляет результат текущего выражения"""
    if not current_expression["expression"]:
        raise HTTPException(status_code=400, detail="Выражение не задано. Сначала создайте выражение через /set-expression")

    try:
        result = evaluate_complex_expression(current_expression["expression"])
        current_expression["result"] = result
        return {
            "expression": current_expression["expression"],
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при вычислении: {str(e)}")

# 6. Дополнительный метод: вычисление любого переданного выражения
@app.post("/evaluate-expression")
async def evaluate_any_expression(request: ExpressionRequest):
    """Вычисляет любое переданное выражение без сохранения"""
    try:
        result = evaluate_complex_expression(request.expression)
        return {
            "expression": request.expression,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 7. Очистка текущего выражения
@app.delete("/clear-expression")
async def clear_expression():
    """Очищает текущее выражение"""
    current_expression["expression"] = ""
    current_expression["result"] = None
    return {"message": "Выражение очищено"}

get_ipython().run_line_magic('%writefile', 'calculator.py')
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Union
import re
import operator

app = FastAPI(title="Калькулятор", description="Калькулятор с поддержкой сложных выражений")

current_expression = {
    "expression": "",
    "result": None
}

class SimpleOperation(BaseModel):
    a: Union[int, float]
    op: str  # +, -, *, /
    b: Union[int, float]

class ExpressionRequest(BaseModel):
    expression: str

operations = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv
}

def evaluate_simple_operation(a: Union[int, float], op: str, b: Union[int, float]) -> float:
    """Выполняет простую операцию над двумя числами"""
    if op not in operations:
        raise HTTPException(status_code=400, detail=f"Неподдерживаемая операция: {op}. Доступны: +, -, *, /")

    if op == '/' and b == 0:
        raise HTTPException(status_code=400, detail="Деление на ноль невозможно")

    result = operations[op](a, b)
    return result

def evaluate_complex_expression(expression: str) -> float:
    """
    Вычисляет сложное выражение с учетом приоритета операций
    Поддерживает: +, -, *, /, скобки
    """
    # Очищаем строку от пробелов
    expression = expression.replace(' ', '')

    if not expression:
        raise HTTPException(status_code=400, detail="Выражение не может быть пустым")

    def apply_operator(operators, values):
        """Применяет оператор к двум значениям"""
        operator_func = operators.pop()
        right = values.pop()
        left = values.pop()

        if operator_func == '+':
            values.append(left + right)
        elif operator_func == '-':
            values.append(left - right)
        elif operator_func == '*':
            values.append(left * right)
        elif operator_func == '/':
            if right == 0:
                raise HTTPException(status_code=400, detail="Деление на ноль невозможно")
            values.append(left / right)

    def precedence(op):
        """Возвращает приоритет операции"""
        if op in ('+', '-'):
            return 1
        if op in ('*', '/'):
            return 2
        return 0

    values = []
    operators = []
    i = 0

    while i < len(expression):
        # Обработка чисел
        if expression[i].isdigit() or expression[i] == '.':
            j = i
            while j < len(expression) and (expression[j].isdigit() or expression[j] == '.'):
                j += 1
            values.append(float(expression[i:j]))
            i = j
            continue

        # Обработка операторов и скобок
        elif expression[i] in '+-*/':
            while (operators and operators[-1] != '(' and 
                   precedence(operators[-1]) >= precedence(expression[i])):
                apply_operator(operators, values)
            operators.append(expression[i])

        elif expression[i] == '(':
            operators.append(expression[i])

        elif expression[i] == ')':
            while operators and operators[-1] != '(':
                apply_operator(operators, values)
            if operators and operators[-1] == '(':
                operators.pop()

        else:
            raise HTTPException(status_code=400, 
                              detail=f"Недопустимый символ в выражении: {expression[i]}")

        i += 1

    # Применяем оставшиеся операторы
    while operators:
        apply_operator(operators, values)

    if not values:
        raise HTTPException(status_code=400, detail="Некорректное выражение")

    return values[0]

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Добро пожаловать в калькулятор!",
        "endpoints": [
            "/add",
            "/subtract", 
            "/multiply",
            "/divide",
            "/simple-operation",
            "/set-expression",
            "/current-expression",
            "/evaluate"
        ]
    }

# 1. Простые операции
@app.post("/add")
async def add(a: float, b: float):
    """Сложение двух чисел"""
    result = a + b
    return {"operation": "addition", "a": a, "b": b, "result": result}

@app.post("/subtract")
async def subtract(a: float, b: float):
    """Вычитание двух чисел"""
    result = a - b
    return {"operation": "subtraction", "a": a, "b": b, "result": result}

@app.post("/multiply")
async def multiply(a: float, b: float):
    """Умножение двух чисел"""
    result = a * b
    return {"operation": "multiplication", "a": a, "b": b, "result": result}

@app.post("/divide")
async def divide(a: float, b: float):
    """Деление двух чисел"""
    if b == 0:
        raise HTTPException(status_code=400, detail="Деление на ноль невозможно")
    result = a / b
    return {"operation": "division", "a": a, "b": b, "result": result}

# 2. Операция с a, op, b
@app.post("/simple-operation")
async def simple_operation(operation: SimpleOperation):
    """Выполняет простую операцию над двумя числами"""
    result = evaluate_simple_operation(operation.a, operation.op, operation.b)
    return {
        "expression": f"{operation.a} {operation.op} {operation.b}",
        "result": result
    }

# 3. Создание сложного выражения
@app.post("/set-expression")
async def set_expression(request: ExpressionRequest):
    """Устанавливает текущее выражение для дальнейшего вычисления"""
    # Валидируем выражение перед сохранением
    try:
        # Проверяем, что выражение можно вычислить
        evaluate_complex_expression(request.expression)
        current_expression["expression"] = request.expression
        current_expression["result"] = None
        return {
            "message": "Выражение успешно установлено",
            "expression": current_expression["expression"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Некорректное выражение: {str(e)}")

# 4. Просмотр текущего выражения
@app.get("/current-expression")
async def get_current_expression():
    """Возвращает текущее состояние выражения"""
    if not current_expression["expression"]:
        return {
            "message": "Выражение не задано",
            "expression": "не определено",
            "result": "не вычислено"
        }

    return {
        "expression": current_expression["expression"],
        "result": current_expression["result"] if current_expression["result"] is not None else "еще не вычислено"
    }

# 5. Выполнение выражения
@app.post("/evaluate")
async def evaluate_current_expression():
    """Вычисляет результат текущего выражения"""
    if not current_expression["expression"]:
        raise HTTPException(status_code=400, detail="Выражение не задано. Сначала создайте выражение через /set-expression")

    try:
        result = evaluate_complex_expression(current_expression["expression"])
        current_expression["result"] = result
        return {
            "expression": current_expression["expression"],
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при вычислении: {str(e)}")

# 6. Дополнительный метод: вычисление любого переданного выражения
@app.post("/evaluate-expression")
async def evaluate_any_expression(request: ExpressionRequest):
    """Вычисляет любое переданное выражение без сохранения"""
    try:
        result = evaluate_complex_expression(request.expression)
        return {
            "expression": request.expression,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 7. Очистка текущего выражения
@app.delete("/clear-expression")
async def clear_expression():
    """Очищает текущее выражение"""
    current_expression["expression"] = ""
    current_expression["result"] = None
    return {"message": "Выражение очищено"}

get_ipython().run_line_magic('save', 'calculator.py 1-10')
