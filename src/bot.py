
import discord
from discord.ext import commands
from discord.ext.commands import Context
from discord import app_commands 
from urllib.request import urlopen
import json
import pymongo
from pymongo import MongoClient
import datetime
import config

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='?', intents=intents)


client = MongoClient(config.mongo_key)
token = config.bot_key
database = config.database
db = client[database]



#--- Bot Startup
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


#Help CMD
@bot.tree.command()
async def help(interaction: discord.Interaction):
    """Help - Bot Commands"""
    #Webhook
    data = {
    "title": "Bot Commands",
    "description": "Use **/help** to bring up this menu anytime.",
    "color": 15856113,
        "fields": [
            {
            "name": "/track_product",
            "value": "Track a product(s) sales.\nRequires: `Product Link`"
            },
            {
            "name": "/check_product_data",
            "value": "Check total sales & data for product.\nRequires: `Product Link`"
            },
            {
            "name": "Product Link",
            "value": "EX: `https://juicleds.com/products/galaxy-projector`"
            },
            {
            "name": "/check_store_data (Unavailable version)",
            "value": "Check total sales & data for store\nRequires: `Website Link`"
            },
        ],
    "footer": {
    "text": "If you're tracking a new store, you must first use /track_product."
    },
    }
    embed = discord.Embed.from_dict(data)
    await interaction.response.send_message(embed = embed)

@bot.tree.command()
async def upgrade(interaction: discord.Interaction):
    """More Commands"""
    #Webhook
    data = {
    "title": "Get the latest version",
    "description": "The full 1.0 version is avaliable to purchase or even custom modified\nAdd me on discord or create an offer on fiverr for more information",
    "color": 15856113,
        "fields": [
            {
            "name": "Discord/Fiverr",
            "value": "`Tripping_Lettuce#3780`\n`https://www.fiverr.com/tripping_lettuc`"
            },
            {
            "name": "Version 1.0!",
            "value": "Track multiple products from same store!\nTrack stats of store specific products with `/check_store_data`\n More accurate tracking up to `99.9%` accurate\nStop tracking after 30 days\nBetter UI with gif `\help`"
            },
            {
            "name": "Version 2.0!!!",
            "value": "User Specfic Products and Stores\nButton scroll display for products\nTrack entire stores\nCustom Pings\nTrack incoming products\nEven better UI"
            },

        ],
    "footer": {
    "text": "All profits go to paying of my student loans :)"
    },
    "image": {
        "url": "https://cdn.discordapp.com/attachments/1062641874852122735/1080413136441577493/ezgif.com-video-to-gif.gif"
    }
    }
    embed = discord.Embed.from_dict(data)
    await interaction.response.send_message(embed = embed)


@bot.tree.command()
async def track_product(interaction: discord.Interaction,product_link:str):
    """Track a product(s) sales"""

    #Handel ID Get
    handle_id = product_link.split("/products/")[1]
    #Domain Get
    domain = product_link.split("/")[2]
    #Json Product Page Get
    url = f"https://{domain}/products/{handle_id}/products.json"
    #Open Json File Try
    try:
        response = urlopen(url)
    except:
        content = "There seems to be an error with the link use /help"
        await interaction.response.send_message(content=content, ephemeral=True)
    # Loads Json and Reads Try
    data_json = json.loads(response.read())
    #Send to function to organize and send to mongo Func
    data = organize(data_json,domain,handle_id)
    embed = discord.Embed.from_dict(data)
    await interaction.response.send_message(embed = embed)




