import io

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from DB import workDB


bot_token = "6956938097:AAHwkGApDzp2JeQDRkW-qNVjgl6WYNVY7gs"
bot = Bot(token=bot_token)
dp = Dispatcher(bot=bot)

# Словарь для отлова сообщения
catching_suggestion = {}

# Клавиатура для пользователей
markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton(text="Инструкции"), KeyboardButton(text="Помощь")],
    [KeyboardButton(text="Связь с оператором")]
])

# Клавиатура для операторов
markup_for_operators = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton(text="Свободен"), KeyboardButton(text="Занят")]
])

def create_keyboard(page_number: int, number_pages: int, program_id: int, type: str) -> InlineKeyboardMarkup:

    if page_number < 0:
        page_number = 1
    elif page_number > number_pages:
        page_number = number_pages

    markup_back = InlineKeyboardButton(text='<', callback_data=f'last_page_{program_id}_{page_number - 1}_{type}')
    markup_number_page = InlineKeyboardButton(text=f'Страница: {page_number}/{number_pages}', callback_data='empty_callback')
    markup_next = InlineKeyboardButton(text='>', callback_data=f'new_page_{program_id}_{page_number + 1}_{type}')
    keyboard_next_back = InlineKeyboardMarkup(inline_keyboard=[[markup_back, markup_number_page, markup_next]])
    return keyboard_next_back
def unloading(dict_values: dict, id_program: int, page_number: int=1) -> InlineKeyboardMarkup:
    buttons_on_page = 10
    count = len(dict_values) // buttons_on_page + 1 if len(dict_values) % buttons_on_page else len(dict_values) // buttons_on_page
    if page_number < 1:
        page_number = count
    elif page_number > count:
        page_number = 1

    start = (page_number - 1) * buttons_on_page
    end = min(page_number * buttons_on_page, len(dict_values))

    btns = []


    for instructions_id, instructions_name in list(dict_values.items())[start:end]:
        btns.append(
            [InlineKeyboardButton(text=instructions_name, callback_data=f"selected_instruction_id_{instructions_id}")]
        )
    btns.append(
        [InlineKeyboardButton(text="<", callback_data=f"back_{id_program}_{page_number - 1}"),
         InlineKeyboardButton(text=f"{page_number}/{count}", callback_data=f"{page_number}/{len(dict_values)}"),
         InlineKeyboardButton(text=">", callback_data=f"next_{id_program}_{page_number + 1}")]
    )
    return InlineKeyboardMarkup(inline_keyboard=btns)


# Команда старт
@dp.message(Command(commands=["start"]))
async def start(message: types.Message):
    await message.answer("Приветствую! 🤖 Я чат-бот технической поддержки программного обеспечения."
                         " Готов ответить на ваш вопрос или помочь с возникшей проблемой."
                         " Пожалуйста, задайте свой вопрос. 🛠️", reply_markup=markup)

    # Собираем информацию о пользователе в бд

    workDB.insert_user(message.chat.first_name, message.chat.id)


# Отлов сообщений
@dp.message()
async def answer_and_buttons(message: types.Message):
    if message.text and not (message.text.startswith('/') or message.text in ["Инструкции", "Помощь", "Связь с оператором"]) and catching_suggestion == {}:
        # Получение ответа из бд
        answer = workDB.get_answer(message.text)
        # Отправка ответа пользователю
        if answer:
            await message.answer(answer)
        else:
            await message.answer("Извините, ответ на ваш вопрос не найден. 🤔🔍")

    elif catching_suggestion != {}:
        catching_suggestion['suggestion'] = message.text
        workDB.insert_suggestion(catching_suggestion)
        catching_suggestion.clear()
        await message.answer('Ваше предложение по инструкции добавлено на рассмотрение')

    elif message.text == "Помощь":
        # получаем список
        programs = workDB.get_programs()
        markup_programs = [InlineKeyboardButton(text=program_name, callback_data=f"data_id_{program_id}") for
                           program_id, program_name in
                           programs.items()]
        keyboard_programs = InlineKeyboardMarkup(inline_keyboard=[markup_programs])
        await message.answer("Выберите программу: 🖥️📊📝", reply_markup=keyboard_programs)

    elif message.text == 'Инструкции':
        programs = workDB.get_programs()
        markup_programs = [InlineKeyboardButton(text=program_name, callback_data=f"instructions_{program_id}") for
                           program_id, program_name in
                           programs.items()]
        keyboard_programs = InlineKeyboardMarkup(inline_keyboard=[markup_programs])
        await message.answer("Выберите программу: 🖥️📊📝", reply_markup=keyboard_programs)


    elif message.text == 'Связь с оператором':
        operator = workDB.get_free_operators()
        if operator:
            pass
            await message.answer(f'📞 Здравствуйте! Вот ссылка свободного оператора: {operator} Напишите ему и ожидайте ответа')
        else:
            await message.reply("⌛️ Извините, в данный момент все операторы заняты. Попробуйте позже.")



