import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode, ChatType
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.storage.memory import MemoryStorage

from database import init_db, add_user, is_user_registered, get_total_users, get_balance, update_balance, update_stats

TOKEN = "7968492757:AAGKGsHjyJe6JMEtdnYqLx5tTi4faaD0jSc"
ADMIN_ID = 6025818386

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

BOT_USERNAME = None
unregistered_warned = set()

TOWER_MULTIPLIERS = [1.19, 1.48, 1.86, 2.32, 2.9, 3.62, 4.53, 5.66, 7.08]
user_tower_games = {}

def is_private_chat(message: types.Message) -> bool:
    return message.chat.type == ChatType.PRIVATE

def parse_bet(bet_str: str) -> int:
    bet_str = bet_str.lower().strip()
    if bet_str == "все":
        return -1
    if bet_str.endswith("к"):
        try:
            return int(float(bet_str[:-1]) * 1000)
        except:
            return -1
    try:
        return int(bet_str)
    except:
        return -1

def format_balance(amount: int) -> str:
    if amount >= 1_000_000_000:
        return f"{amount // 1_000_000_000}млрд"
    elif amount >= 1_000_000:
        return f"{amount // 1_000_000}млн"
    elif amount >= 1000:
        return f"{amount // 1000}к"
    return str(amount)

async def send_unregistered_warning(message: types.Message):
    global BOT_USERNAME
    user_id = message.from_user.id
    
    if user_id in unregistered_warned:
        return
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Зарегистрироваться",
                    url=f"https://t.me/{BOT_USERNAME}?start=none"
                )
            ]
        ]
    )

    text = "🤨 <b>Ты не из наших! Для регистрации нажми кнопку ниже</b>"

    await message.answer(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard
    )
    
    unregistered_warned.add(user_id)

def build_tower_keyboard(user_id: int, game_id: str) -> InlineKeyboardMarkup:
    game = user_tower_games.get(game_id)
    if not game or game.get("user_id") != user_id:
        return InlineKeyboardMarkup(inline_keyboard=[])
    
    level = game.get("level", 0)
    selected = game.get("selected", [])
    
    if game.get("lost", False) or level >= 9:
        return InlineKeyboardMarkup(inline_keyboard=[])
    
    kb = []
    kb.append([
        InlineKeyboardButton(text="❔", callback_data=f"tower:{game_id}:0"),
        InlineKeyboardButton(text="❔", callback_data=f"tower:{game_id}:1"),
        InlineKeyboardButton(text="❔", callback_data=f"tower:{game_id}:2"),
        InlineKeyboardButton(text="❔", callback_data=f"tower:{game_id}:3"),
        InlineKeyboardButton(text="❔", callback_data=f"tower:{game_id}:4")
    ])
    
    for i in range(level - 1, -1, -1):
        row = []
        for j in range(5):
            if i < len(selected) and selected[i] == j:
                row.append(InlineKeyboardButton(text="🌀", callback_data="noop"))
            else:
                row.append(InlineKeyboardButton(text="❔", callback_data="noop"))
        kb.append(row)
    
    if level == 0:
        kb.append([InlineKeyboardButton(text="❌ Отмена", callback_data=f"tower_cancel:{game_id}")])
    else:
        kb.append([InlineKeyboardButton(text="💰 Забрать", callback_data=f"tower_collect:{game_id}")])
    
    return InlineKeyboardMarkup(inline_keyboard=kb)

