from logic.bot import bot
from time import sleep
from values.strings import *


class Question:
    def __init__(self, question, chat_id, type_, condition, max_length=None, min_length=None, max_number=None,
                 min_number=None, row=None, changed_data_message=None, showing_data_message=None):
        self.question = question
        self.type = type_
        self.chat_id = chat_id
        self.max_length = max_length
        self.min_length = min_length
        self.max_number = max_number
        self.min_number = min_number
        self.condition = condition
        self.changed_data_message=changed_data_message
        self.showing_data_message=showing_data_message
        self.row = row

        self.answer = None

    def ask(self):
        message = bot.send_message(self.chat_id, self.question)
        bot.register_next_step_handler(message, self.__take_answer)

    def wait(self):
        while self.answer is None:
            sleep(.05)

    def __take_answer(self, message):
        input_ = message.text
        try:
            input_ = int(input_)
        except ValueError:
            pass
        input_type = type(input_)
        if not input_type is self.type:
            bot.send_message(self.chat_id,
                f'{input_must_be_message}{"текстом" if self.type is str else "числом" if self.type is int else "хз"}, '
                f'{input_message}{"текст" if input_type is str else "число" if input_type is int else "хз"}')
            self.ask()
            return

        temp = input_ if type(input_) is int else len(input_)
        if not self.min_number is None and temp < self.min_number:
            bot.send_message(self.chat_id,
                             f'{number_below_min_message if input_type is int else length_below_min_message}'
                             f' {temp} < {self.min_number}')
            self.ask()
            return

        if not self.max_number is None and input_ > self.max_number:
            bot.send_message(self.chat_id,
                             f'{number_higher_max_message if input_type is int else length_higher_max_message}'
                             f' {temp} > {self.max_number}')
            self.ask()
            return

        temp = len(str(input_))
        if not self.min_length is None and temp < self.min_length:
            bot.send_message(self.chat_id,
                             f'{length_below_min_message}'
                             f' {temp} < {self.min_length}')
            self.ask()
            return

        if not self.max_length is None and temp > self.max_length:
            bot.send_message(self.chat_id,
                             f'{length_higher_max_message}'
                             f' {temp} > {self.max_length}')
            self.ask()
            return

        self.answer = input_
