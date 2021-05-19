from telebot import types
from values.strings import *

keyboard_send_contact = types.ReplyKeyboardMarkup(True)
keyboard_send_contact.add(
    types.KeyboardButton(text="Отправить контакт", request_contact=True)
)

keyboard_change_data = types.InlineKeyboardMarkup()
for callback in (change_first_name_message, change_last_name_message,
                change_team_name_message, change_phone_number_message):
    keyboard_change_data.add(types.InlineKeyboardButton(
        text=callback, callback_data=callback))

keyboard_operations = types.ReplyKeyboardMarkup(True)
keyboard_operations.add(types.KeyboardButton(text=my_information_message))
keyboard_operations.add(types.KeyboardButton(text=change_information_message))

keyboard_operations_with_reject = types.ReplyKeyboardMarkup(True)
keyboard_operations_with_reject.add(types.KeyboardButton(text=reject_operation_message))
