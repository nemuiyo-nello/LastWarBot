import os
import discord
from discord.ext import commands, tasks
from discord.ui import Button, View

# 環境変数からトークンを取得
TOKEN = os.getenv('DISCORD_TOKEN')

# botのプレフィックスを設定
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ボタンのコールバック
async def button_callback(interaction: discord.Interaction):
    channel = bot.get_channel(1290535817563082863)  # ボタン設置チャンネル
    if channel:
        user_nick = interaction.user.display_name
        message = await channel.send(f"@everyone\n掘るちゃむ！\nby {user_nick}")
        await message.delete()  # メッセージを削除
        await interaction.response.send_message("メッセージをお知らせチャンネルに送信しました！", ephemeral=True)  # ユーザーに応答
    else:
        await interaction.response.send_message("指定したチャンネルが見つかりませんでした。", ephemeral=True)

# ボタンを作成するコマンド
@bot.command()
async def create_button(ctx):
    button = Button(style=discord.ButtonStyle.success, label='🚀 ちゃむる！')
    button.callback = button_callback

    view = View()
    view.add_item(button)

    await ctx.send("## 掘るちゃむをお知らせする", view=view)

# Botの起動時に実行されるイベント
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

# Botの実行
bot.run(TOKEN)
