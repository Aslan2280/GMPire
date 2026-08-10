import asyncio
import random
import uuid
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode, ChatType
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.storage.memory import MemoryStorage

from database import init_db, add_user, is_user_registered, get_total_users, get_balance, update_balance, update_stats, get_last_bonus, update_last_bonus

TOKEN = "7968492757:AAGKGsHjyJe6JMEtdnYqLx5tTi4faaD0jSc"
ADMIN_ID = 6025818386
ADMIN_ID_2 = 123456789

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

BOT_USERNAME = None
unregistered_warned = set()

ADMINS = [ADMIN_ID, ADMIN_ID_2]

TOWER_MULTIPLIERS = [1.19, 1.48, 1.86, 2.32, 2.9, 3.62, 4.53, 5.66, 7.08]
GOLD_MULTIPLIERS = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096]

user_tower_games = {}
user_gold_games = {}
user_mines_games = {}
user_diamond_games = {}
active_duels = {}

CUSTOM_EMOJIS = {
    "rocket": '<tg-emoji emoji-id="5283080528818360566">🚀</tg-emoji>',
    "chart_up": '<tg-emoji emoji-id="5373001317042101552">📈</tg-emoji>',
    "chart_down": '<tg-emoji emoji-id="5361748661640372834">📉</tg-emoji>',
    "check": '<tg-emoji emoji-id="5021905410089550576">✅</tg-emoji>',
    "cross": '<tg-emoji emoji-id="5019523782004441717">❌</tg-emoji>',
    "dice": '<tg-emoji emoji-id="5260547274957672345">🎲</tg-emoji>',
    "roulette": '<tg-emoji emoji-id="5235989279024373566">🎰</tg-emoji>',
    "tower": '<tg-emoji emoji-id="">🏯</tg-emoji>',
    "gold": '<tg-emoji emoji-id="5197371802136892976">⛏️</tg-emoji>',
    "mine": '<tg-emoji emoji-id="5454225015534805938">💣</tg-emoji>',
    "diamond": '<tg-emoji emoji-id="5956031393623445676">💠</tg-emoji>',
    "chest": '<tg-emoji emoji-id="">📦</tg-emoji>',
    "duel": '<tg-emoji emoji-id="5454014806950429357">⚔️</tg-emoji>',
    "money": '<tg-emoji emoji-id="5224257782013769471">💰</tg-emoji>',
    "balance": '<tg-emoji emoji-id="5445353829304387411">💳</tg-emoji>',
    "bonus": '<tg-emoji emoji-id="5348297073177406710">🎁</tg-emoji>',
    "question": '<tg-emoji emoji-id="5436113877181941026">❔</tg-emoji>',
    "safe": '<tg-emoji emoji-id="">🌀</tg-emoji>',
    "bomb": '<tg-emoji emoji-id="5276032951342088188">💥</tg-emoji>',
    "mine_field": '<tg-emoji emoji-id="5454225015534805938">💣</tg-emoji>',
    "empty": '<tg-emoji emoji-id="">▫️</tg-emoji>',
    "crown": '<tg-emoji emoji-id="5280769763398671636">🏆</tg-emoji>',
    "star": '<tg-emoji emoji-id="5438496463044752972">⭐</tg-emoji>',
    "fire": '<tg-emoji emoji-id="5424972470023104089">🔥</tg-emoji>',
    "sparkles": '<tg-emoji emoji-id="5219834485389927168">✨</tg-emoji>',
    "lock": '<tg-emoji emoji-id="5197288647275071607">🔒</tg-emoji>',
    "unlock": '<tg-emoji emoji-id="5197288647275071607">🔓</tg-emoji>',
    "warning": '<tg-emoji emoji-id="5807697589885212714">⚠️</tg-emoji>',
    "info": '<tg-emoji emoji-id="">ℹ️</tg-emoji>',
    "help": '<tg-emoji emoji-id="">🆘</tg-emoji>',
    "admin": '<tg-emoji emoji-id="5217822164362739968">👑</tg-emoji>',
    "user": '<tg-emoji emoji-id="">👤</tg-emoji>',
    "registered": '<tg-emoji emoji-id="5231200819986047254">📊</tg-emoji>',
    "send": '<tg-emoji emoji-id="5388632425314140043">📨</tg-emoji>',
    "broadcast": '<tg-emoji emoji-id="5388632425314140043">📢</tg-emoji>',
    "ban": '<tg-emoji emoji-id="5240241223632954241">🚫</tg-emoji>',
    "clear": '<tg-emoji emoji-id="">🗑️</tg-emoji>',
    "reset": '<tg-emoji emoji-id="">🔄</tg-emoji>',
    "add": '<tg-emoji emoji-id="">➕</tg-emoji>',
    "remove": '<tg-emoji emoji-id="">➖</tg-emoji>',
    "settings": '<tg-emoji emoji-id="">⚙️</tg-emoji>',
    "game": '<tg-emoji emoji-id="5260334416378496293">🎮</tg-emoji>',
    "play": '<tg-emoji emoji-id="">▶️</tg-emoji>',
    "stop": '<tg-emoji emoji-id="">⏹️</tg-emoji>',
    "pause": '<tg-emoji emoji-id="">⏸️</tg-emoji>',
    "next": '<tg-emoji emoji-id="">⏭️</tg-emoji>',
    "back": '<tg-emoji emoji-id="">⏮️</tg-emoji>',
    "up": '<tg-emoji emoji-id="">⬆️</tg-emoji>',
    "down": '<tg-emoji emoji-id="">⬇️</tg-emoji>',
    "left": '<tg-emoji emoji-id="">⬅️</tg-emoji>',
    "right": '<tg-emoji emoji-id="">➡️</tg-emoji>',
    "medal": '<tg-emoji emoji-id="">🥇</tg-emoji>',
    "medal2": '<tg-emoji emoji-id="">🥈</tg-emoji>',
    "medal3": '<tg-emoji emoji-id="">🥉</tg-emoji>',
    "gift": '<tg-emoji emoji-id="5907810849504727013">🎁</tg-emoji>',
    "party": '<tg-emoji emoji-id="">🎉</tg-emoji>',
    "sad": '<tg-emoji emoji-id="">😔</tg-emoji>',
    "happy": '<tg-emoji emoji-id="">😊</tg-emoji>',
    "cool": '<tg-emoji emoji-id="">😎</tg-emoji>',
    "heart": '<tg-emoji emoji-id="">❤️</tg-emoji>',
    "lightning": '<tg-emoji emoji-id="">⚡</tg-emoji>',
    "clock": '<tg-emoji emoji-id="">⏰</tg-emoji>',
    "calendar": '<tg-emoji emoji-id="">📅</tg-emoji>',
    "time": '<tg-emoji emoji-id="">⏳</tg-emoji>',
    "percent": '<tg-emoji emoji-id="">💯</tg-emoji>',
    "level": '<tg-emoji emoji-id="">🪜</tg-emoji>'
}

EMOJI_IDS = {
    "rocket": "5283080528818360566",
    "chart_up": "5373001317042101552",
    "chart_down": "5361748661640372834",
    "check": "5021905410089550576",
    "cross": "5019523782004441717",
    "dice": "5260547274957672345",
    "roulette": "5235989279024373566",
    "gold": "5197371802136892976",
    "mine": "5454225015534805938",
    "diamond": "5956031393623445676",
    "duel": "5454014806950429357",
    "money": "5224257782013769471",
    "balance": "5445353829304387411",
    "bonus": "5348297073177406710",
    "question": "5436113877181941026",
    "bomb": "5276032951342088188",
    "sparkles": "5219834485389927168",
    "lock": "5197288647275071607",
    "unlock": "5197288647275071607",
    "warning": "5807697589885212714",
    "ban": "5240241223632954241",
    "game": "5260334416378496293",
    "play": "5350612670435313545",
    "party": "5352660205939890989",
    "crown": "5280769763398671636",
    "star": "5438496463044752972",
    "fire": "5424972470023104089",
    "admin": "5217822164362739968",
    "registered": "5231200819986047254",
    "send": "5388632425314140043",
    "broadcast": "5388632425314140043",
    "add": "5907797234210930711",
    "remove": "5907798295064081354",
    "gift": "5907810849504727013"
}

def get_emoji(key: str) -> str:
    return CUSTOM_EMOJIS.get(key, "❔")

def get_emoji_id(key: str) -> str:
    return EMOJI_IDS.get(key, "")

def is_private_chat(message: types.Message) -> bool:
    return message.chat.type == ChatType.PRIVATE

