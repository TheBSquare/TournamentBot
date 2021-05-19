from logic.bot import bot
from logic.db import Db
from logic.extra import Question

from values.strings import *
from values.keyboards import *


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, autorization_message, reply_markup=keyboard_send_contact)


@bot.message_handler(content_types=['text'])
def parse_text(message):
    chat_id = message.chat.id
    text = message.text

    if text == my_information_message:
        db.create_connection(chat_id)
        user_data = db.get_user_by_chat_id(chat_id, chat_id)
        db.close_connection(chat_id)
        if user_data is None:
            bot.send_message(chat_id, no_autorization_message, reply_markup=keyboard_send_contact)
        else:
            last_name_part = last_name_false_message if user_data['lastName'] is None else\
                ''.join((last_name_true_message, user_data['lastName']))

            team_name_part = team_name_false_message if user_data['team'] is None else \
                ''.join((team_name_true_message, user_data['team']))

            message_text = f'{name_message}{user_data["firstName"]}, ' \
                           f'{last_name_part}, {phone_number_message}{user_data["phoneNumber"]},' \
                           f' {paid_true_message if bool(user_data["paid"]) else paid_false_message}, {team_name_part}'
            bot.send_message(chat_id, message_text)

    elif text == change_information_message:
        bot.send_message(chat_id, 'Что меняем?', reply_markup=keyboard_change_data)


@bot.message_handler(content_types=['contact'])
def get_contact(message):
    contact = message.contact
    chat_id = message.chat.id

    if contact is not None:

        db.create_connection(chat_id)

        if not db.check_user(connection_id=chat_id, chat_id=chat_id):
            db.add_user(
                connection_id=chat_id,
                user_data=(
                    int(chat_id),
                    int(contact.phone_number.replace('+', '')),
                    0,
                    contact.first_name,
                    contact.last_name,
                    None
                )
            )

        db.close_connection(chat_id)

        bot.send_message(chat_id, f'{hello_message}{contact.first_name}', reply_markup=keyboard_operations)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(callback):
    chat_id = callback.message.chat.id

    db.create_connection(chat_id)
    user = db.get_user_by_chat_id(chat_id, chat_id)

    questions = (
        Question(
            question=input_phone_number_message,
            type_=int,
            chat_id=chat_id,
            max_length=12,
            min_length=12,
            condition=change_phone_number_message,
            row='phoneNumber',
            changed_data_message=changed_phone_number_message,
            showing_data_message=your_phone_number_message
        ),
        Question(
            question=input_first_name_message,
            type_=str,
            chat_id=chat_id,
            max_length=20,
            min_length=2,
            condition=change_first_name_message,
            row='firstName',
            changed_data_message=changed_first_name_message,
            showing_data_message=your_first_name_message
        ),
        Question(
            question=input_last_name_message,
            type_=str,
            chat_id=chat_id,
            max_length=20,
            min_length=2,
            condition=change_last_name_message,
            row='lastName',
            changed_data_message=changed_last_name_message,
            showing_data_message=your_last_name_message
        ),
        Question(
            question=input_team_name_message,
            type_=str,
            chat_id=chat_id,
            max_length=20,
            min_length=2,
            condition=change_team_name_message,
            row='team',
            changed_data_message=changed_team_name_message,
            showing_data_message=your_team_name_message
        )
    )

    for question in questions:
        if callback.data == question.condition:
            bot.send_message(chat_id, f'{question.showing_data_message}{user[question.row]}',
                             reply_markup=keyboard_operations_with_reject)
            question.ask()
            question.wait()

            answer = question.answer

            if answer == reject_operation_message:
                bot.send_message(chat_id, operation_rejected_message, reply_markup=keyboard_operations)
                break

            db.change_user_data(chat_id, chat_id, question.row, answer)
            bot.send_message(chat_id, f'{question.changed_data_message}{answer}',reply_markup=keyboard_operations)
            break

    db.close_connection(chat_id)


if __name__ == '__main__':
    db = Db()
    bot.polling()
