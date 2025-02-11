import discord
from discord.ext import commands
import random
from discord import app_commands
import asyncio
import os
from dotenv import load_dotenv
import datetime
import json
from typing import Optional

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Отладочный вывод
print("=== Диагностика токена ===")
print(f"Токен получен: {'Да' if TOKEN else 'Нет'}")
print(f"Длина токена: {len(TOKEN) if TOKEN else 0}")
print(f"Токен содержит пробелы: {'Да' if ' ' in TOKEN else 'Нет'}")
print("========================")

# Проверка и очистка токена
if TOKEN:
    TOKEN = TOKEN.strip()  # Удаляем лишние пробелы
    
if not TOKEN:
    raise ValueError("Токен бота не найден в переменных окружения!")

# Создаем экземпляр бота с префиксом команд '!'
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Словарь с триггерами и ответами
triggers = {
    'привет': ['Привет!', 'Здравствуй!', 'Приветствую!'],
    'как дела': ['Отлично!', 'Все супер!', 'Лучше всех!'],
    'пока': ['До свидания!', 'Пока!', 'Увидимся!']
}

# Добавляем словарь для хранения состояния игр виселицы
hangman_games = {}

# Система уровней
levels = {}

# Система экономики
economy = {}

# Система тегов (заметок)
tags = {}

# Сохранение данных
def save_data():
    with open('data.json', 'w') as f:
        json.dump({
            'economy': economy,
            'levels': levels,
            'tags': tags
        }, f)

# Загрузка данных
try:
    with open('data.json', 'r') as f:
        data = json.load(f)
        economy = data.get('economy', {})
        levels = data.get('levels', {})
        tags = data.get('tags', {})
except FileNotFoundError:
    pass

# Автосохранение каждые 5 минут
async def auto_save():
    while True:
        await asyncio.sleep(300)  # 5 минут
        save_data()
        print("Данные автоматически сохранены")

if not TOKEN:
    raise ValueError("Токен бота не найден в переменных окружения!")

@bot.tree.command(name="привет", description="Поприветствовать бота")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Привет, {interaction.user.name}! 👋")

@bot.event
async def on_ready():
    # Устанавливаем статус и активность бота
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game('/помощь для справки')
    )
    try:
        # Синхронизируем команды глобально
        commands = await bot.tree.sync()
        print(f"Синхронизировано {len(commands)} глобальных слэш-команд:")
        for cmd in commands:
            print(f"- /{cmd.name}")
    except Exception as e:
        print(f"Ошибка синхронизации команд: {e}")
    print(f'Бот {bot.user} успешно запущен!')
    bot.loop.create_task(auto_save())

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if not message.author.bot:
        # Проверяем сообщение на триггеры
        for trigger, responses in triggers.items():
            if trigger in message.content.lower():
                await message.channel.send(random.choice(responses))
        
        # Простая система уровней
        author_id = str(message.author.id)
        if author_id not in levels:
            levels[author_id] = {"level": 0, "xp": 0}
        levels[author_id]["xp"] += random.randint(1, 5)
        
        # Проверяем повышение уровня
        xp_needed = (levels[author_id]["level"] + 1) * 100
        
        if levels[author_id]["xp"] >= xp_needed:
            levels[author_id]["level"] += 1
            levels[author_id]["xp"] = 0
            
            # Награда за уровень
            reward = levels[author_id]["level"] * 50
            if author_id not in economy:
                economy[author_id] = 0
            economy[author_id] += reward
            
            embed = discord.Embed(
                title="🎉 Новый уровень!",
                description=(
                    f"{message.author.mention} достиг уровня {levels[author_id]['level']}!\n"
                    f"Награда: {reward} монет"
                ),
                color=discord.Color.blue()
            )
            await message.channel.send(embed=embed)
    
    await bot.process_commands(message)