@dp.callback_query(F.data.startswith("back") | F.data.startswith("next"))
async def navigation(callback: CallbackQuery):
    cb_data = callback.data.split("_")
    page_num = int(cb_data[2])
    id_program = int(cb_data[1])
    data_instructions = workDB.get_instructions(id_program)
    dict_instructions = {}
    for i in data_instructions:
        dict_instructions[i[0]] = i[1]

    new_markup = unloading(dict_instructions, id_program, page_num)
    if new_markup != callback.message.reply_markup:
        await callback.message.edit_reply_markup(reply_markup=new_markup)


list_programs = workDB.get_programs()
list_programs_id = [f"data_id_{i}" for i in list_programs.keys()]


@dp.callback_query(F.data.startswith(tuple(list_programs_id)))
async def settings(callback: CallbackQuery):
    program_id = callback.data.split('_')[2]
    await callback.message.delete()
    markup_install = InlineKeyboardButton(text='Установка программы', callback_data=f'install_{program_id}')
    markup_settings = InlineKeyboardButton(text='Настройка программы', callback_data=f'settings_{program_id}')
    keyboard_help = InlineKeyboardMarkup(inline_keyboard=[[markup_install, markup_settings]])
    await callback.message.answer("Выберите, в чем вам нужна помощь: 💡🛠️", reply_markup=keyboard_help)


@dp.callback_query(F.data.startswith('install_'))
async def help_with_install(callback: CallbackQuery):
    await callback.message.delete()
    program_id = callback.data.split('_')[1]
    install_paragraphs = workDB.get_install_paragraph(program_id)

    # Проверяем, есть ли элементы в списке
    if install_paragraphs:

        # Проверяем, что список не пустой
        image_id = install_paragraphs[0][2]

        description = install_paragraphs[0][0]
        page_number = install_paragraphs[0][1]

        number_pages = len(install_paragraphs)
        keyboard_pages = create_keyboard(page_number, number_pages, program_id, 'install')

        if image_id:
            image_path = f"/support_bot/image/{image_id}.png"
            image = types.FSInputFile(image_path)

            # Создание описания с номером страницы
            message_text = description

            # Отправка сообщения с изображением и описанием
            await callback.message.answer_photo(photo=image, caption=message_text, reply_markup=keyboard_pages)
        else:
            await callback.message.answer(description, reply_markup=keyboard_pages)
    else:
        # Если список пустой, отправляем сообщение об ошибке
        pass


@dp.callback_query(F.data.startswith('settings_'))
async def help_with_settings(callback: CallbackQuery):
    await callback.message.delete()
    program_id = callback.data.split('_')[1]
    setting_paragraphs = workDB.get_settings_paragraph(program_id)

    # Проверяем, есть ли элементы в списке
    if setting_paragraphs:
        # Проверяем, что список не пустой
        image_id = setting_paragraphs[0][2]
        description = setting_paragraphs[0][0]
        page_number = setting_paragraphs[0][1]
        number_pages = len(setting_paragraphs)
        keyboard_pages = create_keyboard(page_number, number_pages, program_id, 'setting')

        if image_id:
            image_path = f"/support_bot/image/{image_id}.png"
            image = types.FSInputFile(image_path)

            # Создание описания с номером страницы
            message_text = description

            # Отправка сообщения с изображением и описанием
            await callback.message.answer_photo(photo=image, caption=message_text, reply_markup=keyboard_pages)
        else:
            await callback.message.answer(description, reply_markup=keyboard_pages)
    else:
        # Если список пустой, отправляем сообщение об ошибке
        pass