def is_admin(user_id: int) -> bool:
    return user_id in ADMINS

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
                    text=f"{get_emoji('unlock')} Зарегистрироваться",
                    url=f"https://t.me/{BOT_USERNAME}?start=none",
                    icon_custom_emoji_id=get_emoji_id("unlock")
                )
            ]
        ]
    )

    text = f"{get_emoji('warning')} <b>Ты не из наших! Для регистрации нажми кнопку ниже</b>"

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
        InlineKeyboardButton(text=f"{get_emoji('question')}", callback_data=f"tower:{game_id}:0", icon_custom_emoji_id=get_emoji_id("question")),
        InlineKeyboardButton(text=f"{get_emoji('question')}", callback_data=f"tower:{game_id}:1", icon_custom_emoji_id=get_emoji_id("question")),
        InlineKeyboardButton(text=f"{get_emoji('question')}", callback_data=f"tower:{game_id}:2", icon_custom_emoji_id=get_emoji_id("question")),
        InlineKeyboardButton(text=f"{get_emoji('question')}", callback_data=f"tower:{game_id}:3", icon_custom_emoji_id=get_emoji_id("question")),
        InlineKeyboardButton(text=f"{get_emoji('question')}", callback_data=f"tower:{game_id}:4", icon_custom_emoji_id=get_emoji_id("question"))
    ])
    
    for i in range(level - 1, -1, -1):
        row = []
        for j in range(5):
            if i < len(selected) and selected[i] == j:
                row.append(InlineKeyboardButton(text=f"{get_emoji('safe')}", callback_data="noop", icon_custom_emoji_id=get_emoji_id("safe")))
            else:
                row.append(InlineKeyboardButton(text=f"{get_emoji('question')}", callback_data="noop", icon_custom_emoji_id=get_emoji_id("question")))
        kb.append(row)
    
    if level == 0:
        kb.append([InlineKeyboardButton(text=f"{get_emoji('cross')} Отмена", callback_data=f"tower_cancel:{game_id}", icon_custom_emoji_id=get_emoji_id("cross"))])
    else:
        kb.append([InlineKeyboardButton(text=f"{get_emoji('money')} Забрать", callback_data=f"tower_collect:{game_id}", icon_custom_emoji_id=get_emoji_id("money"))])
    
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
                    row.append(InlineKeyboardButton(text=f"{get_emoji('bomb')}", callback_data="noop", icon_custom_emoji_id=get_emoji_id("bomb")))
                else:
                    row.append(InlineKeyboardButton(text=f"{get_emoji('mine_field')}", callback_data="noop", icon_custom_emoji_id=get_emoji_id("mine_field")))
            elif i < len(selected) and selected[i] == j:
                row.append(InlineKeyboardButton(text=f"{get_emoji('safe')}", callback_data="noop", icon_custom_emoji_id=get_emoji_id("safe")))
            else:
                row.append(InlineKeyboardButton(text=f"{get_emoji('empty')}", callback_data="noop", icon_custom_emoji_id=get_emoji_id("empty")))
        kb.append(row)
    
    return InlineKeyboardMarkup(inline_keyboard=kb)

def build_gold_keyboard(user_id: int, game_id: str, level: int) -> InlineKeyboardMarkup:
    if level == 0:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=f"{get_emoji('question')}", callback_data=f"gold:{game_id}:0", icon_custom_emoji_id=get_emoji_id("question")),
                    InlineKeyboardButton(text=f"{get_emoji('question')}", callback_data=f"gold:{game_id}:1", icon_custom_emoji_id=get_emoji_id("question"))
                ],
                [
                    InlineKeyboardButton(text=f"{get_emoji('cross')} Отмена", callback_data=f"gold_cancel:{game_id}", icon_custom_emoji_id=get_emoji_id("cross"))
                ]
            ]
        )
    else:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=f"{get_emoji('question')}", callback_data=f"gold:{game_id}:0", icon_custom_emoji_id=get_emoji_id("question")),
                    InlineKeyboardButton(text=f"{get_emoji('question')}", callback_data=f"gold:{game_id}:1", icon_custom_emoji_id=get_emoji_id("question"))
                ],
                [
                    InlineKeyboardButton(text=f"{get_emoji('money')} Забрать", callback_data=f"gold_collect:{game_id}", icon_custom_emoji_id=get_emoji_id("money"))
                ]
            ]
        )

def build_mines_keyboard(game_id: str) -> InlineKeyboardMarkup:
    game = user_mines_games.get(game_id)
    if not game:
        return InlineKeyboardMarkup(inline_keyboard=[])
    
    kb = []
    for row in range(5):
        row_buttons = []
        for col in range(5):
            idx = row * 5 + col
            row_buttons.append(
                InlineKeyboardButton(
                    text=game["field"][idx],
                    callback_data=f"mines:{game_id}:{idx}"
                )
            )
        kb.append(row_buttons)
    
    opened = len(game.get("opened", []))
    if opened > 0:
        kb.append([
            InlineKeyboardButton(
                text=f"{get_emoji('money')} Забрать",
                callback_data=f"mines_collect:{game_id}",
                icon_custom_emoji_id=get_emoji_id("money")
            )
        ])
    else:
        kb.append([
            InlineKeyboardButton(
                text=f"{get_emoji('cross')} Отмена",
                callback_data=f"mines_cancel:{game_id}",
                icon_custom_emoji_id=get_emoji_id("cross")
            )
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=kb)

def build_final_mines_keyboard(field) -> InlineKeyboardMarkup:
    kb = []
    for row in range(5):
        row_buttons = []
        for col in range(5):
            idx = row * 5 + col
            row_buttons.append(
                InlineKeyboardButton(text=field[idx], callback_data="noop")
            )
        kb.append(row_buttons)
    return InlineKeyboardMarkup(inline_keyboard=kb)

def build_diamond_keyboard(game_id: str) -> InlineKeyboardMarkup:
    game = user_diamond_games.get(game_id)
    if not game:
        return InlineKeyboardMarkup(inline_keyboard=[])
    
    level = game.get("level", 0)
    selected = game.get("selected", [])
    
    if game.get("lost", False) or level >= 50:
        return InlineKeyboardMarkup(inline_keyboard=[])
    
    kb = []
    
    start_prev = max(0, level - 8)
    for i in range(start_prev, level):
        choice = selected[i] if i < len(selected) else None
        row_buttons = []
        for j in range(3):
            if choice is not None and choice == j:
                row_buttons.append(InlineKeyboardButton(text=f"{get_emoji('diamond')}", callback_data="noop", icon_custom_emoji_id=get_emoji_id("diamond")))
            else:
                row_buttons.append(InlineKeyboardButton(text=f"{get_emoji('question')}", callback_data="noop", icon_custom_emoji_id=get_emoji_id("question")))
        kb.append(row_buttons)
    
    kb.append([
        InlineKeyboardButton(text=f"{get_emoji('question')}", callback_data=f"diamond:{game_id}:0", icon_custom_emoji_id=get_emoji_id("question")),
        InlineKeyboardButton(text=f"{get_emoji('question')}", callback_data=f"diamond:{game_id}:1", icon_custom_emoji_id=get_emoji_id("question")),
        InlineKeyboardButton(text=f"{get_emoji('question')}", callback_data=f"diamond:{game_id}:2", icon_custom_emoji_id=get_emoji_id("question"))
    ])
    
    if level == 0:
        kb.append([InlineKeyboardButton(text=f"{get_emoji('cross')} Отмена", callback_data=f"diamond_cancel:{game_id}", icon_custom_emoji_id=get_emoji_id("cross"))])
    else:
        kb.append([InlineKeyboardButton(text=f"{get_emoji('money')} Забрать", callback_data=f"diamond_collect:{game_id}", icon_custom_emoji_id=get_emoji_id("money"))])
    
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
                f"{get_emoji('sparkles')} <b>Привет! Ты в GMPire — место, где время летит незаметно</b>\n\n"
                f"{get_emoji('game')} Тут ты можешь найти интересные игры!\n\n"
                f"Соревнуйся с друзьями или же другими игроками и продвигай свой чат либо канал {get_emoji('crown')}"
            )
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Играть",
                            callback_data="play",
                            icon_custom_emoji_id=get_emoji_id("play")
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Добавить бота в чат",
                            url=f"https://t.me/{BOT_USERNAME}?startgroup=start",
                            icon_custom_emoji_id=get_emoji_id("add")
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
            f"{get_emoji('sparkles')} <b>Привет! Ты в GMPire — место, где время летит незаметно</b>\n\n"
            f"{get_emoji('game')} Тут ты можешь найти интересные игры!\n\n"
            f"Соревнуйся с друзьями или же другими игроками и продвигай свой чат либо канал {get_emoji('crown')}"
        )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Играть",
                        callback_data="play",
                        icon_custom_emoji_id=get_emoji_id("play")
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Добавить бота в чат",
                        url=f"https://t.me/{BOT_USERNAME}?startgroup=start",
                        icon_custom_emoji_id=get_emoji_id("add")
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
            f"{get_emoji('help')} <b>Список игр и команд:</b>\n\n"
            f"{get_emoji('roulette')} <b>Рулетка</b> - рул [сумма] [ставка]\n"
            f"   Ставки: красное, черное, четное, нечетное\n"
            f"   Пример: рул 500 красное\n\n"
            f"{get_emoji('rocket')} <b>Краш</b> - краш [сумма] [множитель]\n"
            f"   Пример: краш 100 2.5\n\n"
            f"{get_emoji('dice')} <b>Кости</b> - кости [сумма] [м|б|равно]\n"
            f"   Пример: кости 500 б\n\n"
            f"{get_emoji('tower')} <b>Башня</b> - башня [сумма]\n"
            f"   Пример: башня 500\n\n"
            f"{get_emoji('gold')} <b>Золото</b> - золото [сумма]\n"
            f"   Пример: золото 500\n\n"
            f"{get_emoji('mine')} <b>Мины</b> - мины [сумма] [мин]\n"
            f"   Пример: мины 500 3\n\n"
            f"{get_emoji('diamond')} <b>Алмазы</b> - алмазы [сумма] [мин]\n"
            f"   Пример: алмазы 500 1\n\n"
            f"{get_emoji('chest')} <b>Сундуки</b> - сундуки [сумма]\n"
            f"   Пример: сундуки 500\n\n"
            f"{get_emoji('duel')} <b>Дуэль</b> - дуэль [сумма]\n"
            f"   Пример: дуэль 500\n\n"
            f"{get_emoji('money')} <b>Баланс</b> - б или баланс\n"
            f"{get_emoji('bonus')} <b>Бонус</b> - бонус",
            parse_mode=ParseMode.HTML
        )
    else:
        if not is_user_registered(user_id):
            await send_unregistered_warning(message)