@bot.command(name='помощь')
async def help_command(ctx):
    embed = discord.Embed(
        title='🤖 Помощь по командам бота',
        description='Список доступных команд и триггеров',
        color=discord.Color.blue()
    )
    
    commands_text = (
        "/привет - поприветствовать бота\n"
        "/инфо - информация о боте\n"
        "/пинг - проверить задержку бота\n"
        "/очистить [количество] - очистить сообщения\n"
        "/монетка - подбросить монетку\n"
        "/кости [количество] - бросить кости\n"
        "/угадай_число [число] - угадать число от 1 до 100\n"
        "/виселица [буква] - сыграть в виселицу"
    )
    
    embed.add_field(
        name='Слэш-команды',
        value=commands_text,
        inline=False
    )
    
    trigger_list = ', '.join(triggers.keys())
    embed.add_field(
        name='Триггеры',
        value=f'Бот реагирует на следующие слова: {trigger_list}',
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.tree.command(name="инфо", description="Информация о боте")
async def info_slash(interaction: discord.Interaction):
    embed = discord.Embed(
        title='Информация о боте',
        description='Многофункциональный бот с системами модерации, экономики и развлечений!',
        color=discord.Color.green()
    )
    
    embed.add_field(
        name='Разработчик',
        value='[yomo4](https://github.com/yomo4)',
        inline=True
    )
    
    embed.add_field(
        name='Версия',
        value='1.0',
        inline=True
    )
    
    embed.add_field(
        name='GitHub',
        value='[Исходный код](https://github.com/yomo4/discord-bot-by-yomo4)',
        inline=True
    )
    
    embed.set_footer(text='Создано с ❤️ by @yomo4')
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="пинг", description="Проверить задержку бота")
async def ping_slash(interaction: discord.Interaction):
    await interaction.response.send_message(
        f'🏓 Понг! Задержка: {round(bot.latency * 1000)}мс'
    )

@bot.tree.command(
    name="очистить",
    description="Очистить указанное количество сообщений"
)
@app_commands.describe(amount="Количество сообщений для удаления")
async def clear(interaction: discord.Interaction, amount: int):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("У вас нет прав на использование этой команды!", ephemeral=True)
        return
    
    await interaction.response.defer()
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"✨ Удалено {len(deleted)} сообщений!", ephemeral=True)

@bot.tree.command(name="камень_ножницы_бумага", description="Сыграть в камень, ножницы, бумага")
@app_commands.describe(выбор="Выберите: камень, ножницы или бумага")
@app_commands.choices(выбор=[
    app_commands.Choice(name="камень", value="камень"),
    app_commands.Choice(name="ножницы", value="ножницы"),
    app_commands.Choice(name="бумага", value="бумага")
])
async def rps(interaction: discord.Interaction, выбор: str):
    choices = ["камень", "ножницы", "бумага"]
    bot_choice = random.choice(choices)
    
    # Определяем победителя
    if выбор == bot_choice:
        result = "Ничья! 🤝"
    elif (выбор == "камень" and bot_choice == "ножницы") or \
         (выбор == "ножницы" and bot_choice == "бумага") or \
         (выбор == "бумага" and bot_choice == "камень"):
        result = "Вы победили! 🎉"
    else:
        result = "Бот победил! 🤖"
    
    await interaction.response.send_message(
        f"Вы выбрали: {выбор}\nБот выбрал: {bot_choice}\n{result}"
    )

@bot.tree.command(name="угадай_число", description="Угадай число от 1 до 100")
@app_commands.describe(число="Введите число от 1 до 100")
async def guess_number(interaction: discord.Interaction, число: int):
    if число < 1 or число > 100:
        await interaction.response.send_message("Число должно быть от 1 до 100!", ephemeral=True)
        return
        
    number = random.randint(1, 100)
    
    if число == number:
        await interaction.response.send_message(f"🎉 Поздравляю! Вы угадали число {number}!")
    elif число < number:
        await interaction.response.send_message(f"Загаданное число больше чем {число}! Попробуйте еще раз.")
    else:
        await interaction.response.send_message(f"Загаданное число меньше чем {число}! Попробуйте еще раз.")

