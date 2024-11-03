import discord
from discord.ext import commands
import asyncio
import os
import asyncpg

# ボットの初期化
intents = discord.Intents.default()
intents.message_content = True  # メッセージコンテンツのインテントを有効にする
bot = commands.Bot(command_prefix="!", intents=intents)

# データベースに接続する関数
async def init_db():
    return await asyncpg.create_pool(dsn=os.getenv('DATABASE_URL'))

# サーバーごとの設定を保存する関数（ボタンチャンネルID）
async def save_button_channel(pool, guild_id, button_channel_id):
    async with pool.acquire() as connection:
        await connection.execute(""" 
            INSERT INTO server_config (guild_id, button_channel_id)
            VALUES ($1, $2)
            ON CONFLICT (guild_id) DO UPDATE
            SET button_channel_id = $2
        """, guild_id, button_channel_id)

# サーバーごとの設定を保存する関数（通知チャンネルID）
async def save_notify_channel(pool, guild_id, notify_channel_id):
    async with pool.acquire() as connection:
        await connection.execute(""" 
            INSERT INTO server_config (guild_id, notify_channel_id)
            VALUES ($1, $2)
            ON CONFLICT (guild_id) DO UPDATE
            SET notify_channel_id = $2
        """, guild_id, notify_channel_id)

# サーバーごとの設定を保存する関数（サブチャンネルID）
async def save_sub_channel(pool, guild_id, sub_channel_id):
    async with pool.acquire() as connection:
        await connection.execute("""
            INSERT INTO server_config (guild_id, sub_channel_id)
            VALUES ($1, $2)
            ON CONFLICT (guild_id) DO UPDATE
            SET sub_channel_id = $2
        """, guild_id, sub_channel_id)

# サーバーごとの設定を読み込む関数
async def load_config(pool, guild_id):
    async with pool.acquire() as connection:
        return await connection.fetchrow("SELECT * FROM server_config WHERE guild_id = $1", guild_id)

# ボタンの作成
class MyView(discord.ui.View):
    def __init__(self, notify_channel_id):
        super().__init__(timeout=None)  # timeoutをNoneに設定して無効化
        self.notify_channel_id = notify_channel_id  # 通知チャンネルのIDを保存

    # 「🚀 ちゃむる！」ボタン
    @discord.ui.button(label="🚀 ちゃむる！", style=discord.ButtonStyle.success)
    async def chamuru_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = bot.get_channel(self.notify_channel_id)
        await interaction.response.send_message("メッセージをお知らせチャンネルに送信するよっ！", ephemeral=True)

        if channel is not None:
            user_nick = interaction.user.display_name  # サーバーニックネームまたは表示名を取得
            try:
                message = await channel.send(f"@everyone\n🌟 わーい！掘るちゃむよ～！🌟\n {user_nick} が教えてくれたよっ！🎉")

                # 5分後にメッセージを削除
                await asyncio.sleep(300)
                try:
                    await message.delete()
                except discord.Forbidden:
                    pass
                except discord.NotFound:
                    pass  # メッセージが既に削除されていた場合、エラーを無視
                except discord.HTTPException as e:
                    print(f"メッセージ削除時のエラー: {e}")
            except discord.Forbidden:
                await interaction.response.send_message("メッセージを送信する権限がありません。", ephemeral=True)
            except discord.HTTPException as e:
                print(f"メッセージ送信時のエラー: {e}")
        else:
            await interaction.response.send_message("指定したチャンネルが見つかりませんでした。", ephemeral=True)

    # 「⚔ 占拠中！」ボタン
    @discord.ui.button(label="⚔ 占拠中！", style=discord.ButtonStyle.primary)
    async def senkyo_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = bot.get_channel(self.notify_channel_id)
        await interaction.response.send_message("占拠中のメッセージをお知らせチャンネルに送信するよっ！", ephemeral=True)

        if channel is not None:
            user_nick = interaction.user.display_name  # サーバーニックネームまたは表示名を取得
            try:
                message = await channel.send(f"@everyone\n🔔 速報！🔔都市or拠点を占拠中！\n {user_nick} が呼んでるよっ！👑")

                # 10分後にメッセージを削除
                await asyncio.sleep(600)
                try:
                    await message.delete()
                except discord.Forbidden:
                    pass
                except discord.NotFound:
                    pass  # メッセージが既に削除されていた場合、エラーを無視
                except discord.HTTPException as e:
                    print(f"メッセージ削除時のエラー: {e}")
            except discord.Forbidden:
                await interaction.response.send_message("メッセージを送信する権限がありません。", ephemeral=True)
            except discord.HTTPException as e:
                print(f"メッセージ送信時のエラー: {e}")
        else:
            await interaction.response.send_message("指定したチャンネルが見つかりませんでした。", ephemeral=True)

    # サブチャンネル通知ボタン
    @discord.ui.button(label="🎉 夜ちゃむ！", style=discord.ButtonStyle.secondary)
    async def sub_notify_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        config = await load_config(bot.db_pool, interaction.guild_id)
        if config and config['sub_channel_id']:
            sub_channel = bot.get_channel(config['sub_channel_id'])
            if sub_channel is not None:
                user_nick = interaction.user.display_name
                try:
                    message = await sub_channel.send(f"@here\n🔔 深夜🌙の掘るちゃむ！\n {user_nick} が教えてくれたよっ！🎉")

                    # 5分後にメッセージを削除
                    await asyncio.sleep(300)
                    try:
                        await message.delete()
                    except discord.Forbidden:
                        pass
                    except discord.NotFound:
                        pass  # メッセージが既に削除されていた場合、エラーを無視
                    except discord.HTTPException as e:
                        print(f"メッセージ削除時のエラー: {e}")
                except discord.Forbidden:
                    await interaction.response.send_message("メッセージを送信する権限がありません。", ephemeral=True)
                except discord.HTTPException as e:
                    print(f"メッセージ送信時のエラー: {e}")
            else:
                await interaction.response.send_message("指定したサブチャンネルが見つかりませんでした。", ephemeral=True)
        else:
            await interaction.response.send_message("サブチャンネルが設定されていません。", ephemeral=True)