def build_final_tower_keyboard(game_id: str) -> InlineKeyboardMarkup:
    game = user_tower_games.get(game_id)
    if not game:
        return InlineKeyboardMarkup(inline_keyboard=[])
    
    bombs = game.get("bombs", [])
    selected = game.get("selected", [])
    lost = game.get("lost", False)
    
    if lost:
        last = len(selected) - 1
    else:
        last = min(len(selected) - 1, 8)
    
    if last < 0:
        return InlineKeyboardMarkup(inline_keyboard=[])
    
    kb = []
    for i in range(last, -1, -1):
        row = []
        for j in range(5):
            if lost and i < len(bombs) and bombs[i][j] == 1:
                if i < len(selected) and selected[i] == j:
                    row.append(InlineKeyboardButton(text="💥", callback_data="noop"))
                else:
                    row.append(InlineKeyboardButton(text="💣", callback_data="noop"))
            elif i < len(selected) and selected[i] == j:
                row.append(InlineKeyboardButton(text="🌀", callback_data="noop"))
            else:
                row.append(InlineKeyboardButton(text="▫️", callback_data="noop"))
        kb.append(row)
    
    return InlineKeyboardMarkup(inline_keyboard=kb)

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    global BOT_USERNAME
    user_id = message.from_user.id
    args = message.text.split()
    payload = args[1] if len(args) > 1 else None
    
    if is_private_chat(message):
        if payload == "none":
            text = (
                "<b>Привет! 👋 Ты в GMPire — место, где время летит незаметно</b>\n\n"
                "🎮 Тут ты можешь найти интересные игры!\n\n"
                "Соревнуйся с друзьями или же другими игроками и продвигай свой чат либо канал🏆"
            )
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Играть",
                            callback_data="play"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Добавить бота в чат",
                            url=f"https://t.me/{BOT_USERNAME}?startgroup=start"
                        )
                    ]
                ]
            )

            photo_url = "https://iili.io/CkddrUx.md.png"

            await message.answer_photo(
                photo=photo_url,
                caption=text,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard
            )
            return

        add_user(
            user_id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        
        if user_id in unregistered_warned:
            unregistered_warned.remove(user_id)

        text = (
            "<b>Привет! 👋 Ты в GMPire — место, где время летит незаметно</b>\n\n"
            "🎮 Тут ты можешь найти интересные игры!\n\n"
            "Соревнуйся с друзьями или же другими игроками и продвигай свой чат либо канал🏆"
        )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Играть",
                        callback_data="play"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Добавить бота в чат",
                        url=f"https://t.me/{BOT_USERNAME}?startgroup=start"
                    )
                ]
            ]
        )

        photo_url = "https://iili.io/CkddrUx.md.png"

        await message.answer_photo(
            photo=photo_url,
            caption=text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard
        )
    else:
        if not is_user_registered(user_id):
            await send_unregistered_warning(message)

@dp.message(Command("help"))
async def help_handler(message: types.Message):
    user_id = message.from_user.id
    
    if is_private_chat(message):
        if not is_user_registered(user_id):
            await send_unregistered_warning(message)
            return
        
        await message.answer(
            "🆘 Список доступных команд:\n"
            "/start - начать работу\n"
            "/help - показать это сообщение\n"
            "/balance - показать баланс\n"
            "/crash [сумма] [множитель] - игра краш\n"
            "/roulette [сумма] [ставка] - рулетка\n"
            "/tower [сумма] - игра башня\n"
            "/info - статистика (админ)"
        )
    else:
        if not is_user_registered(user_id):
            await send_unregistered_warning(message)

@dp.message(Command("balance"))
async def balance_handler(message: types.Message):
    user_id = message.from_user.id
    
    if is_private_chat(message):
        if not is_user_registered(user_id):
            await send_unregistered_warning(message)
            return
        
        balance = get_balance(user_id)
        await message.answer(f"💰 Ваш баланс: <b>{format_balance(balance)}</b> монет", parse_mode=ParseMode.HTML)
    else:
        if not is_user_registered(user_id):
            await send_unregistered_warning(message)

@dp.message(Command("crash"))
async def crash_handler(message: types.Message):
    user_id = message.from_user.id
    
    if not is_private_chat(message):
        if not is_user_registered(user_id):
            await send_unregistered_warning(message)
        return
    
    if not is_user_registered(user_id):
        await send_unregistered_warning(message)
        return
    
    args = message.text.split()
    if len(args) != 3:
        await message.answer(
            "❌ Неверный формат!\n"
            "Пример: <code>/crash 100 2.5</code>\n"
            "Пример: <code>/crash все 3</code>",
            parse_mode=ParseMode.HTML
        )
        return
    
    bet_str = args[1]
    try:
        multiplier = float(args[2])
    except:
        await message.answer("❌ Неверный множитель!")
        return
    
    if multiplier < 1.01 or multiplier > 10:
        await message.answer("❌ Множитель должен быть от 1.01 до 10.00")
        return
    
    balance = get_balance(user_id)
    
    if bet_str.lower() == "все":
        bet = balance
    else:
        bet = parse_bet(bet_str)
    
    if bet <= 0:
        await message.answer("❌ Неверная сумма ставки!")
        return
    
    if bet > balance:
        await message.answer(f"❌ Недостаточно средств! Ваш баланс: {format_balance(balance)}")
        return
    
    r = random.random()
    
    if r < 0.15:
        crash_multiplier = 1.00
    elif r < 0.85:
        crash_multiplier = round(random.uniform(1.01, 1.99), 2)
    elif r < 0.95:
        crash_multiplier = round(random.uniform(2.00, 2.99), 2)
    elif r < 0.99:
        crash_multiplier = round(random.uniform(3.00, 5.99), 2)
    else:
        crash_multiplier = round(random.uniform(6.00, 10.00), 2)
    
    update_balance(user_id, -bet)
    
    if crash_multiplier >= multiplier:
        win = int(bet * multiplier)
        update_balance(user_id, win)
        update_stats(user_id, won=win)
        
        await message.answer(
            f"🚀 <b>Ракета улетела на x{crash_multiplier:.2f}</b> 📈\n"
            f"✅ <b>Ты выиграл!</b> Твой выигрыш составил {format_balance(win)}",
            parse_mode=ParseMode.HTML
        )
    else:
        update_stats(user_id, lost=bet)
        
        await message.answer(
            f"🚀 <b>Ракета упала на x{crash_multiplier:.2f}</b> 📉\n"
            f"❌ <b>Ты проиграл</b> {format_balance(bet)}",
            parse_mode=ParseMode.HTML
        )

