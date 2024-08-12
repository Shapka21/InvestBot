def start_command():
    return 'Привет, я бот, который с радостью поможет тебе собрать инвестиционный портфель из российских акций'


def start_make_portfolio():
    return 'Какой портфель ты хочешь сделать?'


def request_money():
    return 'Введите сумму, на которую будет составляться портфель.\nСумма должна быть более 1000 рублей и не превышать 10 млн рублей.\nДля отмены ввода напишите "отмена"'


def return_main():
    return 'Выберете, что хотите сделать'


def request_stock_name():
    return 'Введите обозначение акции, по которой вы хотите получить информацию\nДля отмены ввода напишите "отмена"'


def low_money():
    return 'Введённая сумма выходит за указаные границы'


def is_not_digit():
    return 'Вы ввели не число, попробуйте ещё раз'


def bad_stock():
    return 'Извините, данная акция не найдена'


def bad_responce():
    return 'Ошибка считывания, попробуйте ещё раз'


def make_portfolio_minvol(portfolio, rest):
    ans = ['Твой портфель:']
    for stocks in portfolio.keys():
        ans.append(f"{stocks.split('.')[0]} - {10 * portfolio[stocks]} шт.")
    ans.append(
        "Остаток денежных средств после построения портфеля с минимальной волатильностью составляет {:.2f} рублей".format(
            rest))
    return '\n'.join(ans)


def make_portfolio_maxsharp(portfolio, rest):
    ans = ['Твой портфель:']
    for stocks in portfolio.keys():
        ans.append(f"{stocks.split('.')[0]} - {10 * portfolio[stocks]} шт.")
    ans.append(
        "Остаток денежных средств после построения портфеля с максимальным коэфициетом шарпа составляет {:.2f} рублей".format(
            rest))
    return '\n'.join(ans)


def get_info_stocks(mu, sisma, last_prise):
    return 'Годовая доходность: {:.2f}%\nДисперсия акции: {:.2f}\nПоследняя цена: {:.2f} руб.'.format(mu, sisma,
                                                                                                      last_prise)