@bot.tree.command(name="виселица", description="Сыграть в виселицу")
@app_commands.describe(буква="Введите одну букву")
async def hangman(interaction: discord.Interaction, буква: str):
    if len(буква) != 1:
        await interaction.response.send_message("Пожалуйста, введите только одну букву!", ephemeral=True)
        return
        
    user_id = interaction.user.id
    
    # Если у пользователя нет активной игры, создаем новую
    if user_id not in hangman_games:
        words = ["питон", "программирование", "дискорд", "разработка", "компьютер", "алгоритм"]
        hangman_games[user_id] = {
            "word": random.choice(words),
            "guessed": set(),
            "attempts": 6
        }
    
    game = hangman_games[user_id]
    буква = буква.lower()
    
    if буква in game["guessed"]:
        await interaction.response.send_message("Вы уже называли эту букву!", ephemeral=True)
        return
    
    game["guessed"].add(буква)
    
    if буква not in game["word"]:
        game["attempts"] -= 1
    
    # Формируем текущее состояние слова
    current_word = "".join(letter if letter in game["guessed"] else "_" for letter in game["word"])
    
    # Проверяем победу или поражение
    if "_" not in current_word:
        del hangman_games[user_id]
        await interaction.response.send_message(f"🎉 Поздравляем! Вы угадали слово: {game['word']}")
        return
    
    if game["attempts"] == 0:
        del hangman_games[user_id]
        await interaction.response.send_message(f"❌ Игра окончена! Слово было: {game['word']}")
        return
    
    await interaction.response.send_message(
        f"Слово: {current_word}\n"
        f"Попыток осталось: {game['attempts']}\n"
        f"Использованные буквы: {', '.join(sorted(game['guessed']))}"
    )

@bot.tree.command(name="монетка", description="Подбросить монетку")
async def flip_coin(interaction: discord.Interaction):
    result = random.choice(["Орёл", "Решка"])
    await interaction.response.send_message(f"🪙 {result}!")

@bot.tree.command(name="кости", description="Бросить кости")
@app_commands.describe(количество="Количество костей (1-5)")
async def roll_dice(interaction: discord.Interaction, количество: int = 1):
    if количество < 1 or количество > 5:
        await interaction.response.send_message("Можно бросить от 1 до 5 костей!", ephemeral=True)
        return
        
    results = [random.randint(1, 6) for _ in range(количество)]
    dice_emojis = {
        1: "⚀", 2: "⚁", 3: "⚂",
        4: "⚃", 5: "⚄", 6: "⚅"
    }
    
    result_str = " ".join(dice_emojis[num] for num in results)
    total = sum(results)
    
    await interaction.response.send_message(f"🎲 Результат: {result_str}\nСумма: {total}")

# Изменим обработчик ошибок
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"Пожалуйста, подождите {error.retry_after:.2f} секунд перед повторным использованием команды.",
            ephemeral=True
        )
    elif isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "У вас недостаточно прав для использования этой команды.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "Произошла ошибка при выполнении команды. Администраторы уведомлены.",
            ephemeral=True
        )
        # Логируем ошибку, но не показываем детали пользователям
        print(f"Ошибка в команде {interaction.command.name}: {str(error)}")