@dp.message(Command("roulette"))
async def roulette_handler(message: types.Message):
    user_id = message.from_user.id
    
    if not is_private_chat(message):
        if not is_user_registered(user_id):
            await send_unregistered_warning(message)
        return
    
    if not is_user_registered(user_id):
        await send_unregistered_warning(message)
        return
    
    args = message.text.split()
    if len(args) != 3:
        await message.answer(
            "❌ Неверный формат!\n"
            "Пример: <code>/roulette 500 красное</code>\n"
            "Пример: <code>/roulette все черное</code>\n\n"
            "Доступные ставки: красное, черное, четное, нечетное",
            parse_mode=ParseMode.HTML
        )
        return
    
    bet_str = args[1]
    bet_type = args[2].lower()
    
    valid_bets = ["красное", "черное", "четное", "нечетное"]
    if bet_type not in valid_bets:
        await message.answer(
            "❌ Неверная ставка!\n"
            "Доступные ставки: красное, черное, четное, нечетное"
        )
        return
    
    balance = get_balance(user_id)
    
    if bet_str.lower() == "все":
        bet = balance
    else:
        bet = parse_bet(bet_str)
    
    if bet <= 0:
        await message.answer("❌ Неверная сумма ставки!")
        return
    
    if bet > balance:
        await message.answer(f"❌ Недостаточно средств! Ваш баланс: {format_balance(balance)}")
        return
    
    number = random.randint(0, 36)
    
    if number == 0:
        color = "зеленое"
        parity = "zero"
    elif number % 2 == 0:
        color = "черное"
        parity = "четное"
    else:
        color = "красное"
        parity = "нечетное"
    
    update_balance(user_id, -bet)
    
    win = False
    if bet_type == "красное" and color == "красное":
        win = True
        multiplier = 2
    elif bet_type == "черное" and color == "черное":
        win = True
        multiplier = 2
    elif bet_type == "четное" and parity == "четное":
        win = True
        multiplier = 2
    elif bet_type == "нечетное" and parity == "нечетное":
        win = True
        multiplier = 2
    
    if win:
        win_amount = bet * multiplier
        update_balance(user_id, win_amount)
        update_stats(user_id, won=win_amount)
        
        if number == 0:
            await message.answer(
                f"🎰 <b>Рулетка!</b>\n\n"
                f"🎯 Выпало: <b>{number}</b> (зеленое)\n"
                f"✅ <b>Ты выиграл!</b> {format_balance(win_amount)}",
                parse_mode=ParseMode.HTML
            )
        else:
            await message.answer(
                f"🎰 <b>Рулетка!</b>\n\n"
                f"🎯 Выпало: <b>{number}</b> ({color})\n"
                f"✅ <b>Ты выиграл!</b> {format_balance(win_amount)}",
                parse_mode=ParseMode.HTML
            )
    else:
        update_stats(user_id, lost=bet)
        
        if number == 0:
            await message.answer(
                f"🎰 <b>Рулетка!</b>\n\n"
                f"🎯 Выпало: <b>{number}</b> (зеленое)\n"
                f"❌ <b>Ты проиграл</b> {format_balance(bet)}",
                parse_mode=ParseMode.HTML
            )
        else:
            await message.answer(
                f"🎰 <b>Рулетка!</b>\n\n"
                f"🎯 Выпало: <b>{number}</b> ({color})\n"
                f"❌ <b>Ты проиграл</b> {format_balance(bet)}",
                parse_mode=ParseMode.HTML
            )

