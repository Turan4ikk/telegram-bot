import asyncio
import logging
import re
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.types import ChatPermissions, BotCommand
from aiogram.filters import Command

# ============ ТВОИ ДАННЫЕ ============
TOKEN = "8623221406:AAF42kKkHeHWABjs0eUBAdhs1rlZ6EBQgCg"
OWNER_ID = 7262038816
WARN_LIMIT = 3

# ============ СИСТЕМА РОЛЕЙ ============
user_roles = {}
ADMIN_IDS = [7262038816]

# ============ ИНИЦИАЛИЗАЦИЯ ============
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()
user_warns = {}

# ============ ТЕКСТЫ ============

HELP_TEXT = """
🤖 МОЙ ФУНКЦИОНАЛ

📌 /start — это сообщение
📋 /rules — правила клуба
⏰ /remind [время] [текст] — напоминание

🔇 /mute [время] [причина] — замутить (ответь на сообщение)
🔊 /unmute — размутить (ответь на сообщение)
🚫 /ban [причина] — забанить (ответь на сообщение)
⚠️ /warn [причина] — предупреждение (ответь на сообщение)
📊 /warns [@user] — проверка предупреждений

👑 /setadmin [@user] — назначить админом (ответь на сообщение)
👮 /setmoder [@user] — назначить модератором (ответь на сообщение)
❌ /removerole [@user] — снять роль (ответь на сообщение)
📊 /roles — список ролей

✅ КАК ИСПОЛЬЗОВАТЬ:
1️⃣ Найдите сообщение пользователя
2️⃣ Нажмите "Ответить" на него
3️⃣ Напишите команду

Примеры:
/mute 5m Спам
/ban Оскорбление
/warn Нарушение правил
/setadmin

👑 Владелец: @L_U_N_A_T_I_KK
👮‍♂️ Модератор: @aivtu
🛡 Администраторы: @jigglytits
📰 Главный по новостям: Богдан
🎆Ивент-контролер: @Devid_L
💻Ивент-менеджер:@Nonamych
"""

RULES_TEXT = """
1. Запрещено использование автокликеров и модов дающих различные преимущества (БСД и прочие). 
Нарушение влечёт за собой исключение из клуба.

2. Клуб ориентирован на командную игру и активное общение. 
Участникам крайне желательно поддерживать активность и взаимодействовать с другими членами клуба. 
При распределении мест приоритет всегда остаётся за теми, кто играет в команде и участвует в жизни клуба.

3. В клуб принимаются преимущественно соло-игроки.
Групповые заявки и приём по рекомендации друзей не рассматриваются. 
Приоритет отдаётся игрокам, готовым к общению и совместной игре со всеми членами клуба.

4. Обсуждение политики в клубе запрещено.

5. Отсутствие в сети 3 дня и более без предупреждения — исключение из клуба без дополнительных предупреждений.

6. Неотыгранные билеты в копилке без предупреждения даже если она заполнена — исключение из клуба без дополнительных предупреждений.

‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾

В клубе проводятся розыгрыши Brawl Pass. 
Розыгрыши организуются ежемесячно во время копилки, а также приурочиваются к специальным мероприятиям.
Подробная информация об условиях участия публикуется заблаговременно до начала.
Проведение конкурса и его результаты публикуются здесь — @placelin

Discord сервер клуба - https://discord.gg/R2PzrhVdZc

👑 Владелец: @L_U_N_A_T_I_KK
🛡 Администратор: @jigglytits
👮‍♂️ Модератор: @aivtu
📰 Главный по новостям:Богдан
🎆Ивент-контролер: @Devid_L
💻Ивент-менеджер:@Nonamych
"""

GREETING_TEXT = """
Приветствую, {name}!

Правила клуба — /rules
"""

ROLE_INFO_TEXT = """
📊 ИНФОРМАЦИЯ О РОЛЯХ

👑 Владелец: @L_U_N_A_T_I_KK
👮‍♂️ Модератор: @aivtu
🛡 Администраторы: @jigglytits
📰 Главный по новостям: Богдан
🎆Ивент-контролер: @Devid_L
💻Ивент-менеджер:@Nonamych

Права:
👑 Владелец — всё
🛡 Админ — всё, кроме назначения ролей
👮 Модератор — мут, размут, варн, но НЕ бан
"""

MUTE_TEXT = """
🔇 ЗАМУЧЕН

👤 {user}
⏱ {duration}
📝 {reason}
"""