# メッセージ一括削除コマンド
@bot.command()
@commands.has_permissions(manage_messages=True)  # メッセージ管理の権限が必要
async def clear(ctx, amount: int):
    """指定した数のメッセージを削除するコマンド"""
    if amount <= 0:
        await ctx.send("削除するメッセージの数は1以上で指定してください。")
        return

    try:
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f"メッセージを {len(deleted)} 件削除しちゃった！🧹✨️")  # 確認メッセージ
    except discord.Forbidden:
        await ctx.send("メッセージを削除する権限がありません。", ephemeral=True)
    except discord.HTTPException as e:
        print(f"メッセージ削除時のエラー: {e}")

# ボットが起動したときに自動的にボタンを表示する処理
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

    # データベースに接続
    bot.db_pool = await init_db()

    # すべてのギルド（サーバー）ごとにボタンを表示
    for guild in bot.guilds:
        config = await load_config(bot.db_pool, guild.id)

        if config and config['button_channel_id'] and config['notify_channel_id']:
            button_channel_id = config['button_channel_id']
            notify_channel_id = config['notify_channel_id']
            sub_channel_id = config.get('sub_channel_id')  # サブチャンネルIDを取得

            button_channel = bot.get_channel(button_channel_id)
            if button_channel is not None:
                view = MyView(notify_channel_id)
                await button_channel.send("## ボタンを押してお知らせするよ！", view=view)
            else:
                print(f"サーバー {guild.name} のボタン設置用チャンネルが見つかりませんでした。")
        else:
            print(f"サーバー {guild.name} の設定が不完全です。")

# コマンド - ボタン設置チャンネルを設定
@bot.command()
@commands.has_permissions(administrator=True)
async def bt(ctx):
    button_channel_id = ctx.channel.id
    await save_button_channel(bot.db_pool, ctx.guild.id, button_channel_id)
    await ctx.send("ボタン設置チャンネルを設定したよ！")

# コマンド - 通知チャンネルを設定
@bot.command()
@commands.has_permissions(administrator=True)
async def nt(ctx):
    notify_channel_id = ctx.channel.id
    await save_notify_channel(bot.db_pool, ctx.guild.id, notify_channel_id)
    await ctx.send("通知チャンネルを設定したよ！")

# コマンド - サブチャンネルを設定
@bot.command()
@commands.has_permissions(administrator=True)
async def ss(ctx):
    sub_channel_id = ctx.channel.id
    await save_sub_channel(bot.db_pool, ctx.guild.id, sub_channel_id)
    await ctx.send("サブチャンネルを設定したよ！")

# Botの起動
bot.run(os.getenv('DISCORD_TOKEN'))