@bot.tree.command(name="настроить_сервер", description="Настроить сервер автоматически")
@app_commands.default_permissions(administrator=True)
async def setup_server(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message("Эта команда работает только на сервере!", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    
    try:
        # Удаляем существующие каналы
        for channel in interaction.guild.channels:
            try:
                await channel.delete()
                await asyncio.sleep(1)
            except:
                continue

        # Создаем категории и каналы
        categories = {
            "NON": [
                ("no-replay", "text")
            ],
            "TEXT CHAT": [
                ("public-chat", "text"),
                ("flood", "text"),
                ("dota-2-id", "text"),
                ("🎵-bot-music-🎵", "text"),
                ("игры", "text")
            ],
            "VOICE CHANNEL": [
                ("общий", "voice", 0)
            ],
            "DOTA 2 / COMMUNICATION": [
                ("tavern lounge", "voice", 10),
                ("turbo / ranking", "voice", 5),
                ("250$ room", "voice", 0)
            ],
            "DOTA 2 / WORKING": [
                ("olx", "text"),
                ("chat", "text"),
                ("secret room", "voice", 5),
                ("700$ room", "voice", 0)
            ],
            "AFK": [
                ("afk", "voice", 0)
            ]
        }

        # Создаем роли
        roles_data = {
            "Admin": discord.Color.red(),
            "Moderator": discord.Color.blue(),
            "Member": discord.Color.green()
        }

        created_roles = {}
        for role_name, color in roles_data.items():
            role = await interaction.guild.create_role(
                name=role_name,
                color=color,
                hoist=True,
                mentionable=True
            )
            created_roles[role_name] = role
            await asyncio.sleep(1)

        # Создаем категории и каналы
        for category_name, channels in categories.items():
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel=True),
                created_roles["Admin"]: discord.PermissionOverwrite(administrator=True),
                created_roles["Moderator"]: discord.PermissionOverwrite(
                    manage_messages=True,
                    mute_members=True,
                    move_members=True
                )
            }

            category = await interaction.guild.create_category(category_name, overwrites=overwrites)
            
            for channel_data in channels:
                if len(channel_data) == 2:  # Текстовый канал
                    name, type = channel_data
                    if type == "text":
                        await interaction.guild.create_text_channel(name, category=category)
                else:  # Голосовой канал
                    name, type, limit = channel_data
                    if type == "voice":
                        await interaction.guild.create_voice_channel(
                            name, 
                            category=category,
                            user_limit=limit
                        )
                await asyncio.sleep(1)

        await interaction.followup.send("✅ Сервер успешно настроен!", ephemeral=True)

    except Exception as e:
        await interaction.followup.send(
            f"❌ Произошла ошибка при настройке сервера: {str(e)}\n"
            "Убедитесь, что у бота есть права администратора.",
            ephemeral=True
        )