UNMUTE_TEXT = """
🔊 РАЗМУЧЕН

👤 {user}
"""

BAN_TEXT = """
🚫 ЗАБАНЕН

👤 {user}
📝 {reason}
"""

UNBAN_TEXT = """
✅ РАЗБАНЕН

👤 {user}
"""

WARN_TEXT = """
⚠️ ПРЕДУПРЕЖДЕНИЕ

👤 {user}
📝 {reason}
📊 {warns}/{limit}

При {limit} нарушениях → МУТ 1 ЧАС
"""

MUTE_CONFLICT_TEXT = """
🔇 МУТ ЗА КОНФЛИКТ

👤 {user}
⏱ 1 час
📝 Повторное нарушение (конфликт/оск)

⚠️ Следующее нарушение → БАН
"""

AUTO_MUTE_TEXT = """
🔇 АВТОМАТИЧЕСКИЙ МУТ НА 1 ЧАС

👤 {user}
📊 Причина: превышение лимита предупреждений ({limit})

⚠️ Следующее нарушение → БАН
"""

WARNS_TEXT = """
📊 ПРЕДУПРЕЖДЕНИЯ

👤 {user}
📊 {warns}/{limit}
{status}
"""

REMIND_TEXT = """
⏰ НАПОМИНАНИЕ

📝 {text}
⏱ Через {duration}
"""

REMIND_ALERT = """
🔔 НАПОМИНАНИЕ!

📝 {text}
"""

NO_PERMISSION = """
⛔ Доступ запрещён

У вас нет прав для этой команды.
"""

WRONG_FORMAT = """
❌ Неверный формат

{example}
"""

USER_NOT_FOUND = """
❌ Пользователь не найден

✅ Ответьте на сообщение пользователя!
"""

ROLE_SET = """
✅ РОЛЬ НАЗНАЧЕНА

👤 {user}
👑 Роль: {role}
"""

ROLE_REMOVED = """
❌ РОЛЬ СНЯТА

👤 {user}
"""

# ============ ФУНКЦИИ ПРОВЕРКИ РОЛЕЙ ============

def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS or is_owner(user_id)

def is_moder(user_id: int) -> bool:
    return user_roles.get(user_id) == 'moder' or is_admin(user_id)

# ============ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ============

def parse_time(time_str: str) -> int:
    pattern = r'(\d+)([mhd])'
    match = re.match(pattern, time_str)
    if not match:
        return 0
    value = int(match.group(1))
    unit = match.group(2)
    if unit == 'm':
        return value * 60
    elif unit == 'h':
        return value * 3600
    elif unit == 'd':
        return value * 86400
    return 0

def format_duration(seconds: int) -> str:
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    parts = []
    if days: parts.append(f"{days}д")
    if hours: parts.append(f"{hours}ч")
    if minutes: parts.append(f"{minutes}м")
    return " ".join(parts) if parts else "0м"

async def send_message(message: types.Message, text: str):
    await message.answer(text)

# ============ ГЛАВНАЯ ФУНКЦИЯ ПОИСКА ПОЛЬЗОВАТЕЛЯ ============

async def get_target_user(message: types.Message):
    """
    Ищет пользователя:
    1. Из реплая (ответа на сообщение)
    2. По @username в тексте команды
    3. По ID в тексте команды
    """
    print(f"🔍 Поиск пользователя в команде: {message.text}")
    
    # СПОСОБ 1: Если есть реплай - берем оттуда (САМЫЙ НАДЕЖНЫЙ)
    if message.reply_to_message:
        user = message.reply_to_message.from_user
        print(f"✅ Найден через реплай: {user.id} ({user.first_name})")
        return user
    
    # СПОСОБ 2: Парсим аргументы команды
    args = message.text.split()
    if len(args) > 1:
        target = args[1].strip()
        
        # Если это @username
        if target.startswith('@'):
            username = target.replace('@', '').lower()
            print(f"🔍 Ищем по username: @{username}")
            
            # Пробуем найти через get_chat
            try:
                chat = await bot.get_chat(f"@{username}")
                # Проверяем, есть ли в чате
                try:
                    member = await bot.get_chat_member(message.chat.id, chat.id)
                    if member:
                        print(f"✅ Найден через get_chat: {chat.id} ({member.user.first_name})")
                        return member.user
                except:
                    pass
            except:
                pass
            
            # Пробуем найти среди администраторов
            try:
                admins = await bot.get_chat_administrators(message.chat.id)
                for admin in admins:
                    if admin.user.username and admin.user.username.lower() == username:
                        print(f"✅ Найден среди админов: {admin.user.id} ({admin.user.first_name})")
                        return admin.user
            except:
                pass
            
            # Пробуем найти среди всех участников (через get_chat_members)
            try:
                async for member in bot.get_chat_members(message.chat.id):
                    if member.user.username and member.user.username.lower() == username:
                        print(f"✅ Найден среди участников: {member.user.id} ({member.user.first_name})")
                        return member.user
            except:
                pass
        
        # Если это ID (цифры)
        elif target.isdigit():
            user_id = int(target)
            try:
                member = await bot.get_chat_member(message.chat.id, user_id)
                if member:
                    print(f"✅ Найден по ID: {user_id} ({member.user.first_name})")
                    return member.user
            except:
                pass
    
    print("❌ Пользователь не найден")
    return None

