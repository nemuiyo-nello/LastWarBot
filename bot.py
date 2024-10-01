import discord
from discord.ext import commands
from discord.ui import Button, View
import os
import asyncio

intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

# チャンネルIDの設定
button_channel_id = 1290535817563082863  # ボタンを設置するチャンネル
notify_channel_id = 1284553911583113290  # 通知を送りたいチャンネル

# ボタンのコールバック
class MyView(View):
    @discord.ui.button(label='🚀 ちゃむる！', style=discord.ButtonStyle.success)
    async def button_callback(self, button: Button, interaction: discord.Interaction):
        await interaction.response.send_message("メッセージをお知らせチャンネルに送信しました！", ephemeral=True)  # ユーザーに応答
        notify_channel = bot.get_channel(notify_channel_id)
        await notify_channel.send(f"@everyone\n掘るちゃむ！\nby {interaction.user.nick}")
        await asyncio.sleep(300)  # 5分待機
        # ここで必要に応じてメッセージを削除するコードを追加できます

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

    channel = bot.get_channel(button_channel_id)
    if channel:
        # チャンネル内のメッセージを削除
        async for message in channel.history(limit=100):
            await message.delete()
        # ボタンを設置
        view = MyView()
        await channel.send("ボタンを押してください！", view=view)

# Botのトークンを環境変数から取得
TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)
