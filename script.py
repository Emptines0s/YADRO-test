from sys import argv
import csv
import re


script, filename = argv  # Строчка для получения значения параметра при вызове скрипта из консоли (название csv файла)


# Функция для чтения csv файла. Его мы локально представляем в виде списка списков, а для навигации в нём по индексам
# и колонкам используем два вспомогательных словаря (таким образом мы используем БОЛЬШЕ памяти на создание дополнитель
# ных словарей, ЗАТО операции поиска конкретной ячейки через arr[x][y] + два .get() будут в решаться за O(1) + O(1)
# + O(1) + O(1) = 4*O(1). Но так как сложность алгоритма константная, то выполняться это будет куда шустрее чем O(n),
# уже при размерах таблицы в 200+ ячеек (я так считаю, не тестил).
def read_csv(filename):
    with open(filename, 'r', newline='') as f:
        reader = csv.reader(f)
        try:
            head = next(reader)[1:]  # Берём первую строку для формирования словаря столбцов
            columns = {head[i]: i for i in range(len(head))}  # Словарь столбцов (Название столбца: индекс в массиве)
        except:
            print('Csv file is empty')
            return False, False, False
        indexes = {}
        table = []
        for index, row in enumerate(reader):
            indexes.update({row[0]: index})  # Словарь индексов строк (Значения индекса таблицы: индекс в массиве)
            if not row[0].isdigit():  # Проверка удовлетворяет ли индекс условию: "целыми положительными числами"
                print('Index value is incorrect: ' + row[0])
                return False, False, False
            else:
                table.append(row[1:])
    return table, columns, indexes


def transformation(cell):  # Функция для преобразования строки выражения в отдельные переменные
    if cell[0] != '=':  # Если значение текущей ячейки не выражение, то скипаем преобразования и возвращаем значение
        return cell
    else:
        cell = cell[1:]  # Убираем знак "=" для дальнейшей работы

    for symbol in cell:  # Ищем знак арифметической операции, запоминаем его и делим строку на левую и правую часть
        if symbol in ['+', '-', '*', '/']:
            operator = symbol
            left, right = cell.split(symbol)
    r = re.compile("([a-zA-Z]+)([0-9]+)")  # Делим правую/левую на переменные: Цифры - индекс, буквы - название столбца

    # Если ARG1 имеет формат "СтолбецИндекс", то идентифицируем его как ссылку и запускаем рекурсию
    if r.match(left) is not None:
        try:
            column1 = r.match(left).group(1)
            index1 = r.match(left).group(2)
            cell1 = table[indexes.get(index1)][columns.get(column1)]  # Получаем содержимое ячейки по адресу 4*O(1)
            cell1 = transformation(cell1)  # Запускаем эту же функцию рекурсивно
        except:
            return 'ARG1 incorrect reference'
    else:
        cell1 = left

    # Если ARG2 имеет формат "СтолбецИндекс", то идентифицируем его как ссылку и запускаем рекурсию
    if r.match(right) is not None:
        try:
            column2 = r.match(right).group(1)
            index2 = r.match(right).group(2)
            cell2 = table[indexes.get(index2)][columns.get(column2)]  # Получаем содержимое ячейки по адресу 4*O(1)
            cell2 = transformation(cell2)  # Запускаем эту же функцию рекурсивно
        except:
            return 'ARG2 incorrect reference'
    else:
        cell2 = right

    try:
        return calculate(cell1, cell2, operator)  # Считаем выражение
    except:
        return 'ARG1 or/and ARG2 are not numbers'


def calculate(arg1, arg2, operator):  # Пребразование набора переменных в арифметику
    arg1 = float(arg1)  # Приводим числа из str в float
    arg2 = float(arg2)

    if operator == '+':  # При помощи простых регулярок считаем значение выражения ARG1 OP ARG2
        return arg1 + arg2
    if operator == '-':
        return arg1 - arg2
    if operator == '*':
        return arg1 * arg2
    if operator == '/':
        try:  # Отлавливаем ошибку при делении на ноль
            return arg1 / arg2
        except:
            return  'Division by zero'


def main(table, columns, indexes):
    # Сложность алгоритма: проход по всем элементам таблицы O(n*m) n - количество строк, m - количество столбцов
    for row in table:  # В двойном цикле проходимся по всем элементам таблицы и ищем ячейки с выражениями внутри
        for  i, cell in enumerate(row):
            if cell[0] == '=':  #  Если нашли строчку выражение преобразуем её в набор пременных, затем посчитаем
                result = transformation(cell)  # Пропускаем знак "=" чтобы не мешал
                if not isinstance(result, str):  # Если получаем ошибку (str) выходим из функции
                    row[i] = str(result)
                else:
                    print(f'{result}, cell: ({cell}) <--- An error occurred while calculating the equations!')
                    return

    # Выводим готовую таблицу с посчитаными выражениями в консоль
    current_string = ''
    for column in columns.keys():
        current_string += f',{column}'
    print(current_string)
    for i, index in enumerate(indexes.keys()):
        current_string = index
        for element in table[i]:
            current_string += f',{element}'
        print(current_string)


if __name__ == "__main__":
    table, columns, indexes = read_csv(filename)  # Читаем csv файл
    if table:  # Сработает если таблица НЕ пустая и индексы в таблице УДОВЛЕТВОРЯЮТ условию (положительные целые числа)
        main(table, columns, indexes)