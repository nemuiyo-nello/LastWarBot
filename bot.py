import discord
from discord.ext import commands, tasks
import asyncio
import os

# ボットの初期化
intents = discord.Intents.default()
intents.message_content = True  # メッセージコンテンツのインテントを有効にする
bot = commands.Bot(command_prefix="!", intents=intents)

# ボタンの作成
class MyView(discord.ui.View):
    def __init__(self, notify_channel_id):
        super().__init__()
        self.notify_channel_id = notify_channel_id  # 通知を送るチャンネルのIDを保存

    @discord.ui.button(label="🚀 ちゃむる！", style=discord.ButtonStyle.success)
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 通知を送るチャンネルIDで指定
        channel = bot.get_channel(self.notify_channel_id)

        if channel is not None:
            # サーバーニックネームを取得
            user_nick = interaction.user.display_name  # サーバーニックネームまたは表示名を取得
            message = await channel.send(f"@everyone\n掘るちゃむ！\nby {user_nick}")  # ユーザーのニックネームをメッセージに追加

            # 5分後にメッセージを削除
            await asyncio.sleep(300)  # 300秒（5分）待機
            await message.delete()  # メッセージを削除
        else:
            await interaction.response.send_message("指定したチャンネルが見つかりませんでした。", ephemeral=True)

# 定期的にメッセージを送信するタスク
@tasks.loop(minutes=10)  # 10分ごとに実行
async def send_ping():
    channel = bot.get_channel(1290535817563082863)  # 適切なチャンネルIDに変更
    if channel is not None:
        await channel.send("ボットは元気です！")

# ボットが起動したときに自動的にボタンを表示する処理
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    send_ping.start()  # タスクを開始

    # ボタンを設置するチャンネルID
    button_channel_id = 1290535817563082863  # ボタンを設置したいチャンネルのID
    # 通知を送るチャンネルID
    notify_channel_id = 1284553911583113290  # 通知を送りたいチャンネルのID

    # ボタンを設置するチャンネルを取得
    button_channel = bot.get_channel(button_channel_id)
    if button_channel is not None:
        # 指定したチャンネルのメッセージを削除
        async for message in button_channel.history(limit=100):  # 最後の100件のメッセージを削除
            await message.delete()
        
        view = MyView(notify_channel_id)  # 通知チャンネルのIDをビューに渡す
        await button_channel.send("## 掘るちゃむをお知らせする", view=view)
    else:
        print("指定したボタン設置用のチャンネルが見つかりませんでした。")

# ボットを起動
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')  # 環境変数からボットのトークンを取得
    bot.run(token)
