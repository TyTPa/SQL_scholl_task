import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from config import TOKEN
import sqlite3
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import aiohttp
import logging

bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

class Form(StatesGroup):
    name = State()
    age = State()
    grade = State()

def init_db():
	conn = sqlite3.connect('school_data.db')
	cur = conn.cursor()
	cur.execute('''
	CREATE TABLE IF NOT EXISTS users (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL,
	age INTEGER NOT NULL,
	grade TEXT NOT NULL)
	''')

	conn.commit()
	conn.close()
conn = sqlite3.connect('bot.db')
init_db()

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
	await message.answer("Привет! Как тебя зовут?")
	await state.set_state(Form.name)

@dp.message(Form.name)
async def name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Сколько тебе лет?")
    await state.set_state(Form.age)

@dp.message(Form.age)
async def grade(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Из какого ты класса?")
    await state.set_state(Form.grade)

@dp.message(Form.grade)
async def city(message: Message, state:FSMContext):
	await state.update_data(grade=message.text)

	school_data = await state.get_data()

	conn = sqlite3.connect('school_data.db')
	cur = conn.cursor()
	cur.execute('''
	   INSERT INTO users (name, age, grade) VALUES (?, ?, ?)''',
				(school_data['name'], school_data['age'], school_data['grade']))
	conn.commit()
	conn.close()
	await message.answer("Данные сохранены!")
	await state.clear()

@dp.message(Command('exc'))
async def exc(message: Message):
    conn = sqlite3.connect('school_data.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM users')
    rows = cur.fetchall()
    conn.close()

    if rows:
        response = "Данные из базы данных:\n"
        for row in rows:
            response += f"Имя: {row[1]}, Возраст: {row[2]}, Класс: {row[3]}\n"
    else:
        response = "База данных пуста."

    await message.answer(response)

async def main():
	await dp.start_polling(bot)

if __name__ == '__main__':
	asyncio.run(main())