@bot.tree.command(name="очистить_сервер", description="Удалить все каналы")
@app_commands.default_permissions(administrator=True)
async def clear_server(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message("Эта команда работает только на сервере!", ephemeral=True)
        return

    await interaction.response.send_message("🗑️ Удаляю каналы...", ephemeral=True)
    
    try:
        for channel in interaction.guild.channels:
            await channel.delete()
        await interaction.edit_original_response(content="✅ Все каналы удалены!")
    except Exception as e:
        await interaction.edit_original_response(
            content=f"❌ Ошибка: {str(e)}\nУбедитесь, что у бота есть права администратора."
        )

@bot.tree.command(name="создать_навигацию", description="Создать навигационное меню сервера")
@app_commands.default_permissions(administrator=True)
async def create_navigation(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message("Эта команда работает только на сервере!", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    try:
        # Находим канал навигации или создаем новый
        nav_channel = discord.utils.get(interaction.guild.text_channels, name="📋┃навигация")
        if not nav_channel:
            info_category = discord.utils.get(interaction.guild.categories, name="📌 ИНФОРМАЦИЯ")
            if not info_category:
                info_category = await interaction.guild.create_category("📌 ИНФОРМАЦИЯ", position=0)
            nav_channel = await interaction.guild.create_text_channel("📋┃навигация", category=info_category)

        # Создаем основное навигационное меню
        main_nav = discord.Embed(
            title="🗺️ Навигация по серверу",
            description="Добро пожаловать! Здесь вы найдете всю информацию о каналах сервера.",
            color=discord.Color.blue()
        )

        # Информационные каналы
        info_channels = (
            "**📌 ИНФОРМАЦИОННЫЕ КАНАЛЫ**\n"
            "📋┃навигация - карта сервера\n"
            "📢┃правила - правила сервера\n"
            "📣┃новости - важные объявления\n"
            "🎉┃события - мероприятия сервера\n"
        )
        main_nav.add_field(name="Информация", value=info_channels, inline=False)

        # Чат каналы
        chat_channels = (
            "**💭 ТЕКСТОВЫЕ КАНАЛЫ**\n"
            "💬┃общий-чат - основное общение\n"
            "🤖┃команды - команды бота\n"
            "🎮┃игры - игровые обсуждения\n"
            "🎵┃музыка - музыкальные боты\n"
            "😂┃мемы - развлекательный контент\n"
        )
        main_nav.add_field(name="Общение", value=chat_channels, inline=False)

        # Голосовые каналы
        voice_channels = (
            "**🔊 ГОЛОСОВЫЕ КАНАЛЫ**\n"
            "🎮┃Основной - общий голосовой\n"
            "🎲┃Игровой - для игр (5 мест)\n"
            "🎵┃Музыка - музыкальный (10 мест)\n"
            "🤝┃Переговорная - личное общение (2 места)\n"
        )
        main_nav.add_field(name="Голосовые каналы", value=voice_channels, inline=False)

        # Административные каналы
        admin_channels = (
            "**👮 АДМИН-КАНАЛЫ**\n"
            "📌┃админ-чат - чат администрации\n"
            "🚨┃модерация - модерационные действия\n"
            "📝┃логи - логи сервера\n"
        )
        main_nav.add_field(name="Администрация", value=admin_channels, inline=False)

        # Роли
        roles = (
            "**👑 РОЛИ СЕРВЕРА**\n"
            "👑 Владелец - создатель сервера\n"
            "⚡ Администратор - управление сервером\n"
            "🛡️ Модератор - модерация чатов\n"
            "🎭 VIP - особый статус\n"
            "👥 Участник - базовая роль\n"
        )
        main_nav.add_field(name="Роли", value=roles, inline=False)

        # Полезная информация
        info = (
            "**ℹ️ ПОЛЕЗНАЯ ИНФОРМАЦИЯ**\n"
            "• Используйте `/помощь` для просмотра команд бота\n"
            "• Обращайтесь к администрации по вопросам\n"
            "• Следите за обновлениями в канале новостей\n"
        )
        main_nav.add_field(name="Дополнительно", value=info, inline=False)

        main_nav.set_footer(text="Приятного общения на сервере! | Обновлено")

        # Очищаем канал навигации
        await nav_channel.purge()
        
        # Отправляем навигационное меню
        await nav_channel.send(embed=main_nav)

        # Создаем разделитель
        separator = discord.Embed(color=discord.Color.blue())
        separator.add_field(
            name="🔽 БЫСТРЫЕ ССЫЛКИ 🔽",
            value="Нажмите на название канала, чтобы перейти",
            inline=False
        )
        await nav_channel.send(embed=separator)

        # Создаем быстрые ссылки на основные каналы
        quick_links = ""
        for channel in interaction.guild.channels:
            if isinstance(channel, discord.TextChannel):
                if channel.name in ["📢┃правила", "📣┃новости", "💬┃общий-чат", "🤖┃команды"]:
                    quick_links += f"• {channel.mention}\n"

        links_embed = discord.Embed(
            title="📌 Основные каналы",
            description=quick_links,
            color=discord.Color.green()
        )
        await nav_channel.send(embed=links_embed)

        await interaction.followup.send("✅ Навигация успешно создана!", ephemeral=True)

    except Exception as e:
        await interaction.followup.send(
            f"❌ Ошибка при создании навигации: {str(e)}",
            ephemeral=True
        )

@bot.event
async def on_member_join(member):
    # Находим канал для приветствий
    welcome_channel = discord.utils.get(member.guild.text_channels, name="📣┃новости")
    if not welcome_channel:
        return

    try:
        # Создаем приветственное сообщение
        welcome_embed = discord.Embed(
            title=f"👋 Добро пожаловать на сервер, {member.name}!",
            description=f"Ты стал {len(member.guild.members)}-м участником нашего сервера!",
            color=discord.Color.green()
        )
        
        # Добавляем аватар пользователя
        welcome_embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        
        # Добавляем информацию о сервере
        welcome_embed.add_field(
            name="📌 Важная информация",
            value=(
                "• Прочитай <#" + str(discord.utils.get(member.guild.text_channels, name="📢┃правила").id) + ">\n"
                "• Используй </помощь:0> для просмотра команд\n"
                "• Общайся в <#" + str(discord.utils.get(member.guild.text_channels, name="💬┃общий-чат").id) + ">"
            ),
            inline=False
        )
        
        # Добавляем дату регистрации
        welcome_embed.add_field(
            name="📅 Дата регистрации",
            value=f"Аккаунт создан: {member.created_at.strftime('%d.%m.%Y')}"
        )
        
        welcome_embed.set_footer(text=f"ID: {member.id}")
        
        # Отправляем приветствие
        await welcome_channel.send(embed=welcome_embed)
        
        # Выдаем базовую роль
        default_role = discord.utils.get(member.guild.roles, name="👥 Участник")
        if default_role:
            await member.add_roles(default_role)
            
    except Exception as e:
        print(f"Ошибка при отправке приветствия: {e}")

@bot.event
async def on_member_remove(member):
    # Находим канал для уведомлений
    channel = discord.utils.get(member.guild.text_channels, name="📣┃новости")
    if not channel:
        return
        
    try:
        # Создаем сообщение о выходе
        leave_embed = discord.Embed(
            description=f"👋 **{member.name}** покинул сервер...",
            color=discord.Color.red()
        )
        leave_embed.set_footer(text=f"Участников: {len(member.guild.members)}")
        
        await channel.send(embed=leave_embed)
        
    except Exception as e:
        print(f"Ошибка при отправке уведомления о выходе: {e}")

@bot.tree.command(name="королевская_битва", description="Запустить королевскую битву")
@app_commands.default_permissions(administrator=True)
async def battle_royale(interaction: discord.Interaction):
    await interaction.response.defer()
    
    # Находим канал событий
    events_channel = discord.utils.get(interaction.guild.text_channels, name="🎉┃события")
    if not events_channel:
        await interaction.followup.send("Канал событий не найден!", ephemeral=True)
        return
    
    # Создаем эмбед с анонсом события
    announcement = discord.Embed(
        title="👑 КОРОЛЕВСКАЯ БИТВА 👑",
        description="Грандиозное событие! Сражайтесь за звание чемпиона и роль VIP!",
        color=discord.Color.gold()
    )
    
    announcement.add_field(
        name="📜 Правила",
        value=(
            "1. Нажмите на 🗡️ чтобы участвовать\n"
            "2. У вас есть 30 минут на регистрацию\n"
            "3. Победитель получает роль 🎭 VIP\n"
            "4. Минимум участников: 2"
        ),
        inline=False
    )
    
    announcement.add_field(
        name="⏰ Время",
        value="Регистрация: 30 минут\nНачало битвы после регистрации",
        inline=False
    )
    
    announcement.set_footer(text="Удачи всем участникам!")
    
    # Отправляем анонс и добавляем реакцию
    message = await events_channel.send(embed=announcement)
    await message.add_reaction("🗡️")
    
    # Ждем 30 минут для сбора участников
    await interaction.followup.send("Регистрация на битву началась! Продлится 30 минут.", ephemeral=True)
    await asyncio.sleep(1800)  # 30 минут
    
    # Собираем участников
    message = await events_channel.fetch_message(message.id)
    reaction = discord.utils.get(message.reactions, emoji="🗡️")
    
    if not reaction:
        await events_channel.send("❌ Ошибка при получении реакций!")
        return
    
    participants = []
    async for user in reaction.users():
        if not user.bot:
            participants.append(user)
    
    if len(participants) < 2:
        await events_channel.send("❌ Недостаточно участников для начала битвы! (минимум 2)")
        return
    
    # Начинаем битву
    battle_announcement = discord.Embed(
        title="⚔️ БИТВА НАЧАЛАСЬ ⚔️",
        description=f"Участвует {len(participants)} бойцов!",
        color=discord.Color.red()
    )
    await events_channel.send(embed=battle_announcement)
    
    # Симулируем битву
    while len(participants) > 1:
        await asyncio.sleep(3)  # Пауза между раундами
        
        # Выбираем случайных участников для поединка
        fighter1 = random.choice(participants)
        participants.remove(fighter1)
        fighter2 = random.choice(participants)
        participants.remove(fighter2)
        
        # Симулируем бой
        actions = [
            f"🗡️ {fighter1.name} наносит мощный удар по {fighter2.name}!",
            f"🛡️ {fighter2.name} блокирует атаку {fighter1.name}!",
            f"💫 {fighter1.name} использует специальный прием против {fighter2.name}!",
            f"⚔️ {fighter2.name} контратакует {fighter1.name}!"
        ]
        
        # Отправляем действия боя
        battle_log = await events_channel.send("\n".join(random.sample(actions, 2)))
        await asyncio.sleep(2)
        
        # Определяем победителя раунда
        winner = random.choice([fighter1, fighter2])
        loser = fighter2 if winner == fighter1 else fighter1
        
        await events_channel.send(f"**{winner.name}** побеждает в этом раунде! 🏆")
        participants.append(winner)
    
    # Объявляем победителя
    winner = participants[0]
    
    victory_embed = discord.Embed(
        title="👑 ЧЕМПИОН ОПРЕДЕЛЁН 👑",
        description=f"🎉 Победитель битвы: **{winner.name}**!",
        color=discord.Color.gold()
    )
    
    victory_embed.add_field(
        name="🎁 Награда",
        value="Роль 🎭 VIP и вечная слава!",
        inline=False
    )
    
    await events_channel.send(embed=victory_embed)
    
    # Выдаем награду
    try:
        vip_role = discord.utils.get(interaction.guild.roles, name="🎭 VIP")
        if vip_role:
            member = await interaction.guild.fetch_member(winner.id)
            await member.add_roles(vip_role)
            await events_channel.send(f"🎭 {winner.mention} получает роль VIP!")
    except Exception as e:
        await events_channel.send(f"❌ Ошибка при выдаче роли: {str(e)}")

@bot.tree.command(
    name="настроить_active_developer",
    description="Настроить сервер для получения значка Active Developer"
)
@app_commands.default_permissions(administrator=True)
async def setup_active_developer(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message("Эта команда работает только на сервере!", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    
    try:
        # Создаем категорию для системных каналов
        system_category = await interaction.guild.create_category("📱 SYSTEM")
        
        # Создаем канал для объявлений
        announcements_channel = await interaction.guild.create_text_channel(
            "developer-announcements",
            category=system_category,
            topic="Канал для объявлений Discord Developer",
            reason="Настройка для Active Developer Badge"
        )
        
        # Создаем канал для команд бота
        commands_channel = await interaction.guild.create_text_channel(
            "bot-commands",
            category=system_category,
            topic="Используйте команды бота здесь",
            reason="Настройка для Active Developer Badge"
        )
        
        # Отправляем приветственное сообщение
        embed = discord.Embed(
            title="🎉 Сервер настроен для Active Developer Badge!",
            description=(
                "Этот сервер теперь готов для получения значка Active Developer.\n\n"
                "**Что дальше:**\n"
                "1. Используйте этот сервер как Support Server в настройках приложения\n"
                "2. Подпишитесь на #developer-announcements в Discord Developer Portal\n"
                "3. Используйте команды бота в канале #bot-commands\n"
                "4. Подождите 24 часа\n"
                "5. Получите свой значок!\n\n"
                "**Полезные ссылки:**\n"
                "• [Discord Developer Portal](https://discord.com/developers/applications)\n"
                "• [Active Developer Badge](https://discord.com/developers/active-developer)"
            ),
            color=discord.Color.blue()
        )
        
        await announcements_channel.send(embed=embed)
        
        # Создаем роль для разработчиков
        dev_role = await interaction.guild.create_role(
            name="Developer",
            color=discord.Color.blurple(),
            reason="Роль для активных разработчиков"
        )
        
        # Настраиваем права для каналов
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=False
            ),
            dev_role: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                embed_links=True,
                attach_files=True
            )
        }
        
        await announcements_channel.edit(overwrites=overwrites)
        await commands_channel.edit(overwrites={
            interaction.guild.default_role: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True
            )
        })
        
        # Выдаем роль создателю сервера
        await interaction.user.add_roles(dev_role)
        
        await interaction.followup.send(
            "✅ Сервер успешно настроен для получения Active Developer Badge!\n"
            f"Проверьте канал {announcements_channel.mention} для дальнейших инструкций.",
            ephemeral=True
        )

    except Exception as e:
        await interaction.followup.send(
            f"❌ Произошла ошибка при настройке сервера: {str(e)}\n"
            "Убедитесь, что у бота есть права администратора.",
            ephemeral=True
        )

# Добавим команду для тестирования (необходима для получения значка)
@bot.tree.command(
    name="ping_test",
    description="Тестовая команда для Active Developer Badge"
)
async def ping_test(interaction: discord.Interaction):
    await interaction.response.send_message(
        "🏓 Pong! Эта команда поможет получить значок Active Developer.",
        ephemeral=True
    )

# Добавим новые команды для модерации
@bot.tree.command(name="мут", description="Замутить пользователя")
@app_commands.describe(
    участник="Пользователь для мута",
    время="Время мута (например: 1h, 30m, 1d)",
    причина="Причина мута"
)
@app_commands.default_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, участник: discord.Member, время: str, причина: str = None):
    # Конвертируем время из строки в секунды
    time_convert = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    mute_time = int(время[:-1]) * time_convert[время[-1]]
    
    try:
        await участник.timeout(
            discord.utils.utcnow() + datetime.timedelta(seconds=mute_time),
            reason=причина
        )
        
        embed = discord.Embed(
            title="🔇 Мут",
            description=f"{участник.mention} получил мут на {время}",
            color=discord.Color.red()
        )
        if причина:
            embed.add_field(name="Причина", value=причина)
            
        await interaction.response.send_message(embed=embed)
        
    except Exception as e:
        await interaction.response.send_message(
            f"❌ Ошибка: {str(e)}",
            ephemeral=True
        )