# ============ КОМАНДЫ ============

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await send_message(message, HELP_TEXT)

@dp.message(Command("rules"))
@dp.message(Command("p"))
async def cmd_rules(message: types.Message):
    await send_message(message, RULES_TEXT)

@dp.message(Command("remind"))
async def cmd_remind(message: types.Message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await send_message(message, WRONG_FORMAT.format(
            example="/remind 10m Позвонить маме"
        ))
        return
    
    time_str = args[1]
    reminder_text = args[2]
    
    seconds = parse_time(time_str)
    if seconds == 0:
        await send_message(message, "❌ Используйте: 10m, 1h, 2d")
        return
    
    duration = format_duration(seconds)
    text = REMIND_TEXT.format(text=reminder_text, duration=duration)
    await send_message(message, text)
    
    asyncio.create_task(send_reminder_after_delay(message, reminder_text, seconds))

async def send_reminder_after_delay(message: types.Message, text: str, delay: int):
    await asyncio.sleep(delay)
    alert = REMIND_ALERT.format(text=text)
    await send_message(message, alert)

# ============ КОМАНДЫ ДЛЯ РОЛЕЙ ============

@dp.message(Command("setadmin"))
async def cmd_set_admin(message: types.Message):
    if not is_owner(message.from_user.id):
        await send_message(message, "❌ Только владелец может назначать администраторов!")
        return
    
    if message.chat.type == "private":
        await send_message(message, "❌ Работает только в группах!")
        return
    
    user = await get_target_user(message)
    if not user:
        await send_message(message, USER_NOT_FOUND)
        return
    
    if user.id == OWNER_ID:
        await send_message(message, "❌ Это владелец!")
        return
    
    if user.id not in ADMIN_IDS:
        ADMIN_IDS.append(user.id)
    
    user_roles.pop(user.id, None)
    
    text = ROLE_SET.format(user=user.first_name, role="Администратор 🛡")
    await send_message(message, text)

@dp.message(Command("setmoder"))
async def cmd_set_moder(message: types.Message):
    if not is_owner(message.from_user.id):
        await send_message(message, "❌ Только владелец может назначать модераторов!")
        return
    
    if message.chat.type == "private":
        await send_message(message, "❌ Работает только в группах!")
        return
    
    user = await get_target_user(message)
    if not user:
        await send_message(message, USER_NOT_FOUND)
        return
    
    if user.id == OWNER_ID:
        await send_message(message, "❌ Это владелец!")
        return
    
    if is_admin(user.id):
        await send_message(message, "❌ Этот пользователь уже администратор!")
        return
    
    user_roles[user.id] = 'moder'
    
    text = ROLE_SET.format(user=user.first_name, role="Модератор 👮")
    await send_message(message, text)

@dp.message(Command("removerole"))
async def cmd_remove_role(message: types.Message):
    if not is_owner(message.from_user.id):
        await send_message(message, "❌ Только владелец может снимать роли!")
        return
    
    if message.chat.type == "private":
        await send_message(message, "❌ Работает только в группах!")
        return
    
    user = await get_target_user(message)
    if not user:
        await send_message(message, USER_NOT_FOUND)
        return
    
    if user.id == OWNER_ID:
        await send_message(message, "❌ Нельзя снять роль с владельца!")
        return
    
    if user.id in ADMIN_IDS:
        ADMIN_IDS.remove(user.id)
    
    user_roles.pop(user.id, None)
    
    text = ROLE_REMOVED.format(user=user.first_name)
    await send_message(message, text)

@dp.message(Command("roles"))
async def cmd_roles(message: types.Message):
    if not is_admin(message.from_user.id):
        await send_message(message, NO_PERMISSION)
        return
    
    admin_names = []
    for admin_id in ADMIN_IDS:
        if admin_id == OWNER_ID:
            continue
        try:
            user = await bot.get_chat(admin_id)
            admin_names.append(user.first_name)
        except:
            admin_names.append(f"ID:{admin_id}")
    
    moder_names = []
    for user_id, role in user_roles.items():
        if role == 'moder':
            try:
                user = await bot.get_chat(user_id)
                moder_names.append(user.first_name)
            except:
                moder_names.append(f"ID:{user_id}")
    
    text = ROLE_INFO_TEXT.format(
        admins=", ".join(admin_names) if admin_names else "Нет",
        moders=", ".join(moder_names) if moder_names else "Нет"
    )
    await send_message(message, text)

# ============ КОМАНДЫ МОДЕРАЦИИ ============

@dp.message(Command("mute"))
async def cmd_mute(message: types.Message):
    if not is_moder(message.from_user.id):
        await send_message(message, NO_PERMISSION)
        return
    
    if message.chat.type == "private":
        await send_message(message, "❌ Работает только в группах!")
        return
    
    if not message.reply_to_message:
        await send_message(message, "❌ Ответьте на сообщение пользователя!")
        return
    
    target_user = message.reply_to_message.from_user
    user_id = target_user.id
    
    args = message.text.split(maxsplit=2)
    if len(args) < 2:
        await send_message(message, WRONG_FORMAT.format(
            example="/mute 5m Спам"
        ))
        return
    
    time_str = args[1]
    reason = args[2] if len(args) > 2 else "Без причины"
    
    seconds = parse_time(time_str)
    if seconds == 0:
        await send_message(message, "❌ Используйте: 10m, 1h, 2d")
        return
    
    until_date = datetime.now() + timedelta(seconds=seconds)
    
    try:
        await bot.restrict_chat_member(
            message.chat.id,
            user_id,
            ChatPermissions(can_send_messages=False),
            until_date=until_date
        )
        duration = format_duration(seconds)
        text = MUTE_TEXT.format(
            user=target_user.first_name,
            duration=duration,
            reason=reason
        )
        await send_message(message, text)
    except Exception as e:
        await send_message(message, f"❌ Ошибка: {e}")

@dp.message(Command("unmute"))
async def cmd_unmute(message: types.Message):
    if not is_moder(message.from_user.id):
        await send_message(message, NO_PERMISSION)
        return
    
    if message.chat.type == "private":
        await send_message(message, "❌ Работает только в группах!")
        return
    
    if not message.reply_to_message:
        await send_message(message, "❌ Ответьте на сообщение пользователя!")
        return
    
    target_user = message.reply_to_message.from_user
    user_id = target_user.id
    
    try:
        await bot.restrict_chat_member(
            message.chat.id,
            user_id,
            ChatPermissions(
                can_send_messages=True,
                can_send_media=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        text = UNMUTE_TEXT.format(user=target_user.first_name)
        await send_message(message, text)
    except Exception as e:
        await send_message(message, f"❌ Ошибка: {e}")

@dp.message(Command("ban"))
async def cmd_ban(message: types.Message):
    if not is_admin(message.from_user.id):
        await send_message(message, "❌ Только администраторы могут банить!")
        return
    
    if message.chat.type == "private":
        await send_message(message, "❌ Работает только в группах!")
        return
    
    if not message.reply_to_message:
        await send_message(message, "❌ Ответьте на сообщение пользователя!")
        return
    
    target_user = message.reply_to_message.from_user
    user_id = target_user.id
    
    args = message.text.split(maxsplit=1)
    reason = args[1] if len(args) > 1 else "Без причины"
    
    try:
        await bot.ban_chat_member(message.chat.id, user_id)
        text = BAN_TEXT.format(user=target_user.first_name, reason=reason)
        await send_message(message, text)
    except Exception as e:
        await send_message(message, f"❌ Ошибка: {e}")

@dp.message(Command("unban"))
async def cmd_unban(message: types.Message):
    if not is_admin(message.from_user.id):
        await send_message(message, "❌ Только администраторы могут разбанивать!")
        return
    
    if message.chat.type == "private":
        await send_message(message, "❌ Работает только в группах!")
        return
    
    if not message.reply_to_message:
        await send_message(message, "❌ Ответьте на сообщение пользователя!")
        return
    
    target_user = message.reply_to_message.from_user
    user_id = target_user.id
    
    try:
        await bot.unban_chat_member(message.chat.id, user_id)
        text = UNBAN_TEXT.format(user=target_user.first_name)
        await send_message(message, text)
    except Exception as e:
        await send_message(message, f"❌ Ошибка: {e}")

@dp.message(Command("warn"))
async def cmd_warn(message: types.Message):
    if not is_moder(message.from_user.id):
        await send_message(message, NO_PERMISSION)
        return
    
    if message.chat.type == "private":
        await send_message(message, "❌ Работает только в группах!")
        return
    
    if not message.reply_to_message:
        await send_message(message, "❌ Ответьте на сообщение пользователя!")
        return
    
    target_user = message.reply_to_message.from_user
    user_id = target_user.id
    
    args = message.text.split(maxsplit=1)
    reason = args[1] if len(args) > 1 else "Без причины"
    
    if user_id not in user_warns:
        user_warns[user_id] = 0
    user_warns[user_id] += 1
    warns_count = user_warns[user_id]
    
    is_conflict = any(word in reason.lower() for word in ['конфликт', 'оск', 'оскорбление'])
    
    text = WARN_TEXT.format(
        user=target_user.first_name,
        reason=reason,
        warns=warns_count,
        limit=WARN_LIMIT
    )
    await send_message(message, text)
    
    if warns_count >= WARN_LIMIT:
        until_date = datetime.now() + timedelta(hours=1)
        try:
            await bot.restrict_chat_member(
                message.chat.id,
                user_id,
                ChatPermissions(can_send_messages=False),
                until_date=until_date
            )
            if is_conflict:
                await send_message(message, MUTE_CONFLICT_TEXT.format(user=target_user.first_name))
            else:
                await send_message(message, AUTO_MUTE_TEXT.format(
                    user=target_user.first_name,
                    limit=WARN_LIMIT
                ))
        except Exception as e:
            await send_message(message, f"❌ Ошибка при муте: {e}")

@dp.message(Command("warns"))
async def cmd_warns(message: types.Message):
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        user_id = message.from_user.id
        user_name = message.from_user.first_name
    else:
        user = await get_target_user(message)
        if not user:
            await send_message(message, USER_NOT_FOUND)
            return
        user_id = user.id
        user_name = user.first_name
    
    warns = user_warns.get(user_id, 0)
    
    if warns >= WARN_LIMIT:
        status = "🔇 Мут на 1 час (лимит превышен)"
    else:
        remaining = WARN_LIMIT - warns
        status = f"⚠️ Осталось {remaining} предупреждений до мута"
    
    text = WARNS_TEXT.format(
        user=user_name,
        warns=warns,
        limit=WARN_LIMIT,
        status=status
    )
    await send_message(message, text)

@dp.message()
async def greeting(message: types.Message):
    if message.new_chat_members:
        for member in message.new_chat_members:
            if not member.is_bot:
                await send_message(message, GREETING_TEXT.format(name=member.first_name))

# ============ ЗАПУСК ============

async def set_commands():
    commands = [
        BotCommand(command="/start", description="Главное меню"),
        BotCommand(command="/rules", description="Правила"),
        BotCommand(command="/p", description="Правила"),
        BotCommand(command="/remind", description="Напоминание"),
        BotCommand(command="/mute", description="Замутить"),
        BotCommand(command="/unmute", description="Размутить"),
        BotCommand(command="/ban", description="Забанить"),
        BotCommand(command="/unban", description="Разбанить"),
        BotCommand(command="/warn", description="Предупреждение"),
        BotCommand(command="/warns", description="Проверить предупреждения"),
        BotCommand(command="/setadmin", description="Назначить админа"),
        BotCommand(command="/setmoder", description="Назначить модератора"),
        BotCommand(command="/removerole", description="Снять роль"),
        BotCommand(command="/roles", description="Список ролей"),
    ]
    await bot.set_my_commands(commands)

async def main():
    print("🚀 БОТ ЗАПУЩЕН")
    print("👑 Владелец: @L_U_N_A_T_I_KK")
    print("👮 Модератор: @aivtu")
    print("🛡 Администраторы: @jigglytits")
    print("✅ Бот готов к работе!")
    await set_commands()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
