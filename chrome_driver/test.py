

message_date = {'login': 'sdfsd', 'password': 'sdfjgfd', 'date': 'November 1,10'}

text = 'First Available Appointment Is Tuesday November 26, 2024.'


def filter_date(date_user):
    date = date_user['date']
    punc = ''',.'''

    for char in date:
        if char in punc:
            date = date.replace(char, ' ')

    lst_date = date.split(' ')
    return lst_date


def check_date(text):
    date_list = filter_date(message_date)
    found = False
    for date in range(int(date_list[1]), int(date_list[2]) + 1):
        date_str = str(date)
        print(date_str)
        if date_str in text and date_list[0] in text:
            found = True
            break  # Найдено совпадение, выходим из цикла
    return found  # Возвращаем результат после завершения цикла


if check_date(text):
    print('Yes')
else:
    print('No')