# Система экономики
@bot.tree.command(name="баланс", description="Проверить баланс")
async def balance(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id not in economy:
        economy[user_id] = 0
        
    embed = discord.Embed(
        title="💰 Баланс",
        description=f"У вас {economy[user_id]} монет",
        color=discord.Color.gold()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="работать", description="Заработать монеты")
@app_commands.checks.cooldown(1, 3600)  # Раз в час
async def work(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id not in economy:
        economy[user_id] = 0
        
    earnings = random.randint(10, 100)
    economy[user_id] += earnings
    
    jobs = [
        "поработал в шахте", "продал товары", "написал код",
        "провел стрим", "выполнил задание", "помог NPC"
    ]
    
    embed = discord.Embed(
        title="💼 Работа",
        description=f"Вы {random.choice(jobs)} и заработали {earnings} монет!",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)

# Музыкальные команды
@bot.tree.command(name="плей", description="Включить музыку")
@app_commands.describe(запрос="Название песни или URL")
async def play(interaction: discord.Interaction, запрос: str):
    if not interaction.user.voice:
        await interaction.response.send_message(
            "❌ Вы должны быть в голосовом канале!",
            ephemeral=True
        )
        return
        
    # Здесь будет код для воспроизведения музыки
    # Требуется установка PyNaCl и youtube_dl
    await interaction.response.send_message(
        "🎵 Добавление музыки в очередь...",
        ephemeral=True
    )

# Система тегов (заметок)
@bot.tree.command(name="тег_создать", description="Создать тег")
@app_commands.describe(
    имя="Имя тега",
    контент="Содержимое тега"
)
async def tag_create(interaction: discord.Interaction, имя: str, контент: str):
    if имя in tags:
        await interaction.response.send_message(
            "❌ Тег с таким именем уже существует!",
            ephemeral=True
        )
        return
        
    tags[имя] = {
        "content": контент,
        "author": interaction.user.id,
        "uses": 0
    }
    
    await interaction.response.send_message(
        f"✅ Тег `{имя}` успешно создан!",
        ephemeral=True
    )

@bot.tree.command(name="тег", description="Показать тег")
@app_commands.describe(имя="Имя тега")
async def tag_show(interaction: discord.Interaction, имя: str):
    if имя not in tags:
        await interaction.response.send_message(
            "❌ Тег не найден!",
            ephemeral=True
        )
        return
        
    tags[имя]["uses"] += 1
    await interaction.response.send_message(tags[имя]["content"])

try:
    bot.run(TOKEN)
except Exception as e:
    print(f"❌ Ошибка при запуске бота: {str(e)}")
    print(f"Тип ошибки: {type(e).__name__}") 