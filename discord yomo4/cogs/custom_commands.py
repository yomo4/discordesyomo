from discord.ext import commands
import discord

class CustomCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(manage_messages=True)
    @commands.command(name='poll')
    async def create_poll(self, ctx, question, *options):
        """Создание опроса"""
        if len(options) < 2:
            await ctx.send('Нужно указать как минимум 2 варианта ответа!')
            return
            
        embed = discord.Embed(title='📊 Опрос', description=question)
        
        # Эмодзи для вариантов ответа
        emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
        
        for idx, option in enumerate(options[:5]):
            embed.add_field(name=f'Вариант {idx+1}', value=f'{emojis[idx]} {option}', inline=False)
            
        poll_msg = await ctx.send(embed=embed)
        
        for idx in range(len(options[:5])):
            await poll_msg.add_reaction(emojis[idx])

    @commands.has_permissions(manage_channels=True)
    @commands.command(name='ticket')
    async def create_ticket(self, ctx):
        """Создание тикета поддержки"""
        category = discord.utils.get(ctx.guild.categories, name='Тикеты')
        if not category:
            category = await ctx.guild.create_category('Тикеты')
            
        channel = await ctx.guild.create_text_channel(
            f'ticket-{ctx.author.name}',
            category=category
        )
        
        await channel.send(f'{ctx.author.mention}, ваш тикет создан! Опишите вашу проблему.')

async def setup(bot):
    await bot.add_cog(CustomCommands(bot)) 