import discord
from discord.ext import commands
import asyncio
import os
import asyncpg

# ボットの初期化
intents = discord.Intents.default()
intents.message_content = True
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

# サーバーごとの設定を読み込む関数
async def load_config(pool, guild_id):
    async with pool.acquire() as connection:
        return await connection.fetchrow("SELECT * FROM server_config WHERE guild_id = $1", guild_id)

# ボタンの作成
class MyView(discord.ui.View):
    def __init__(self, notify_channel_id):
        super().__init__(timeout=None)
        self.notify_channel_id = notify_channel_id

    @discord.ui.button(label="🚀 ちゃむる！", style=discord.ButtonStyle.success)
    async def chamuru_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = bot.get_channel(self.notify_channel_id)
        await interaction.response.send_message("メッセージをお知らせチャンネルに送信するよっ！", ephemeral=True)

        if channel:
            user_nick = interaction.user.display_name
            message = await channel.send(f"@everyone\n掘るちゃむ！\nby {user_nick}")
            await asyncio.sleep(300)
            try:
                await message.delete()
            except discord.Forbidden:
                pass
            except discord.HTTPException:
                pass

    @discord.ui.button(label="⚔ 占拠中！", style=discord.ButtonStyle.primary)
    async def senkyo_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = bot.get_channel(self.notify_channel_id)
        await interaction.response.send_message("占拠中のメッセージをお知らせチャンネルに送信するよっ！", ephemeral=True)

        if channel:
            user_nick = interaction.user.display_name
            message = await channel.send(f"@everyone\n都市or拠点占拠中！\nby {user_nick}")
            await asyncio.sleep(600)
            try:
                await message.delete()
            except discord.Forbidden:
                pass
            except discord.HTTPException:
                pass

# ボットが起動したときに自動的にボタンを表示する処理
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    bot.db_pool = await init_db()

    for guild in bot.guilds:
        config = await load_config(bot.db_pool, guild.id)

        if config and config['button_channel_id'] and config['notify_channel_id']:
            button_channel = bot.get_channel(config['button_channel_id'])
            if button_channel:
                async for message in button_channel.history(limit=100):
                    await message.delete()
                view = MyView(config['notify_channel_id'])
                await button_channel.send("## 掘るちゃむをお知らせする", view=view)
            else:
                print(f"{guild.name}: ボタンチャンネルが見つかりませんでした。")
        else:
            print(f"{guild.name}: 設定が不完全です。")

# ボタンチャンネル設定コマンド
@bot.command()
@commands.has_permissions(administrator=True)
async def sb(ctx):
    await save_button_channel(bot.db_pool, ctx.guild.id, ctx.channel.id)
    await ctx.send("ボタンチャンネルを設定しました。")

# 通知チャンネル設定コマンド
@bot.command()
@commands.has_permissions(administrator=True)
async def sn(ctx):
    await save_notify_channel(bot.db_pool, ctx.guild.id, ctx.channel.id)
    await ctx.send("通知チャンネルを設定しました。")

# 通知チャンネルクリアコマンド
@bot.command()
@commands.has_permissions(administrator=True)
async def clear_notify(ctx):
    await save_notify_channel(bot.db_pool, ctx.guild.id, None)
    await ctx.send("通知チャンネルをクリアしました。")

# ボタンチャンネルクリアコマンド
@bot.command()
@commands.has_permissions(administrator=True)
async def clear_button(ctx):
    await save_button_channel(bot.db_pool, ctx.guild.id, None)
    await ctx.send("ボタンチャンネルをクリアしました。")

# ボットを起動
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    bot.run(token)
