import discord
from discord.ext import commands
import datetime
import json
import random

intents = discord.Intents.default()
intents.message_content = True

with open('setting.json','r',encoding='utf8') as jfile :
    jdata = json.load(jfile)
    
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(">>Bot is online<<")
#機器人登入完成
    
#-------------------------自動功能-------------------------

#偵測訊息修改
@bot.event
async def on_message_edit(before, after):
    if before.channel.id == int(jdata["Test_channel_ID"]):
        channel = bot.get_channel(int(jdata["Test_channel_ID"]))
        time=datetime.date.today()
        await channel.send(F'{before.author.mention}<{time}>更新了加班/請假訊息')

#偵測訊息關鍵字
@bot.event
async def on_message(msg):
    keyword = ['apple','bird','cat','dog']
    if msg.content in keyword and msg.author != bot.user:
        await msg.channel.send('bingo')
    await bot.process_commands(msg)
#---------------------------指令---------------------------

@bot.command()
async def hi(ctx):
	await ctx.send('Hello!')

#回覆延遲
@bot.command()
async def ping(ctx):
    await ctx.send(F'{round(bot.latency*1000)}ms')

#回覆圖片
@bot.command()
async def 圖片(ctx): 
    pic = discord.File(jdata['PIC1'])
    await ctx.send(file=pic)

#回覆隨機圖片
@bot.command()
async def 隨機圖片(ctx):
    random_pic=random.choice(jdata['PIC2'])
    pic = discord.File(random_pic)
    await ctx.send(file=pic)

#訊息清理
@bot.command()
async def clean(ctx,num:int):
    await ctx.channel.purge(limit=num+1)

#---------------------------點餐---------------------------


# 建立一個字典來記錄每個人的點餐內容和總金額
orders = {}

@bot.event
async def on_message(message):
    # 避免 bot 自己的訊息觸發事件
    if message.author == bot.user:
        return

    # 檢查是否是點餐指令
    if message.content.startswith('!點餐'):
        await handle_order_message(message)

    # 繼續處理其他訊息事件
    await bot.process_commands(message)

@bot.event
async def on_message_edit(before, after):
    # 檢查是否是點餐指令
    if after.content.startswith('!點餐'):
        # 刪除編輯前的點餐紀錄
        await handle_order_edit(before, remove=True)
        # 處理編輯後的點餐指令
        await handle_order_message(after)
        # 加上反應
        await after.add_reaction('📝')

async def handle_order_message(message):
    order_content = message.content[len('!點餐'):].strip()
    
    # 獲取使用者名稱
    if message.author.display_name == 'Talk Bot': #特定ID改用第一字串當點餐人
        user = order_content.split()[0]
        order_content = ' '.join(order_content.split()[1:])
    else:
        user = message.author.display_name

    # 檢查是否已經點過餐
    if user in orders:
        await message.channel.send(f'{user} 你已經點過了，更改餐點請編輯訊息!')
        return
    else:
        await message.add_reaction('👌')
    # 提取點餐內容和餐點金額
    amount_start_index = order_content.rfind('$')

    if amount_start_index != -1:
        order_items = order_content[:amount_start_index].strip()
        order_amount = float(order_content[amount_start_index + 1:].strip())
    else:
        order_items = order_content
        order_amount = 0.0

    # 將點餐記錄到字典中
    orders[user] = {'items': [order_items], 'amount': order_amount}

    # await message.channel.send(f'{user} 已點餐：{order_items}\t金額：${order_amount:.0f}')

async def handle_order_edit(message, remove=False):
    # 刪除編輯前的點餐紀錄
    order_content = message.content[len('!點餐'):].strip()
    
    # 獲取使用者名稱
    if message.author.display_name == 'Talk Bot': #特定ID改用第一字串當點餐人
        user = order_content.split()[0]
    else:
        user = message.author.display_name

    if user in orders:
        # 移除點餐紀錄
        if remove:
            del orders[user]
        else:
            # 更新點餐紀錄
            amount_start_index = order_content.rfind('$')
            if amount_start_index != -1:
                order_items = order_content[:amount_start_index].strip()
                order_amount = float(order_content[amount_start_index + 1:].strip())
                orders[user]['items'] = [order_items]
                orders[user]['amount'] = order_amount
            else:
                orders[user]['items'] = [order_content]
                orders[user]['amount'] = 0.0

        #await message.channel.send(f'{user} 已點餐：{order_items}\t金額：${order_amount:.0f}')

    # 繼續處理其他訊息事件
    await bot.process_commands(message)


# 定義收單指令
@bot.command(name='收單')
async def finalize_order(ctx):
    # 整理每個人的點餐內容和總金額
    final_orders = "\n".join([f'{user}：{"+".join(items["items"])}\t總金額：${items["amount"]:.0f}' for user, items in orders.items()])
    
    # 計算整單金額總和
    total_amount = sum(items['amount'] for items in orders.values())

    # 顯示整理後的點餐內容和總金額
    #await ctx.send(f'收單完成，點餐清單：\n{final_orders}\n整單金額總和：${total_amount:.0f}')

    

    embed=discord.Embed(title="點餐清單", color=0xf7872b)
    for user, items in orders.items():
        embed.add_field(name=f'{user}', value=f'{"+".join(items["items"])}\t\t金額：${items["amount"]:.0f}', inline=False)
    embed.set_footer(text=f'總計 : ${total_amount:.0f}')
    await ctx.send(embed=embed)

    
    # 清空點餐字典
    orders.clear()

bot.run(jdata['TOKEN'])