def organize(data_json: str, domain:str,handle_id:str):


    # Go to Mongo Collection
    collection = db[domain]
    #Started Tracking Get
    today = datetime.datetime.today()
    formatted_date = today.strftime('%m-%d-%y')
    document_count = collection.count_documents({})

    prod_handle = data_json["product"]['handle']


    if document_count == 2:
        prodData = collection.find_one({"_id": 1})
        db_handle = prodData["handle"]
        if db_handle == prod_handle:
            data = {
            "title": "This product is already being tracked",
            "description": "Use /check_product_data to check total sales & data for this product.\nRequires: `Product Link`",
            "color": 880808,
            }
            return data

    collection.insert_one({"_id":0,"track_start":formatted_date,"total":0.00,"week":0.00}) #time stamps to track time

    prod_name = data_json["product"]['title']
    prod_bought = data_json["product"]['updated_at']
    prod_post = data_json["product"]['published_at']

    #Product Sales,Ammount Set
    sold_total = 0
    sold_prod = 0

    #Product Image Set
    src = data_json["product"]["images"][0]["src"]

    #Price from variants Get
    prod_price = data_json["product"]["variants"][0]["price"]
    prod_price = float(prod_price) #Convert to int

    #Put into mongo Push
    collection.insert_one({"_id":1,"title":prod_name,"handle":prod_handle,"bought":prod_bought,"post":prod_post,"image":src,"price":prod_price, "total_price":sold_total,"total_sales":sold_prod,"track_start":formatted_date})
    
    url = "https://" + domain

    data = {
    "title": domain,
    "description": "Allow 24 hours for data to populate.",
    "url": url,
    "color": 15856113,
    "fields": [
            {
            "name": "/track_product",
            "value": "Track a product sales.\nRequires: `Product Link`"
            },
            {
            "name": "/check_product_data",
            "value": "Check total sales & data for product.\nRequires: `Product Link`"
            },
            {
            "name": "/help",
            "value": "Show the list of commands."
            }
    ],
    "author": {
        "name": "Product Tracking Started"
        }
    }
    return data



@bot.tree.command()
async def check_product_data(interaction: discord.Interaction, product_link:str):
    """Check total sales & data for product"""

    #Handel ID Get
    handle_id = product_link.split("/products/")[1]
    #Domain Get
    domain = product_string = product_link.split("/")[2]
    #Get mongo colelction Get
    collection = db[domain]



    prodData = collection.find_one({"_id": 1})


    #----Get Top Data-----
    title = prodData["title"]
    domain = domain.replace("/", "")
    handle = prodData["handle"]
    src = prodData["image"]
    prod_price = prodData["total_price"]
    prod_price = str(prod_price)
    prod_sales = prodData["total_sales"]
    track_start = prodData["track_start"]
    prod_pricessss = prodData["price"]
    #Get Post Date
    prod_post = prodData["post"]
    prod_post = prod_post.split("T")[0]

    prod_buy = prodData["bought"]
    prod_buy1 = prod_buy.split("T")[0]
    prod_buy2 = prod_buy.split("T")[1]
    prod_buy2 = prod_buy2.split("-")[0]
    prod_buy = f"{prod_buy1} : {prod_buy2}" 

    product_link = "https://" + domain + '/products/' + handle


    data = {
    "title": title,
    "url": product_link,
    "color": 15856113,
    "fields": [
        {
        "name": "Product Tracking Since",
        "value": track_start,
        "inline": True
        },
        {
        "name": "Total Sales",
        "value": f"${prod_price}",
        "inline": True
        },
        {
        "name": "7 Day Sales",
        "value": f"${prod_price}",
        "inline": True
        },
        {
        "name": "Product Data",
        "value": f"-----------------------------\n**Name - {title}\nLast Sold - {prod_buy}\nCreated - {prod_post}\nPrice - {prod_pricessss}**\n-----------------------------"
        },
    ],
    "author": {
    "name": "Product Sales Data"
    },
    "footer": {
        "text": "Tracking stops if not searched in 30 days, or no sales in 3 days."
    },
    "thumbnail": {
        "url": src
    }
    }

    embed = discord.Embed.from_dict(data)
    await interaction.response.send_message(embed = embed)


#------ Sync Command ------
@bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(ctx: Context):
	synced = await ctx.bot.tree.sync()
	await ctx.send(f"Synced {len(synced)} commands {'globally'}")


bot.run(token) 