@dp.message(Command("tower"))
async def tower_handler(message: types.Message):
    user_id = message.from_user.id
    
    if not is_private_chat(message):
        if not is_user_registered(user_id):
            await send_unregistered_warning(message)
        return
    
    if not is_user_registered(user_id):
        await send_unregistered_warning(message)
        return
    
    args = message.text.split()
    if len(args) != 2:
        await message.answer(
            "❌ Неверный формат!\n"
            "Пример: <code>/tower 500</code>\n"
            "Пример: <code>/tower все</code>",
            parse_mode=ParseMode.HTML
        )
        return
    
    bet_str = args[1]
    balance = get_balance(user_id)
    
    if bet_str.lower() == "все":
        bet = balance
    else:
        bet = parse_bet(bet_str)
    
    if bet <= 0:
        await message.answer("❌ Неверная сумма ставки!")
        return
    
    if bet > balance:
        await message.answer(f"❌ Недостаточно средств! Ваш баланс: {format_balance(balance)}")
        return
    
    update_balance(user_id, -bet)
    
    bombs = []
    for _ in range(9):
        row = [0, 0, 0, 0, 0]
        bomb_index = random.randint(0, 4)
        row[bomb_index] = 1
        bombs.append(row)
    
    game_id = str(user_id) + "_" + str(random.randint(1000, 9999))
    
    user_tower_games[game_id] = {
        "user_id": user_id,
        "bet": bet,
        "level": 0,
        "bombs": bombs,
        "selected": [],
        "lost": False
    }
    
    keyboard = build_tower_keyboard(user_id, game_id)
    
    await message.answer(
        f"🏯 <b>Игра Башня!</b>\n\n"
        f"💸 Ставка: {format_balance(bet)}\n"
        f"🪜 Уровень: 1/9\n"
        f"💰 Возможный выигрыш: {format_balance(int(bet * TOWER_MULTIPLIERS[0]))} (x{TOWER_MULTIPLIERS[0]:.2f})\n\n"
        f"Выбери ячейку:",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )

@dp.callback_query(lambda c: c.data.startswith("tower:"))
async def tower_choose_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    parts = callback.data.split(":")
    game_id = parts[1]
    choice = int(parts[2])
    
    game = user_tower_games.get(game_id)
    if not game:
        await callback.answer("❌ Игра не найдена!", show_alert=True)
        return
    
    if game["user_id"] != user_id:
        await callback.answer("❌ Это не твоя игра!", show_alert=True)
        return
    
    if game.get("lost", False):
        await callback.answer("❌ Ты уже проиграл!", show_alert=True)
        return
    
    level = game["level"]
    if level >= 9:
        await callback.answer("❌ Игра уже завершена!", show_alert=True)
        return
    
    if choice < 0 or choice > 4:
        await callback.answer("❌ Неверный выбор!", show_alert=True)
        return
    
    game["selected"].append(choice)
    
    if game["bombs"][level][choice] == 1:
        game["lost"] = True
        update_stats(user_id, lost=game["bet"])
        
        keyboard = build_final_tower_keyboard(game_id)
        
        await callback.message.edit_text(
            f"💥 <b>Ты попал на мину!</b>\n\n"
            f"💸 Ставка: {format_balance(game['bet'])}",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
        
        del user_tower_games[game_id]
        return
    
    game["level"] = level + 1
    
    if game["level"] >= 9:
        win = int(game["bet"] * TOWER_MULTIPLIERS[8])
        update_balance(user_id, win)
        update_stats(user_id, won=win)
        
        keyboard = build_final_tower_keyboard(game_id)
        
        await callback.message.edit_text(
            f"🏆 <b>Поздравляем! Ты прошел башню!</b>\n\n"
            f"💰 Выигрыш: {format_balance(win)} (x{TOWER_MULTIPLIERS[8]:.2f})",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
        
        del user_tower_games[game_id]
        return
    
    multiplier = TOWER_MULTIPLIERS[game["level"] - 1]
    potential_win = int(game["bet"] * multiplier)
    
    keyboard = build_tower_keyboard(user_id, game_id)
    
    await callback.message.edit_text(
        f"🏯 <b>Игра Башня!</b>\n\n"
        f"💸 Ставка: {format_balance(game['bet'])}\n"
        f"🪜 Уровень: {game['level'] + 1}/9\n"
        f"💰 Возможный выигрыш: {format_balance(potential_win)} (x{multiplier:.2f})\n\n"
        f"Выбери ячейку:",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )

@dp.callback_query(lambda c: c.data.startswith("tower_collect:"))
async def tower_collect_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    game_id = callback.data.split(":")[1]
    
    game = user_tower_games.get(game_id)
    if not game:
        await callback.answer("❌ Игра не найдена!", show_alert=True)
        return
    
    if game["user_id"] != user_id:
        await callback.answer("❌ Это не твоя игра!", show_alert=True)
        return
    
    if game.get("lost", False):
        await callback.answer("❌ Ты уже проиграл!", show_alert=True)
        return
    
    level = game["level"]
    if level == 0:
        await callback.answer("❌ Сделай хотя бы один ход!", show_alert=True)
        return
    
    multiplier = TOWER_MULTIPLIERS[level - 1]
    win = int(game["bet"] * multiplier)
    
    update_balance(user_id, win)
    update_stats(user_id, won=win)
    
    keyboard = build_final_tower_keyboard(game_id)
    
    await callback.message.edit_text(
        f"💰 <b>Ты забрал выигрыш!</b>\n\n"
        f"💸 Ставка: {format_balance(game['bet'])}\n"
        f"🎯 Выигрыш: {format_balance(win)} (x{multiplier:.2f})",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    
    del user_tower_games[game_id]

@dp.callback_query(lambda c: c.data.startswith("tower_cancel:"))
async def tower_cancel_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    game_id = callback.data.split(":")[1]
    
    game = user_tower_games.get(game_id)
    if not game:
        await callback.answer("❌ Игра не найдена!", show_alert=True)
        return
    
    if game["user_id"] != user_id:
        await callback.answer("❌ Это не твоя игра!", show_alert=True)
        return
    
    if game["level"] != 0:
        await callback.answer("❌ Нельзя отменить после хода!", show_alert=True)
        return
    
    update_balance(user_id, game["bet"])
    
    await callback.message.edit_text(
        f"❌ <b>Игра отменена!</b>\n\n"
        f"💸 Ставка возвращена: {format_balance(game['bet'])}",
        parse_mode=ParseMode.HTML
    )
    
    del user_tower_games[game_id]

@dp.callback_query(lambda c: c.data == "noop")
async def noop_callback(callback: types.CallbackQuery):
    await callback.answer()

@dp.message(Command("b"))
async def b_handler(message: types.Message):
    user_id = message.from_user.id
    
    if is_private_chat(message):
        if not is_user_registered(user_id):
            await send_unregistered_warning(message)
            return
    else:
        if not is_user_registered(user_id):
            await send_unregistered_warning(message)

@dp.message(Command("info"))
async def info_handler(message: types.Message):
    if not is_private_chat(message):
        return
    
    user_id = message.from_user.id
    
    if user_id != ADMIN_ID:
        await message.answer("⛔ У вас нет доступа к этой команде.")
        return
    
    total_users = get_total_users()
    await message.answer(f"📊 <b>Статистика бота</b>\n\n👥 Всего зарегистрированных пользователей: <b>{total_users}</b>", parse_mode=ParseMode.HTML)

@dp.callback_query(lambda c: c.data == "play")
async def play_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    
    if not is_user_registered(user_id):
        await callback.answer("❌ Вы не зарегистрированы!", show_alert=True)
        return
    
    await callback.answer()
    await callback.message.answer(
        "🎮 <b>Доступные игры:</b>\n\n"
        "🚀 <b>Краш</b> - /crash [сумма] [множитель]\n"
        "   Пример: /crash 100 2.5\n\n"
        "🎰 <b>Рулетка</b> - /roulette [сумма] [ставка]\n"
        "   Ставки: красное, черное, четное, нечетное\n"
        "   Пример: /roulette 500 красное\n\n"
        "🏯 <b>Башня</b> - /tower [сумма]\n"
        "   Пример: /tower 500",
        parse_mode=ParseMode.HTML
    )

async def main():
    global BOT_USERNAME
    init_db()
    me = await bot.get_me()
    BOT_USERNAME = me.username
    print(f"Бот запущен: @{BOT_USERNAME}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())