@dp.callback_query(F.data.startswith('instructions_'))
async def instructions(callback: CallbackQuery):
    await callback.message.delete()
    all_instructions = workDB.get_instructions(callback.data.split('_')[1])
    id_program = callback.data.split('_')[1]
    dict_instructions = {}
    for i in all_instructions:
        dict_instructions[i[0]] = i[1]

    await callback.message.answer("Выберите инструкцию: 📝", reply_markup=unloading(dict_instructions, int(id_program)))


@dp.callback_query(F.data.startswith('selected_instruction_'))
async def selected_instruction(callback: CallbackQuery):
    await callback.message.delete()
    instruction_id = callback.data.split('_')[-1]
    content = workDB.get_content(instruction_id)
    texts = [item[0] for item in content]
    # Подсчет кликов
    workDB.insert_count_of_clicks(instruction_id)

    await callback.message.answer(*texts)

    # Выбор оценок
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="★", callback_data=f"rating_{instruction_id}_1"),
            InlineKeyboardButton(text="★★", callback_data=f"rating_{instruction_id}_2"),
            InlineKeyboardButton(text="★★★", callback_data=f"rating_{instruction_id}_3"),
            InlineKeyboardButton(text="★★★★", callback_data=f"rating_{instruction_id}_4"),
            InlineKeyboardButton(text="★★★★★", callback_data=f"rating_{instruction_id}_5")
        ],
        [
            InlineKeyboardButton(text="Оставить предложение", callback_data=f"suggestion_{instruction_id}")
        ]
    ])
    await callback.message.answer("Поставьте оценку данной инструкции или оставьте свое предложение:", reply_markup=keyboard)


@dp.callback_query(lambda c: c.data.startswith('rating'))
async def process_callback(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    rating = int(callback_query.data.split('_')[2])
    inst_id = int(callback_query.data.split('_')[1])
    user_id = callback_query.from_user.id
    workDB.enter_rating(user_id, inst_id, rating)
    await bot.send_message(callback_query.from_user.id, f"Вы поставили оценку: {rating} звезд")


@dp.callback_query(F.data.startswith('suggestion_'))
async def selected_instruction(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("Введите свое предложение по данной инструкции:")

    catching_suggestion['instruction_id'] = callback.data.split('_')[1]
    catching_suggestion['user_tg_id'] = callback.message.chat.id


@dp.callback_query(F.data.startswith("last_page") | F.data.startswith("new_page"))
async def next_page(callback: CallbackQuery):
    await callback.message.delete()
    program_id = int(callback.data.split('_')[2])
    page_number = int(callback.data.split('_')[3])

    if callback.data.split('_')[4] == 'setting':
        settings_or_install = 'setting'
        data_paragraphs = workDB.get_settings_paragraph(program_id)
    else:
        data_paragraphs = workDB.get_install_paragraph(program_id)
        settings_or_install = 'install'

    # Проверяем, чтобы номер страницы не выходил за пределы списка
    if 0 < page_number <= len(data_paragraphs):
        paragraph = data_paragraphs[page_number - 1]
        image_id = paragraph[2]
        description = paragraph[0]
        page_number = paragraph[1]
        number_pages = len(data_paragraphs)
        keyboard_pages = create_keyboard(page_number, number_pages, program_id, settings_or_install)

        if image_id:
            image_path = f"/support_bot/image/{image_id}.png"
            image = types.FSInputFile(image_path)

            # Создание описания с номером страницы
            message_text = f"{description}"


            # Отправка сообщения с изображением и описанием
            await callback.message.answer_photo(photo=image, caption=message_text, reply_markup=keyboard_pages)
        else:
            # Если нет изображения, отправляем только описание
            message_text = f"{description}"
            await callback.message.answer(message_text,reply_markup= keyboard_pages)
    else:
        # Номер страницы выходит за пределы списка, обработаем эту ситуацию
        await callback.message.answer("Вы просмотрели все страницы")


if __name__ == '__main__':
    dp.run_polling(bot)