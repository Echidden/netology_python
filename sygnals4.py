import matplotlib.pyplot as plt
import numpy as np

# функция для преобразования синусоиды в прямоугольную форму с пределами 0 - 1
def my_sign(x, k, delta):
  return np.sin(k*x+delta)>0 # k - частота сигнала; delta - смещение сигнала (в данной работе используется)

plt.figure(figsize=(25,10))

plt.yticks([])
plt.xticks([])
text = ["0", "1"] * 7
y = 0
for label in text:
  plt.text(-10, y, label)
  y += 0.75

# формируем массивы меток времени и сигналов X1, X2, X3, X4
t = np.arange(0, 1000, 1)
x1 = my_sign(t, 0.1, 0)
x2 = my_sign(t, 0.06, 0)
x3 = my_sign(t, 0.02, 0)
x4 = my_sign(t, 0.01, 0)
x1[0], x2[0], x3[0], x4[0] = True, True, True, True

# формируем инверсию сигналов
not_x1 = np.ones(len(t)) - x1
not_x2 = np.ones(len(t)) - x2
not_x3 = np.ones(len(t)) - x3
not_x4 = np.ones(len(t)) - x4

# формируем сигналы a1, a2, E0 как результат логических формул
a1 = (not_x1*not_x2*x3)+(not_x1*not_x2*not_x3*x4)+3 # задаем смещение сигналу, чтобы поднять его относительно других
a2 = (not_x1*x2)+(not_x1*not_x2*not_x3*x4)+1.5
E0 = not_x1*not_x2*not_x3*not_x4

# рисуем графики
plt.plot(t, x1+9)
plt.plot(t, x2+7.5)
plt.plot(t, x3+6)
plt.plot(t, x4+4.5)
plt.plot(t, a1, '--r')
plt.plot(t, a2, '--g')
plt.plot(t, E0, '--k')

# рисуем вертикальные линии по изменению уровня некоторых сигналов
xcoords = [0, 31, 52, 62, 94, 104, 125, 157, 471, 502]
for xc in xcoords:
    plt.axvline(x=xc, linestyle='--', color='gray', alpha=0.5)

plt.legend(['X1', 'X2', 'X3', 'X4', 'a1', 'a2', 'E0'])


plt.show()