@dp.message(lambda message: message.text.lower() in ["б", "баланс"])
async def balance_text_handler(message: types.Message):
    user_id = message.from_user.id
    
    if is_private_chat(message):
        if not is_user_registered(user_id):
            await send_unregistered_warning(message)
            return
        
        balance = get_balance(user_id)
        await message.answer(f"{get_emoji('money')} Ваш баланс: <b>{format_balance(balance)}</b> монет", parse_mode=ParseMode.HTML)
    else:
        if not is_user_registered(user_id):
            await send_unregistered_warning(message)

@dp.message(lambda message: message.text.lower() == "бонус")
async def bonus_handler(message: types.Message):
    user_id = message.from_user.id
    
    if not is_private_chat(message):
        if not is_user_registered(user_id):
            await send_unregistered_warning(message)
        return
    
    if not is_user_registered(user_id):
        await send_unregistered_warning(message)
        return
    
    last_bonus = get_last_bonus(user_id)
    
    if last_bonus:
        try:
            last_time = datetime.fromisoformat(last_bonus)
            if datetime.now() - last_time < timedelta(hours=1):
                remaining = timedelta(hours=1) - (datetime.now() - last_time)
                minutes = int(remaining.total_seconds() / 60)
                await message.answer(
                    f"{get_emoji('time')} Ты уже получал бонус! Подожди {minutes} минут.",
                    parse_mode=ParseMode.HTML
                )
                return
        except:
            pass
    
    balance = get_balance(user_id)
    bonus = random.randint(1000, 5000)
    
    update_balance(user_id, bonus)
    update_last_bonus(user_id)
    
    await message.answer(
        f"{get_emoji('bonus')} <b>Ты получил бонус!</b>\n\n"
        f"{get_emoji('money')} Бонус: {format_balance(bonus)}\n"
        f"{get_emoji('balance')} Баланс: {format_balance(get_balance(user_id))}",
        parse_mode=ParseMode.HTML
    )

@dp.message(lambda message: message.text.lower().startswith("краш"))
async def crash_text_handler(message: types.Message):
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
            f"{get_emoji('cross')} Неверный формат!\n"
            "Пример: <code>краш 100 2.5</code>\n"
            "Пример: <code>краш все 3</code>",
            parse_mode=ParseMode.HTML
        )
        return
    
    bet_str = args[1]
    try:
        multiplier = float(args[2].replace(",", "."))
    except:
        await message.answer(f"{get_emoji('cross')} Неверный множитель!")
        return
    
    if multiplier < 1.01 or multiplier > 10:
        await message.answer(f"{get_emoji('cross')} Множитель должен быть от 1.01 до 10.00")
        return
    
    balance = get_balance(user_id)
    
    if bet_str.lower() == "все":
        bet = balance
    else:
        bet = parse_bet(bet_str)
    
    if bet <= 0:
        await message.answer(f"{get_emoji('cross')} Неверная сумма ставки!")
        return
    
    if bet > balance:
        await message.answer(f"{get_emoji('cross')} Недостаточно средств! Ваш баланс: {format_balance(balance)}")
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
            f"{get_emoji('rocket')} <b>Ракета улетела на x{crash_multiplier:.2f}</b> {get_emoji('chart_up')}\n"
            f"{get_emoji('check')} <b>Ты выиграл!</b> Твой выигрыш составил {format_balance(win)}",
            parse_mode=ParseMode.HTML
        )
    else:
        update_stats(user_id, lost=bet)
        
        await message.answer(
            f"{get_emoji('rocket')} <b>Ракета упала на x{crash_multiplier:.2f}</b> {get_emoji('chart_down')}\n"
            f"{get_emoji('cross')} <b>Ты проиграл</b> {format_balance(bet)}",
            parse_mode=ParseMode.HTML
        )

@dp.message(lambda message: message.text.lower().startswith("рул"))
async def roulette_text_handler(message: types.Message):
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
            f"{get_emoji('cross')} Неверный формат!\n"
            "Пример: <code>рул 500 красное</code>\n"
            "Пример: <code>рул все черное</code>\n\n"
            "Доступные ставки: красное, черное, четное, нечетное",
            parse_mode=ParseMode.HTML
        )
        return
    
    bet_str = args[1]
    bet_type = args[2].lower()
    
    valid_bets = ["красное", "черное", "четное", "нечетное"]
    if bet_type not in valid_bets:
        await message.answer(
            f"{get_emoji('cross')} Неверная ставка!\n"
            "Доступные ставки: красное, черное, четное, нечетное"
        )
        return
    
    balance = get_balance(user_id)
    
    if bet_str.lower() == "все":
        bet = balance
    else:
        bet = parse_bet(bet_str)
    
    if bet <= 0:
        await message.answer(f"{get_emoji('cross')} Неверная сумма ставки!")
        return
    
    if bet > balance:
        await message.answer(f"{get_emoji('cross')} Недостаточно средств! Ваш баланс: {format_balance(balance)}")
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
                f"{get_emoji('roulette')} <b>Рулетка!</b>\n\n"
                f"{get_emoji('star')} Выпало: <b>{number}</b> (зеленое)\n"
                f"{get_emoji('check')} <b>Ты выиграл!</b> {format_balance(win_amount)}",
                parse_mode=ParseMode.HTML
            )
        else:
            await message.answer(
                f"{get_emoji('roulette')} <b>Рулетка!</b>\n\n"
                f"{get_emoji('star')} Выпало: <b>{number}</b> ({color})\n"
                f"{get_emoji('check')} <b>Ты выиграл!</b> {format_balance(win_amount)}",
                parse_mode=ParseMode.HTML
            )
    else:
        update_stats(user_id, lost=bet)
        
        if number == 0:
            await message.answer(
                f"{get_emoji('roulette')} <b>Рулетка!</b>\n\n"
                f"{get_emoji('star')} Выпало: <b>{number}</b> (зеленое)\n"
                f"{get_emoji('cross')} <b>Ты проиграл</b> {format_balance(bet)}",
                parse_mode=ParseMode.HTML
            )
        else:
            await message.answer(
                f"{get_emoji('roulette')} <b>Рулетка!</b>\n\n"
                f"{get_emoji('star')} Выпало: <b>{number}</b> ({color})\n"
                f"{get_emoji('cross')} <b>Ты проиграл</b> {format_balance(bet)}",
                parse_mode=ParseMode.HTML
            )

@dp.message(lambda message: message.text.lower().startswith("кости"))
async def dice_text_handler(message: types.Message):
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
            f"{get_emoji('cross')} Неверный формат!\n"
            "Пример: <code>кости 500 б</code>\n"
            "Пример: <code>кости все равно</code>\n\n"
            "Доступные ставки: м (меньше 7), б (больше 7), равно (ровно 7)",
            parse_mode=ParseMode.HTML
        )
        return
    
    bet_str = args[1]
    bet_type = args[2].lower()
    
    if bet_type not in ["м", "б", "равно"]:
        await message.answer(
            f"{get_emoji('cross')} Неверная ставка!\n"
            "Доступные ставки: м, б, равно"
        )
        return
    
    balance = get_balance(user_id)
    
    if bet_str.lower() == "все":
        bet = balance
    else:
        bet = parse_bet(bet_str)
    
    if bet <= 0:
        await message.answer(f"{get_emoji('cross')} Неверная сумма ставки!")
        return
    
    if bet > balance:
        await message.answer(f"{get_emoji('cross')} Недостаточно средств! Ваш баланс: {format_balance(balance)}")
        return
    
    d1 = random.randint(1, 6)
    d2 = random.randint(1, 6)
    total = d1 + d2
    
    update_balance(user_id, -bet)
    
    win = False
    if bet_type == "м" and total < 7:
        win = True
        multiplier = 2.25
    elif bet_type == "б" and total > 7:
        win = True
        multiplier = 2.25
    elif bet_type == "равно" and total == 7:
        win = True
        multiplier = 5
    
    if win:
        win_amount = int(bet * multiplier)
        update_balance(user_id, win_amount)
        update_stats(user_id, won=win_amount)
        
        await message.answer(
            f"{get_emoji('dice')} <b>Кости!</b>\n\n"
            f"{get_emoji('star')} Выпало: <b>{d1}</b> и <b>{d2}</b> = <b>{total}</b>\n"
            f"{get_emoji('check')} <b>Ты выиграл!</b> {format_balance(win_amount)}",
            parse_mode=ParseMode.HTML
        )
    else:
        update_stats(user_id, lost=bet)
        
        await message.answer(
            f"{get_emoji('dice')} <b>Кости!</b>\n\n"
            f"{get_emoji('star')} Выпало: <b>{d1}</b> и <b>{d2}</b> = <b>{total}</b>\n"
            f"{get_emoji('cross')} <b>Ты проиграл</b> {format_balance(bet)}",
            parse_mode=ParseMode.HTML
        )

