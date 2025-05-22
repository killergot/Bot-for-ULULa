
LEXICON_COMMANDS_RU: dict[str, str] = {
    '/help': 'Список команд',
    '/schedule': 'Получение расписания',
    '/tasks' : 'Все твои таски',
    '/my_group' : 'Списко моей группы',
    '/login' : 'Ввод данных для входа в систему'
}


LEXICON_RU: dict[str, str| dict[str,str]] = {
    '/start': 'Салам пополам плебей. Не знаешь что делать? '
              'Тыкай на /help',
    '/help' : f'{LEXICON_COMMANDS_RU}'
}
