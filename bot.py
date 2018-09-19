import re
import fex
import time
import emoji
import config
import telebot

from telebot import types

bot = telebot.TeleBot(token=config.TOKEN)


@bot.message_handler(commands=['start'])
def welcome(message):
    """
    This function used for handling "/start" command.
    If user send "/start" bot return request with inline buttons.
    """

    # Console output
    print(str(message))

    # Call InlineKeyboardMarkup class
    button = telebot.types.InlineKeyboardMarkup()

    # Add Inline Buttons
    button.row(
        types.InlineKeyboardButton('Перейти на FEX.NET', url=config.HOST),
    )

    button.row(
        types.InlineKeyboardButton('Создать анонимный объект', callback_data='object'),
    )

    button.row(
        types.InlineKeyboardButton('Сократить ссылку', callback_data='link'),
    )

    bot.send_message(message.chat.id,
                     text='Здравствуйте <b>{0}</b> {1}\n'
                          'Я маленький тестовый бот FEX.NET\n'
                          'Вот что я могу:'.format(message.chat.first_name, emoji.hand),
                     reply_markup=button,
                     parse_mode='HTML')

    fex_id_massage(message.chat.id)


@bot.message_handler(commands=['link'])
def short_link_flow(message):
    """
    Flow will start after then user send command '/link' or click on button "Сократить ссылку"
    This function includes steps of the user flow for create short link.
    """
    bot.send_message(message.chat.id,
                     text='Пожалуйста введите ссылку!\n'
                          '\n{0} Ссылка должна быть верного формата: '
                          '"https://example.com"'.format(emoji.info))

    # This is second step of creating shot link
    bot.register_next_step_handler(message, shortening_link)


@bot.callback_query_handler(func=lambda call: call.data == 'link')
def short_link_from_callback(call):
    # This method using for deactivate circle on inline button after click
    bot.answer_callback_query(call.id)

    short_link_flow(call.message)


@bot.message_handler(commands=['object'])
def object_from_command(message):
    """
    After user send command '/object' function for creating new object will call.
    """
    send_object(message)


@bot.callback_query_handler(func=lambda call: call.data == 'object')
def object_from_callback(call):
    # This method using for deactivate circle on inline button after click
    bot.answer_callback_query(call.id)

    # Call function for creating new object
    send_object(call.message)


@bot.message_handler(commands=['help'])
def help_message(message):
    """
    After user send command '/help' will be sent a text with description and hints.
    """
    bot.send_message(message.chat.id,
                     text='*Справка*'
                          '\nДанный бот создан исключительно с целью обучения\n'
                          '\n*Автор* [Philip Kandyba](https://t.me/PhilipKandyba)\n',
                     parse_mode='Markdown',
                     disable_web_page_preview=True)

    bot.send_message(message.chat.id,
                     text='\n*Создание объекта*\n'
                          'Данная функция вызывается при помощи команды /object. Цель данной функции - создание '
                          'анонимного объекта на сайте FEX.NET в который любой пользователь может загружать файлы. '
                          'Файлы в данном объекте доступны всем у кого есть ссылка и хранятся в течение 7 дней, '
                          'после файлы будут удалены.',
                     parse_mode='Markdown',
                     disable_web_page_preview=True)

    bot.send_message(message.chat.id,
                     text='\n*Сокращение ссылки*\n'
                          'Данная функция вызывается при помощи команды /link. '
                          'Вы можете сделать из длинной ссылки короткую. '
                          'Создавайте простые ссылки для более удобного их использования '
                          'Для корректно сокращения ссылок, ее нужно передать в корректном формате '
                          'Правильный формат для ссылки: https://google.com',
                     parse_mode='Markdown',
                     disable_web_page_preview=True)


def fex_id_massage(chat_id):
    """
    A method that contains buttons with links of the FEX ID application
    """
    app_button = telebot.types.InlineKeyboardMarkup()

    app_button.row(
        types.InlineKeyboardButton('iOS ' + emoji.apple, url=config.IOS_APP),
        types.InlineKeyboardButton('Android ' + emoji.play, url=config.ANDROID_APP),
    )

    app_button.row(
        types.InlineKeyboardButton('Smart TV ' + emoji.tv, url=config.TV_APP),
    )

    bot.send_message(chat_id,
                     text='Так же вы можете скачать наше приложение <b>FEX ID</b>\n'
                          'Приложение доступно для <b>iOS</b>, <b>Android</b> и <b>Smart TV</b>',
                     reply_markup=app_button,
                     parse_mode='HTML')


def shortening_link(message):
    """
    Function for shortening references.
    """
    message_text = message.text

    # Check that the message text contain url
    # Old regexp with fex https?://[^fex.net](?:[-\w.]|(?:%[\da-fA-F]{2}))+
    link_list = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', message_text)

    # Check that the link_list is not empty
    if link_list:
        bot.send_chat_action(message.chat.id, action='typing')

        # Call function for create new short link
        short_link = fex.short_link(link_list[0])

        # Send massage about working process was start
        bot.send_chat_action(message.chat.id, action='typing')

        # This sleep used for reduce the load
        time.sleep(2)

        # Sent created link to user
        bot.send_message(
            message.chat.id,
            disable_web_page_preview=True,
            text='Поздравляем{0}, \nВаша ссылка готова{1}\n\n{2} {3}'.format(
                emoji.party, emoji.check, emoji.rigtharrow, short_link),
        )
    # Check that the link is not contain fex.net urls
    elif re.match('https?://fex.net/', message_text) is not None:

        bot.send_message(message.chat.id, emoji.stop + ' Не нужно вставлять ссылки на FEX.NET')

    else:
        bot.send_message(message.chat.id, emoji.info + ' Что-то не так, воспользуйтесь подсказкой /help')
        return


def send_object(message):
    """
    Function to create and send a new object.
    """
    bot.send_message(message.chat.id,
                     text='Поздравляем <b>{0}</b> {1}\n'
                          'Ваш новый, анонимный объект готов! {2}\n'
                          'Вы можете хранить любые Ваши файлы бесплатно в течение 7 дней {3}\n'
                          '\n{4} {5}'.format(message.chat.first_name,
                                             emoji.party,
                                             emoji.check,
                                             emoji.calendar,
                                             emoji.rigtharrow,
                                             fex.new_object()),
                     disable_web_page_preview=True,
                     parse_mode='HTML')


bot.polling(
    none_stop=True
)
