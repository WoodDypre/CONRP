import discord
from discord.ext import commands
import random

# Замените на ваш токен
TOKEN = 'MTMyNzcwOTU4OTUyMDc4MTM0NA.GHRvOF.4nw-98xqJ67ZoAABCyiswTsfxvb3NEgBt99idw'

# Укажите ID голосового канала, который нужно отслеживать
TARGET_VOICE_CHANNEL_ID = 1327712930891829372  # Замените на ваш ID канала

# Укажите категорию, в которой будут создаваться временные каналы
TARGET_CATEGORY_ID = 1231524909897875498  # Замените на ID категории

# Создаем экземпляр бота с нужными намерениями
intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True
intents.members = True  # Добавляем members для работы с пользователями
bot = commands.Bot(command_prefix="!", intents=intents)

# Словарь для хранения временных каналов и их создателей
temp_channels = {}

class ControlButtons(discord.ui.View):
    def __init__(self, voice_channel, text_channel, author_id, author_name):
        super().__init__(timeout=None)
        self.voice_channel = voice_channel
        self.text_channel = text_channel
        self.author_id = author_id
        self.author_name = author_name

    @discord.ui.button(label="Сделать видимым для всех", style=discord.ButtonStyle.green)
    async def make_visible_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Вы не являетесь создателем этого канала.", ephemeral=True)
            return

        await self.voice_channel.set_permissions(interaction.guild.default_role, view_channel=True, connect=True)
        await interaction.response.send_message(f"Канал {self.voice_channel.name} теперь видим для всех.", ephemeral=True)

    @discord.ui.button(label="Скрыть канал", style=discord.ButtonStyle.red)
    async def hide_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Вы не являетесь создателем этого канала.", ephemeral=True)
            return

        await self.voice_channel.set_permissions(interaction.guild.default_role, view_channel=False)
        await interaction.response.send_message(f"Канал {self.voice_channel.name} теперь скрыт для всех, кроме вас.", ephemeral=True)

@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel and after.channel.id == TARGET_VOICE_CHANNEL_ID:
        frequency = round(random.uniform(30.000, 213.000), 3)
        channel_name = f"{frequency} МГц"
        
        category = member.guild.get_channel(TARGET_CATEGORY_ID)
        
        new_voice_channel = await category.create_voice_channel(
            name=channel_name,
            overwrites={
                member.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                member: discord.PermissionOverwrite(view_channel=True, connect=True, manage_channels=True)
            }
        )
        
        new_text_channel = await category.create_text_channel(
            name=f"{channel_name}-text",
            overwrites={
                member.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                member: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True, manage_channels=True)
            }
        )
        
        temp_channels[new_voice_channel.id] = (new_voice_channel, new_text_channel, member.id)
        
        await member.move_to(new_voice_channel)
        
        view = ControlButtons(new_voice_channel, new_text_channel, member.id, member.display_name)
        await new_text_channel.send(
            f"{member.mention}, ваш канал '{channel_name}' создан. Используйте кнопки ниже, чтобы управлять доступом к каналу.", view=view
        )

    if before.channel and before.channel.id in temp_channels:
        voice_channel, text_channel, creator_id = temp_channels[before.channel.id]
        if len(voice_channel.members) == 0:
            await voice_channel.delete()
            await text_channel.delete()
            del temp_channels[before.channel.id]

bot.run(TOKEN)