@dp.message(lambda message: message.text.lower().startswith("башня"))
async def tower_text_handler(message: types.Message):
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
            f"{get_emoji('cross')} Неверный формат!\n"
            "Пример: <code>башня 500</code>\n"
            "Пример: <code>башня все</code>",
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
        await message.answer(f"{get_emoji('cross')} Неверная сумма ставки!")
        return
    
    if bet > balance:
        await message.answer(f"{get_emoji('cross')} Недостаточно средств! Ваш баланс: {format_balance(balance)}")
        return
    
    update_balance(user_id, -bet)
    
    bombs = []
    for _ in range(9):
        row = [0, 0, 0, 0, 0]
        bomb_index = random.randint(0, 4)
        row[bomb_index] = 1
        bombs.append(row)
    
    game_id = str(uuid.uuid4())[:8]
    
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
        f"{get_emoji('tower')} <b>Игра Башня!</b>\n\n"
        f"{get_emoji('money')} Ставка: {format_balance(bet)}\n"
        f"{get_emoji('level')} Уровень: 1/9\n"
        f"{get_emoji('money')} Возможный выигрыш: {format_balance(int(bet * TOWER_MULTIPLIERS[0]))} (x{TOWER_MULTIPLIERS[0]:.2f})\n\n"
        f"Выбери ячейку:",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )

@dp.message(lambda message: message.text.lower().startswith("золото"))
async def gold_text_handler(message: types.Message):
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
            f"{get_emoji('cross')} Неверный формат!\n"
            "Пример: <code>золото 500</code>\n"
            "Пример: <code>золото все</code>",
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
        await message.answer(f"{get_emoji('cross')} Неверная сумма ставки!")
        return
    
    if bet > balance:
        await message.answer(f"{get_emoji('cross')} Недостаточно средств! Ваш баланс: {format_balance(balance)}")
        return
    
    update_balance(user_id, -bet)
    
    bad_cells = [random.randint(0, 1) for _ in range(12)]
    game_id = str(uuid.uuid4())[:8]
    
    user_gold_games[game_id] = {
        "user_id": user_id,
        "bet": bet,
        "bad_cells": bad_cells,
        "level": 0,
        "path": [],
        "lost": False
    }
    
    keyboard = build_gold_keyboard(user_id, game_id, 0)
    
    await message.answer(
        f"{get_emoji('gold')} <b>Игра Золото!</b>\n\n"
        f"{get_emoji('money')} Ставка: {format_balance(bet)}\n"
        f"{get_emoji('level')} Уровень: 1/12\n"
        f"{get_emoji('money')} Возможный выигрыш: {format_balance(bet * 2)} (x2)\n\n"
        f"Выбери ячейку:",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )

@dp.message(lambda message: message.text.lower().startswith("мины"))
async def mines_text_handler(message: types.Message):
    user_id = message.from_user.id
    
    if not is_private_chat(message):
        if not is_user_registered(user_id):
            await send_unregistered_warning(message)
        return
    
    if not is_user_registered(user_id):
        await send_unregistered_warning(message)
        return
    
    args = message.text.split()
    if len(args) not in [2, 3]:
        await message.answer(
            f"{get_emoji('cross')} Неверный формат!\n"
            "Пример: <code>мины 500 3</code>\n"
            "Пример: <code>мины все</code>",
            parse_mode=ParseMode.HTML
        )
        return
    
    bet_str = args[1]
    mines_count = int(args[2]) if len(args) == 3 else 3
    
    if mines_count < 1 or mines_count > 6:
        await message.answer(f"{get_emoji('cross')} Количество мин должно быть от 1 до 6")
        return
    
    balance = get_balance(user_id)
    
    if bet_str.lower() == "все":
        bet = balance
    else:
        bet = parse_bet(bet_str)
    
    if bet <= 0:
        await message.answer(f"{get_emoji('cross')} Неверная сумма ставки!")
        return
    
    if bet > balance:
        await message.answer(f"{get_emoji('cross')} Недостаточно средств! Ваш баланс: {format_balance(balance)}")
        return
    
    update_balance(user_id, -bet)
    
    field = ["❔"] * 25
    mines = random.sample(range(25), mines_count)
    game_id = str(uuid.uuid4())[:8]
    
    user_mines_games[game_id] = {
        "user_id": user_id,
        "bet": bet,
        "field": field,
        "opened": [],
        "mines": mines,
        "mines_count": mines_count
    }
    
    keyboard = build_mines_keyboard(game_id)
    
    await message.answer(
        f"{get_emoji('mine')} <b>Игра Мины!</b>\n\n"
        f"{get_emoji('money')} Ставка: {format_balance(bet)}\n"
        f"{get_emoji('mine_field')} Мин: {mines_count}\n"
        f"{get_emoji('question')} Открыто: 0/25\n\n"
        f"Выбери ячейку:",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )

@dp.message(lambda message: message.text.lower().startswith("алмазы"))
async def diamond_text_handler(message: types.Message):
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
            f"{get_emoji('cross')} Неверный формат!\n"
            "Пример: <code>алмазы 500 1</code>\n"
            "Пример: <code>алмазы все 2</code>",
            parse_mode=ParseMode.HTML
        )
        return
    
    bet_str = args[1]
    mines_count = int(args[2])
    
    if mines_count < 1 or mines_count > 2:
        await message.answer(f"{get_emoji('cross')} Количество мин должно быть 1 или 2")
        return
    
    balance = get_balance(user_id)
    
    if bet_str.lower() == "все":
        bet = balance
    else:
        bet = parse_bet(bet_str)
    
    if bet <= 0:
        await message.answer(f"{get_emoji('cross')} Неверная сумма ставки!")
        return
    
    if bet > balance:
        await message.answer(f"{get_emoji('cross')} Недостаточно средств! Ваш баланс: {format_balance(balance)}")
        return
    
    update_balance(user_id, -bet)
    
    bombs = []
    for _ in range(50):
        row = [0, 0, 0]
        mine_positions = random.sample(range(3), mines_count)
        for p in mine_positions:
            row[p] = 1
        bombs.append(row)
    
    game_id = str(uuid.uuid4())[:8]
    
    user_diamond_games[game_id] = {
        "user_id": user_id,
        "bet": bet,
        "level": 0,
        "bombs": bombs,
        "selected": [],
        "lost": False,
        "mines_count": mines_count
    }
    
    keyboard = build_diamond_keyboard(game_id)
    
    await message.answer(
        f"{get_emoji('diamond')} <b>Игра Алмазы!</b>\n\n"
        f"{get_emoji('money')} Ставка: {format_balance(bet)}\n"
        f"{get_emoji('mine_field')} Мин в ряду: {mines_count}\n"
        f"{get_emoji('level')} Уровень: 1/50\n\n"
        f"Выбери ячейку:",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )

@dp.message(lambda message: message.text.lower().startswith("сундуки"))
async def chest_text_handler(message: types.Message):
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
            f"{get_emoji('cross')} Неверный формат!\n"
            "Пример: <code>сундуки 500</code>\n"
            "Пример: <code>сундуки все</code>",
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
        await message.answer(f"{get_emoji('cross')} Неверная сумма ставки!")
        return
    
    if bet > balance:
        await message.answer(f"{get_emoji('cross')} Недостаточно средств! Ваш баланс: {format_balance(balance)}")
        return
    
    update_balance(user_id, -bet)
    
    correct = random.randint(1, 4)
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{get_emoji('chest')} Сундук 1", callback_data=f"chest:{user_id}:{correct}:1:{bet}", icon_custom_emoji_id=get_emoji_id("chest"))],
            [InlineKeyboardButton(text=f"{get_emoji('chest')} Сундук 2", callback_data=f"chest:{user_id}:{correct}:2:{bet}", icon_custom_emoji_id=get_emoji_id("chest"))],
            [InlineKeyboardButton(text=f"{get_emoji('chest')} Сундук 3", callback_data=f"chest:{user_id}:{correct}:3:{bet}", icon_custom_emoji_id=get_emoji_id("chest"))],
            [InlineKeyboardButton(text=f"{get_emoji('chest')} Сундук 4", callback_data=f"chest:{user_id}:{correct}:4:{bet}", icon_custom_emoji_id=get_emoji_id("chest"))]
        ]
    )
    
    await message.answer(
        f"{get_emoji('chest')} <b>Игра Сундуки!</b>\n\n"
        f"{get_emoji('money')} Ставка: {format_balance(bet)}\n"
        f"Выбери сундук:",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )

@dp.message(lambda message: message.text.lower().startswith("дуэль"))
async def duel_text_handler(message: types.Message):
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
            f"{get_emoji('cross')} Неверный формат!\n"
            "Пример: <code>дуэль 500</code>\n"
            "Пример: <code>дуэль все</code>",
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
        await message.answer(f"{get_emoji('cross')} Неверная сумма ставки!")
        return
    
    if bet > balance:
        await message.answer(f"{get_emoji('cross')} Недостаточно средств! Ваш баланс: {format_balance(balance)}")
        return
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{get_emoji('check')} Принять дуэль",
                    callback_data=f"duel_accept:{user_id}:{bet}",
                    icon_custom_emoji_id=get_emoji_id("check")
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{get_emoji('cross')} Отменить",
                    callback_data=f"duel_cancel:{user_id}",
                    icon_custom_emoji_id=get_emoji_id("cross")
                )
            ]
        ]
    )
    
    await message.answer(
        f"{get_emoji('duel')} <b>Дуэль!</b>\n\n"
        f"{get_emoji('user')} {message.from_user.first_name} вызывает на дуэль!\n"
        f"{get_emoji('money')} Ставка: {format_balance(bet)}",
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
        await callback.answer(f"{get_emoji('cross')} Игра не найдена!", show_alert=True)
        return
    
    if game["user_id"] != user_id:
        await callback.answer(f"{get_emoji('cross')} Это не твоя игра!", show_alert=True)
        return
    
    if game.get("lost", False):
        await callback.answer(f"{get_emoji('cross')} Ты уже проиграл!", show_alert=True)
        return
    
    level = game["level"]
    if level >= 9:
        await callback.answer(f"{get_emoji('cross')} Игра уже завершена!", show_alert=True)
        return
    
    if choice < 0 or choice > 4:
        await callback.answer(f"{get_emoji('cross')} Неверный выбор!", show_alert=True)
        return
    
    game["selected"].append(choice)
    
    if game["bombs"][level][choice] == 1:
        game["lost"] = True
        update_stats(user_id, lost=game["bet"])
        
        keyboard = build_final_tower_keyboard(game_id)
        
        await callback.message.edit_text(
            f"{get_emoji('bomb')} <b>Ты попал на мину!</b>\n\n"
            f"{get_emoji('money')} Ставка: {format_balance(game['bet'])}",
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
            f"{get_emoji('crown')} <b>Поздравляем! Ты прошел башню!</b>\n\n"
            f"{get_emoji('money')} Выигрыш: {format_balance(win)} (x{TOWER_MULTIPLIERS[8]:.2f})",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
        
        del user_tower_games[game_id]
        return
    
    multiplier = TOWER_MULTIPLIERS[game["level"] - 1]
    potential_win = int(game["bet"] * multiplier)
    
    keyboard = build_tower_keyboard(user_id, game_id)
    
    await callback.message.edit_text(
        f"{get_emoji('tower')} <b>Игра Башня!</b>\n\n"
        f"{get_emoji('money')} Ставка: {format_balance(game['bet'])}\n"
        f"{get_emoji('level')} Уровень: {game['level'] + 1}/9\n"
        f"{get_emoji('money')} Возможный выигрыш: {format_balance(potential_win)} (x{multiplier:.2f})\n\n"
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
        await callback.answer(f"{get_emoji('cross')} Игра не найдена!", show_alert=True)
        return
    
    if game["user_id"] != user_id:
        await callback.answer(f"{get_emoji('cross')} Это не твоя игра!", show_alert=True)
        return
    
    if game.get("lost", False):
        await callback.answer(f"{get_emoji('cross')} Ты уже проиграл!", show_alert=True)
        return
    
    level = game["level"]
    if level == 0:
        await callback.answer(f"{get_emoji('cross')} Сделай хотя бы один ход!", show_alert=True)
        return
    
    multiplier = TOWER_MULTIPLIERS[level - 1]
    win = int(game["bet"] * multiplier)
    
    update_balance(user_id, win)
    update_stats(user_id, won=win)
    
    keyboard = build_final_tower_keyboard(game_id)
    
    await callback.message.edit_text(
        f"{get_emoji('money')} <b>Ты забрал выигрыш!</b>\n\n"
        f"{get_emoji('money')} Ставка: {format_balance(game['bet'])}\n"
        f"{get_emoji('star')} Выигрыш: {format_balance(win)} (x{multiplier:.2f})",
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
        await callback.answer(f"{get_emoji('cross')} Игра не найдена!", show_alert=True)
        return
    
    if game["user_id"] != user_id:
        await callback.answer(f"{get_emoji('cross')} Это не твоя игра!", show_alert=True)
        return
    
    if game["level"] != 0:
        await callback.answer(f"{get_emoji('cross')} Нельзя отменить после хода!", show_alert=True)
        return
    
    update_balance(user_id, game["bet"])
    
    await callback.message.edit_text(
        f"{get_emoji('cross')} <b>Игра отменена!</b>\n\n"
        f"{get_emoji('money')} Ставка возвращена: {format_balance(game['bet'])}",
        parse_mode=ParseMode.HTML
    )
    
    del user_tower_games[game_id]

@dp.callback_query(lambda c: c.data.startswith("gold:"))
async def gold_choose_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    parts = callback.data.split(":")
    game_id = parts[1]
    choice = int(parts[2])
    
    game = user_gold_games.get(game_id)
    if not game:
        await callback.answer(f"{get_emoji('cross')} Игра не найдена!", show_alert=True)
        return
    
    if game["user_id"] != user_id:
        await callback.answer(f"{get_emoji('cross')} Это не твоя игра!", show_alert=True)
        return
    
    if game.get("lost", False):
        await callback.answer(f"{get_emoji('cross')} Ты уже проиграл!", show_alert=True)
        return
    
    level = game["level"]
    if level >= 12:
        await callback.answer(f"{get_emoji('cross')} Игра уже завершена!", show_alert=True)
        return
    
    game["path"].append(choice)
    
    if game["bad_cells"][level] == choice:
        game["lost"] = True
        update_stats(user_id, lost=game["bet"])
        
        await callback.message.edit_text(
            f"{get_emoji('bomb')} <b>Ты проиграл!</b>\n\n"
            f"{get_emoji('money')} Ставка: {format_balance(game['bet'])}",
            parse_mode=ParseMode.HTML
        )
        
        del user_gold_games[game_id]
        return
    
    game["level"] = level + 1
    
    if game["level"] >= 12:
        win = int(game["bet"] * GOLD_MULTIPLIERS[11])
        update_balance(user_id, win)
        update_stats(user_id, won=win)
        
        await callback.message.edit_text(
            f"{get_emoji('crown')} <b>Поздравляем! Ты прошел игру!</b>\n\n"
            f"{get_emoji('money')} Выигрыш: {format_balance(win)} (x{GOLD_MULTIPLIERS[11]})",
            parse_mode=ParseMode.HTML
        )
        
        del user_gold_games[game_id]
        return
    
    multiplier = GOLD_MULTIPLIERS[game["level"]]
    potential_win = int(game["bet"] * multiplier)
    
    keyboard = build_gold_keyboard(user_id, game_id, game["level"])
    
    await callback.message.edit_text(
        f"{get_emoji('gold')} <b>Игра Золото!</b>\n\n"
        f"{get_emoji('money')} Ставка: {format_balance(game['bet'])}\n"
        f"{get_emoji('level')} Уровень: {game['level'] + 1}/12\n"
        f"{get_emoji('money')} Возможный выигрыш: {format_balance(potential_win)} (x{multiplier})\n\n"
        f"Выбери ячейку:",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )

@dp.callback_query(lambda c: c.data.startswith("gold_collect:"))
async def gold_collect_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    game_id = callback.data.split(":")[1]
    
    game = user_gold_games.get(game_id)
    if not game:
        await callback.answer(f"{get_emoji('cross')} Игра не найдена!", show_alert=True)
        return
    
    if game["user_id"] != user_id:
        await callback.answer(f"{get_emoji('cross')} Это не твоя игра!", show_alert=True)
        return
    
    level = game["level"]
    if level == 0:
        await callback.answer(f"{get_emoji('cross')} Сделай хотя бы один ход!", show_alert=True)
        return
    
    multiplier = GOLD_MULTIPLIERS[level - 1]
    win = int(game["bet"] * multiplier)
    
    update_balance(user_id, win)
    update_stats(user_id, won=win)
    
    await callback.message.edit_text(
        f"{get_emoji('money')} <b>Ты забрал выигрыш!</b>\n\n"
        f"{get_emoji('money')} Ставка: {format_balance(game['bet'])}\n"
        f"{get_emoji('star')} Выигрыш: {format_balance(win)} (x{multiplier})",
        parse_mode=ParseMode.HTML
    )
    
    del user_gold_games[game_id]

@dp.callback_query(lambda c: c.data.startswith("gold_cancel:"))
async def gold_cancel_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    game_id = callback.data.split(":")[1]
    
    game = user_gold_games.get(game_id)
    if not game:
        await callback.answer(f"{get_emoji('cross')} Игра не найдена!", show_alert=True)
        return
    
    if game["user_id"] != user_id:
        await callback.answer(f"{get_emoji('cross')} Это не твоя игра!", show_alert=True)
        return
    
    if game["level"] != 0:
        await callback.answer(f"{get_emoji('cross')} Нельзя отменить после хода!", show_alert=True)
        return
    
    update_balance(user_id, game["bet"])
    
    await callback.message.edit_text(
        f"{get_emoji('cross')} <b>Игра отменена!</b>\n\n"
        f"{get_emoji('money')} Ставка возвращена: {format_balance(game['bet'])}",
        parse_mode=ParseMode.HTML
    )
    
    del user_gold_games[game_id]

@dp.callback_query(lambda c: c.data.startswith("mines:"))
async def mines_choose_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    parts = callback.data.split(":")
    game_id = parts[1]
    idx = int(parts[2])
    
    game = user_mines_games.get(game_id)
    if not game:
        await callback.answer(f"{get_emoji('cross')} Игра не найдена!", show_alert=True)
        return
    
    if game["user_id"] != user_id:
        await callback.answer(f"{get_emoji('cross')} Это не твоя игра!", show_alert=True)
        return
    
    if idx in game["opened"]:
        await callback.answer(f"{get_emoji('cross')} Ячейка уже открыта!", show_alert=True)
        return
    
    if idx in game["mines"]:
        update_stats(user_id, lost=game["bet"])
        
        final_field = ["❔"] * 25
        for i in game["opened"]:
            final_field[i] = f"{get_emoji('safe')}"
        for m in game["mines"]:
            final_field[m] = f"{get_emoji('mine_field')}"
        final_field[idx] = f"{get_emoji('bomb')}"
        
        keyboard = build_final_mines_keyboard(final_field)
        
        await callback.message.edit_text(
            f"{get_emoji('bomb')} <b>Ты попал на мину!</b>\n\n"
            f"{get_emoji('money')} Ставка: {format_balance(game['bet'])}",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
        
        del user_mines_games[game_id]
        return
    
    game["opened"].append(idx)
    game["field"][idx] = f"{get_emoji('safe')}"
    
    opened = len(game["opened"])
    safe_needed = 25 - game["mines_count"]
    
    if opened >= safe_needed:
        win = int(game["bet"] * 2.5)
        update_balance(user_id, win)
        update_stats(user_id, won=win)
        
        final_field = ["❔"] * 25
        for i in game["opened"]:
            final_field[i] = f"{get_emoji('safe')}"
        for m in game["mines"]:
            final_field[m] = f"{get_emoji('mine_field')}"
        
        keyboard = build_final_mines_keyboard(final_field)
        
        await callback.message.edit_text(
            f"{get_emoji('crown')} <b>Поздравляем! Ты прошел поле!</b>\n\n"
            f"{get_emoji('money')} Выигрыш: {format_balance(win)}",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
        
        del user_mines_games[game_id]
        return
    
    keyboard = build_mines_keyboard(game_id)
    
    await callback.message.edit_text(
        f"{get_emoji('mine')} <b>Игра Мины!</b>\n\n"
        f"{get_emoji('money')} Ставка: {format_balance(game['bet'])}\n"
        f"{get_emoji('mine_field')} Мин: {game['mines_count']}\n"
        f"{get_emoji('question')} Открыто: {opened}/25\n\n"
        f"Выбери ячейку:",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )

@dp.callback_query(lambda c: c.data.startswith("mines_collect:"))
async def mines_collect_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    game_id = callback.data.split(":")[1]
    
    game = user_mines_games.get(game_id)
    if not game:
        await callback.answer(f"{get_emoji('cross')} Игра не найдена!", show_alert=True)
        return
    
    if game["user_id"] != user_id:
        await callback.answer(f"{get_emoji('cross')} Это не твоя игра!", show_alert=True)
        return
    
    opened = len(game["opened"])
    if opened == 0:
        await callback.answer(f"{get_emoji('cross')} Сделай хотя бы один ход!", show_alert=True)
        return
    
    multiplier = 1 + (opened * 0.1)
    win = int(game["bet"] * multiplier)
    
    update_balance(user_id, win)
    update_stats(user_id, won=win)
    
    final_field = ["❔"] * 25
    for i in game["opened"]:
        final_field[i] = f"{get_emoji('safe')}"
    for m in game["mines"]:
        final_field[m] = f"{get_emoji('mine_field')}"
    
    keyboard = build_final_mines_keyboard(final_field)
    
    await callback.message.edit_text(
        f"{get_emoji('money')} <b>Ты забрал выигрыш!</b>\n\n"
        f"{get_emoji('money')} Ставка: {format_balance(game['bet'])}\n"
        f"{get_emoji('star')} Выигрыш: {format_balance(win)} (x{multiplier:.2f})",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    
    del user_mines_games[game_id]

@dp.callback_query(lambda c: c.data.startswith("mines_cancel:"))
async def mines_cancel_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    game_id = callback.data.split(":")[1]
    
    game = user_mines_games.get(game_id)
    if not game:
        await callback.answer(f"{get_emoji('cross')} Игра не найдена!", show_alert=True)
        return
    
    if game["user_id"] != user_id:
        await callback.answer(f"{get_emoji('cross')} Это не твоя игра!", show_alert=True)
        return
    
    if len(game["opened"]) != 0:
        await callback.answer(f"{get_emoji('cross')} Нельзя отменить после хода!", show_alert=True)
        return
    
    update_balance(user_id, game["bet"])
    
    await callback.message.edit_text(
        f"{get_emoji('cross')} <b>Игра отменена!</b>\n\n"
        f"{get_emoji('money')} Ставка возвращена: {format_balance(game['bet'])}",
        parse_mode=ParseMode.HTML
    )
    
    del user_mines_games[game_id]

@dp.callback_query(lambda c: c.data.startswith("diamond:"))
async def diamond_choose_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    parts = callback.data.split(":")
    game_id = parts[1]
    choice = int(parts[2])
    
    game = user_diamond_games.get(game_id)
    if not game:
        await callback.answer(f"{get_emoji('cross')} Игра не найдена!", show_alert=True)
        return
    
    if game["user_id"] != user_id:
        await callback.answer(f"{get_emoji('cross')} Это не твоя игра!", show_alert=True)
        return
    
    if game.get("lost", False):
        await callback.answer(f"{get_emoji('cross')} Ты уже проиграл!", show_alert=True)
        return
    
    level = game["level"]
    if level >= 50:
        await callback.answer(f"{get_emoji('cross')} Игра уже завершена!", show_alert=True)
        return
    
    if choice < 0 or choice > 2:
        await callback.answer(f"{get_emoji('cross')} Неверный выбор!", show_alert=True)
        return
    
    game["selected"].append(choice)
    
    if game["bombs"][level][choice] == 1:
        game["lost"] = True
        update_stats(user_id, lost=game["bet"])
        
        keyboard = build_diamond_keyboard(game_id)
        
        await callback.message.edit_text(
            f"{get_emoji('bomb')} <b>Ты попал на мину!</b>\n\n"
            f"{get_emoji('money')} Ставка: {format_balance(game['bet'])}",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
        
        del user_diamond_games[game_id]
        return
    
    game["level"] = level + 1
    
    if game["level"] >= 50:
        win = int(game["bet"] * 2.5)
        update_balance(user_id, win)
        update_stats(user_id, won=win)
        
        keyboard = build_diamond_keyboard(game_id)
        
        await callback.message.edit_text(
            f"{get_emoji('crown')} <b>Поздравляем! Ты прошел все уровни!</b>\n\n"
            f"{get_emoji('money')} Выигрыш: {format_balance(win)}",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
        
        del user_diamond_games[game_id]
        return
    
    multiplier = 1 + (game["level"] * 0.03)
    potential_win = int(game["bet"] * multiplier)
    
    keyboard = build_diamond_keyboard(game_id)
    
    await callback.message.edit_text(
        f"{get_emoji('diamond')} <b>Игра Алмазы!</b>\n\n"
        f"{get_emoji('money')} Ставка: {format_balance(game['bet'])}\n"
        f"{get_emoji('mine_field')} Мин в ряду: {game['mines_count']}\n"
        f"{get_emoji('level')} Уровень: {game['level'] + 1}/50\n"
        f"{get_emoji('money')} Возможный выигрыш: {format_balance(potential_win)} (x{multiplier:.2f})\n\n"
        f"Выбери ячейку:",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )

@dp.callback_query(lambda c: c.data.startswith("diamond_collect:"))
async def diamond_collect_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    game_id = callback.data.split(":")[1]
    
    game = user_diamond_games.get(game_id)
    if not game:
        await callback.answer(f"{get_emoji('cross')} Игра не найдена!", show_alert=True)
        return
    
    if game["user_id"] != user_id:
        await callback.answer(f"{get_emoji('cross')} Это не твоя игра!", show_alert=True)
        return
    
    level = game["level"]
    if level == 0:
        await callback.answer(f"{get_emoji('cross')} Сделай хотя бы один ход!", show_alert=True)
        return
    
    multiplier = 1 + (level * 0.03)
    win = int(game["bet"] * multiplier)
    
    update_balance(user_id, win)
    update_stats(user_id, won=win)
    
    keyboard = build_diamond_keyboard(game_id)
    
    await callback.message.edit_text(
        f"{get_emoji('money')} <b>Ты забрал выигрыш!</b>\n\n"
        f"{get_emoji('money')} Ставка: {format_balance(game['bet'])}\n"
        f"{get_emoji('star')} Выигрыш: {format_balance(win)} (x{multiplier:.2f})",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    
    del user_diamond_games[game_id]

@dp.callback_query(lambda c: c.data.startswith("diamond_cancel:"))
async def diamond_cancel_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    game_id = callback.data.split(":")[1]
    
    game = user_diamond_games.get(game_id)
    if not game:
        await callback.answer(f"{get_emoji('cross')} Игра не найдена!", show_alert=True)
        return
    
    if game["user_id"] != user_id:
        await callback.answer(f"{get_emoji('cross')} Это не твоя игра!", show_alert=True)
        return
    
    if game["level"] != 0:
        await callback.answer(f"{get_emoji('cross')} Нельзя отменить после хода!", show_alert=True)
        return
    
    update_balance(user_id, game["bet"])
    
    await callback.message.edit_text(
        f"{get_emoji('cross')} <b>Игра отменена!</b>\n\n"
        f"{get_emoji('money')} Ставка возвращена: {format_balance(game['bet'])}",
        parse_mode=ParseMode.HTML
    )
    
    del user_diamond_games[game_id]

@dp.callback_query(lambda c: c.data.startswith("chest:"))
async def chest_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    parts = callback.data.split(":")
    owner_id = int(parts[1])
    correct = int(parts[2])
    choice = int(parts[3])
    bet = int(parts[4])
    
    if user_id != owner_id:
        await callback.answer(f"{get_emoji('cross')} Это не твоя игра!", show_alert=True)
        return
    
    if choice == correct:
        win = int(bet * 2.5)
        update_balance(user_id, win)
        update_stats(user_id, won=win)
        
        await callback.message.edit_text(
            f"{get_emoji('party')} <b>Ты угадал!</b>\n\n"
            f"{get_emoji('money')} Выигрыш: {format_balance(win)}",
            parse_mode=ParseMode.HTML
        )
    else:
        update_stats(user_id, lost=bet)
        
        await callback.message.edit_text(
            f"{get_emoji('cross')} <b>Ты не угадал!</b>\n\n"
            f"{get_emoji('money')} Ставка: {format_balance(bet)}\n"
            f"{get_emoji('chest')} Правильный сундук: {correct}",
            parse_mode=ParseMode.HTML
        )

@dp.callback_query(lambda c: c.data.startswith("duel_accept:"))
async def duel_accept_callback(callback: types.CallbackQuery):
    parts = callback.data.split(":")
    initiator_id = int(parts[1])
    bet = int(parts[2])
    opponent_id = callback.from_user.id
    
    if opponent_id == initiator_id:
        await callback.answer(f"{get_emoji('cross')} Нельзя принять свою дуэль!", show_alert=True)
        return
    
    initiator_balance = get_balance(initiator_id)
    opponent_balance = get_balance(opponent_id)
    
    if initiator_balance < bet:
        await callback.answer(f"{get_emoji('cross')} У создателя нет денег!", show_alert=True)
        return
    
    if opponent_balance < bet:
        await callback.answer(f"{get_emoji('cross')} У тебя нет денег!", show_alert=True)
        return
    
    update_balance(initiator_id, -bet)
    update_balance(opponent_id, -bet)
    
    await callback.message.edit_text(
        f"{get_emoji('duel')} <b>Дуэль началась!</b>\n\n"
        f"{get_emoji('money')} Ставка: {format_balance(bet)}",
        parse_mode=ParseMode.HTML
    )
    
    d1 = random.randint(1, 6)
    d2 = random.randint(1, 6)
    
    await callback.message.answer(f"{get_emoji('dice')} Игрок 1 выбросил: <b>{d1}</b>", parse_mode=ParseMode.HTML)
    await asyncio.sleep(1)
    await callback.message.answer(f"{get_emoji('dice')} Игрок 2 выбросил: <b>{d2}</b>", parse_mode=ParseMode.HTML)
    await asyncio.sleep(1)
    
    if d1 > d2:
        update_balance(initiator_id, bet * 2)
        update_stats(initiator_id, won=bet * 2)
        update_stats(opponent_id, lost=bet)
        
        await callback.message.answer(
            f"{get_emoji('crown')} <b>Победил игрок 1!</b>\n\n"
            f"{get_emoji('money')} Выигрыш: {format_balance(bet * 2)}",
            parse_mode=ParseMode.HTML
        )
    elif d2 > d1:
        update_balance(opponent_id, bet * 2)
        update_stats(opponent_id, won=bet * 2)
        update_stats(initiator_id, lost=bet)
        
        await callback.message.answer(
            f"{get_emoji('crown')} <b>Победил игрок 2!</b>\n\n"
            f"{get_emoji('money')} Выигрыш: {format_balance(bet * 2)}",
            parse_mode=ParseMode.HTML
        )
    else:
        update_balance(initiator_id, bet)
        update_balance(opponent_id, bet)
        
        await callback.message.answer(
            f"{get_emoji('heart')} <b>Ничья!</b>\n\n"
            f"{get_emoji('money')} Ставки возвращены",
            parse_mode=ParseMode.HTML
        )

@dp.callback_query(lambda c: c.data.startswith("duel_cancel:"))
async def duel_cancel_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    initiator_id = int(callback.data.split(":")[1])
    
    if user_id != initiator_id:
        await callback.answer(f"{get_emoji('cross')} Только создатель может отменить!", show_alert=True)
        return
    
    await callback.message.edit_text(
        f"{get_emoji('cross')} <b>Дуэль отменена!</b>",
        parse_mode=ParseMode.HTML
    )

@dp.callback_query(lambda c: c.data == "noop")
async def noop_callback(callback: types.CallbackQuery):
    await callback.answer()

@dp.message(Command("hhh"))
async def admin_add_coins_handler(message: types.Message):
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        await message.answer(f"{get_emoji('cross')} У вас нет доступа к этой команде.")
        return
    
    if not message.reply_to_message:
        await message.answer(f"{get_emoji('cross')} Ответьте на сообщение пользователя, которому хотите начислить монеты.")
        return
    
    args = message.text.split()
    if len(args) != 2:
        await message.answer(f"{get_emoji('cross')} Использование: /hhh [сумма]\nПример: /hhh 1000")
        return
    
    recipient_id = message.reply_to_message.from_user.id
    amount = parse_bet(args[1])
    
    if amount <= 0:
        await message.answer(f"{get_emoji('cross')} Неверная сумма!")
        return
    
    update_balance(recipient_id, amount)
    
    recipient_name = message.reply_to_message.from_user.first_name
    
    await message.answer(
        f"{get_emoji('check')} Начислено {format_balance(amount)} монет пользователю {recipient_name}",
        parse_mode=ParseMode.HTML
    )

@dp.message(Command("clear_b"))
async def admin_clear_balance_handler(message: types.Message):
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        await message.answer(f"{get_emoji('cross')} У вас нет доступа к этой команде.")
        return
    
    args = message.text.split()
    if len(args) != 2:
        await message.answer(f"{get_emoji('cross')} Использование: /clear_b [ID]\nПример: /clear_b 123456789")
        return
    
    try:
        target_id = int(args[1])
    except:
        await message.answer(f"{get_emoji('cross')} Неверный ID!")
        return
    
    if not is_user_registered(target_id):
        await message.answer(f"{get_emoji('cross')} Пользователь не найден!")
        return
    
    current_balance = get_balance(target_id)
    update_balance(target_id, -current_balance)
    
    await message.answer(
        f"{get_emoji('check')} Баланс пользователя {target_id} обнулен!",
        parse_mode=ParseMode.HTML
    )

@dp.message(Command("ban"))
async def admin_ban_handler(message: types.Message):
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        await message.answer(f"{get_emoji('cross')} У вас нет доступа к этой команде.")
        return
    
    args = message.text.split()
    if len(args) != 2:
        await message.answer(f"{get_emoji('cross')} Использование: /ban [ID]\nПример: /ban 123456789")
        return
    
    try:
        target_id = int(args[1])
    except:
        await message.answer(f"{get_emoji('cross')} Неверный ID!")
        return
    
    if target_id == ADMIN_ID or target_id == ADMIN_ID_2:
        await message.answer(f"{get_emoji('cross')} Нельзя забанить админа!")
        return
    
    if target_id in ADMINS:
        await message.answer(f"{get_emoji('cross')} Нельзя забанить админа!")
        return
    
    if not is_user_registered(target_id):
        await message.answer(f"{get_emoji('cross')} Пользователь не найден!")
        return
    
    await message.answer(
        f"{get_emoji('ban')} Пользователь {target_id} забанен!",
        parse_mode=ParseMode.HTML
    )

@dp.message(Command("unban"))
async def admin_unban_handler(message: types.Message):
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        await message.answer(f"{get_emoji('cross')} У вас нет доступа к этой команде.")
        return
    
    args = message.text.split()
    if len(args) != 2:
        await message.answer(f"{get_emoji('cross')} Использование: /unban [ID]\nПример: /unban 123456789")
        return
    
    try:
        target_id = int(args[1])
    except:
        await message.answer(f"{get_emoji('cross')} Неверный ID!")
        return
    
    await message.answer(
        f"{get_emoji('unban')} Пользователь {target_id} разбанен!",
        parse_mode=ParseMode.HTML
    )

@dp.message(Command("clear"))
async def admin_clear_user_handler(message: types.Message):
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        await message.answer(f"{get_emoji('cross')} У вас нет доступа к этой команде.")
        return
    
    args = message.text.split()
    if len(args) != 2:
        await message.answer(f"{get_emoji('cross')} Использование: /clear [ID]\nПример: /clear 123456789")
        return
    
    try:
        target_id = int(args[1])
    except:
        await message.answer(f"{get_emoji('cross')} Неверный ID!")
        return
    
    if not is_user_registered(target_id):
        await message.answer(f"{get_emoji('cross')} Пользователь не найден!")
        return
    
    current_balance = get_balance(target_id)
    update_balance(target_id, -current_balance)
    update_stats(target_id, won=0, lost=0)
    
    await message.answer(
        f"{get_emoji('clear')} Данные пользователя {target_id} очищены!",
        parse_mode=ParseMode.HTML
    )

@dp.message(Command("get"))
async def admin_get_user_handler(message: types.Message):
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        await message.answer(f"{get_emoji('cross')} У вас нет доступа к этой команде.")
        return
    
    args = message.text.split()
    if len(args) != 2:
        await message.answer(f"{get_emoji('cross')} Использование: /get [ID]\nПример: /get 123456789")
        return
    
    try:
        target_id = int(args[1])
    except:
        await message.answer(f"{get_emoji('cross')} Неверный ID!")
        return
    
    if not is_user_registered(target_id):
        await message.answer(f"{get_emoji('cross')} Пользователь не найден!")
        return
    
    balance = get_balance(target_id)
    
    await message.answer(
        f"{get_emoji('user')} <b>Информация о пользователе {target_id}</b>\n\n"
        f"{get_emoji('money')} Баланс: {format_balance(balance)} монет\n"
        f"{get_emoji('registered')} Статус: Пользователь",
        parse_mode=ParseMode.HTML
    )

@dp.message(Command("data"))
async def admin_data_handler(message: types.Message):
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        await message.answer(f"{get_emoji('cross')} У вас нет доступа к этой команде.")
        return
    
    args = message.text.split()
    if len(args) != 2:
        await message.answer(f"{get_emoji('cross')} Использование: /data [ID]\nПример: /data 123456789")
        return
    
    try:
        target_id = int(args[1])
    except:
        await message.answer(f"{get_emoji('cross')} Неверный ID!")
        return
    
    if not is_user_registered(target_id):
        await message.answer(f"{get_emoji('cross')} Пользователь не найден!")
        return
    
    balance = get_balance(target_id)
    
    await message.answer(
        f"{get_emoji('registered')} <b>Данные пользователя {target_id}</b>\n\n"
        f"{get_emoji('money')} Баланс: {balance}\n"
        f"{get_emoji('balance')} Форматированный: {format_balance(balance)}",
        parse_mode=ParseMode.HTML
    )

@dp.message(Command("rass"))
async def admin_broadcast_handler(message: types.Message):
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        await message.answer(f"{get_emoji('cross')} У вас нет доступа к этой команде.")
        return
    
    args = message.text.split(maxsplit=1)
    if len(args) != 2:
        await message.answer(f"{get_emoji('cross')} Использование: /rass [текст]\nПример: /rass Всем привет!")
        return
    
    broadcast_text = args[1]
    
    await message.answer(f"{get_emoji('broadcast')} <b>Рассылка запущена!</b>\n\nТекст: {broadcast_text}", parse_mode=ParseMode.HTML)
    
    sent = 0
    
    try:
        import sqlite3
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users")
        users = cursor.fetchall()
        conn.close()
        
        for user in users:
            try:
                await bot.send_message(user[0], broadcast_text, parse_mode=ParseMode.HTML)
                sent += 1
                await asyncio.sleep(0.05)
            except:
                pass
        
        await message.answer(f"{get_emoji('check')} Рассылка завершена!\nОтправлено: {sent} пользователям")
    except Exception as e:
        await message.answer(f"{get_emoji('cross')} Ошибка при рассылке: {e}")

@dp.message(Command("admin_send_message"))
async def admin_send_message_handler(message: types.Message):
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        await message.answer(f"{get_emoji('cross')} У вас нет доступа к этой команде.")
        return
    
    args = message.text.split()
    if len(args) < 3:
        await message.answer(f"{get_emoji('cross')} Использование: /admin_send_message [ID] [текст]")
        return
    
    try:
        target_id = int(args[1])
    except:
        await message.answer(f"{get_emoji('cross')} Неверный ID!")
        return
    
    if not is_user_registered(target_id):
        await message.answer(f"{get_emoji('cross')} Пользователь не найден!")
        return
    
    text = " ".join(args[2:])
    if not text:
        await message.answer(f"{get_emoji('cross')} Введите текст сообщения!")
        return
    
    try:
        await bot.send_message(target_id, text, parse_mode=ParseMode.HTML)
        await message.answer(f"{get_emoji('send')} Сообщение отправлено пользователю {target_id}")
    except Exception as e:
        await message.answer(f"{get_emoji('cross')} Ошибка при отправке: {e}")

@dp.message(Command("info"))
async def info_handler(message: types.Message):
    if not is_private_chat(message):
        return
    
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        await message.answer(f"{get_emoji('cross')} У вас нет доступа к этой команде.")
        return
    
    total_users = get_total_users()
    await message.answer(f"{get_emoji('registered')} <b>Статистика бота</b>\n\n{get_emoji('user')} Всего зарегистрированных пользователей: <b>{total_users}</b>", parse_mode=ParseMode.HTML)

@dp.callback_query(lambda c: c.data == "play")
async def play_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    
    if not is_user_registered(user_id):
        await callback.answer(f"{get_emoji('cross')} Вы не зарегистрированы!", show_alert=True)
        return
    
    await callback.answer()
    await callback.message.answer(
        f"{get_emoji('game')} <b>Все игры GMPire:</b>\n\n"
        f"{get_emoji('roulette')} <b>Рулетка</b> - рул [сумма] [ставка]\n"
        f"   Ставки: красное, черное, четное, нечетное\n"
        f"   Пример: рул 500 красное\n\n"
        f"{get_emoji('rocket')} <b>Краш</b> - краш [сумма] [множитель]\n"
        f"   Пример: краш 100 2.5\n\n"
        f"{get_emoji('dice')} <b>Кости</b> - кости [сумма] [м|б|равно]\n"
        f"   Пример: кости 500 б\n\n"
        f"{get_emoji('tower')} <b>Башня</b> - башня [сумма]\n"
        f"   Пример: башня 500\n\n"
        f"{get_emoji('gold')} <b>Золото</b> - золото [сумма]\n"
        f"   Пример: золото 500\n\n"
        f"{get_emoji('mine')} <b>Мины</b> - мины [сумма] [мин]\n"
        f"   Пример: мины 500 3\n\n"
        f"{get_emoji('diamond')} <b>Алмазы</b> - алмазы [сумма] [мин]\n"
        f"   Пример: алмазы 500 1\n\n"
        f"{get_emoji('chest')} <b>Сундуки</b> - сундуки [сумма]\n"
        f"   Пример: сундуки 500\n\n"
        f"{get_emoji('duel')} <b>Дуэль</b> - дуэль [сумма]\n"
        f"   Пример: дуэль 500\n\n"
        f"{get_emoji('money')} <b>Баланс</b> - б или баланс\n"
        f"{get_emoji('bonus')} <b>Бонус</b> - бонус",
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
