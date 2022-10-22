from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import requests
import json
from datetime import datetime
import time
import aioschedule
import asyncio
from aiogram.utils.markdown import link


TOKEN = '1861045996:AAEmp4x_X3Kly6gKKpmlkXAgxsH2xq2ScE0'

a = open("coins.txt", "r")
a = a.read()
coins = list(map(str, a.split()))
print(coins)

def info(s):
	req = ""

	lost_dict = {}
	lost_dict["last_updated_at"] = 'not found'
	lost_dict['usd'] = 'not found'
	lost_dict['5min'] = 'not found'
	lost_dict['15min'] = 'not found'
	lost_dict['30min'] = 'not found'
	lost_dict['5min_num'] = 0
	lost_dict['15min_num'] = 0
	lost_dict['30min_num'] = 0


	req = "https://api.coingecko.com/api/v3/simple/price?ids=" + s + "&vs_currencies=usd&include_last_updated_at=true"
	inf = requests.get(req)
	inf = inf.content
	inf = inf[1:-1]
	if len(inf) < 10:
		return(lost_dict)
	else:
		inf = inf[len(s)+3:]
		dict_inf = json.loads(inf)
		dict_inf["last_updated_at"] = datetime.utcfromtimestamp(dict_inf["last_updated_at"]).strftime('%Y-%m-%d %H:%M:%S')

		req_delta = ''
		time_now = int(time.time())
		time_back = time_now - 1860
		req_delta = 'https://api.coingecko.com/api/v3/coins/{coin}/market_chart/range?vs_currency=usd&from={time_back}&to={time_now}%20'.format(coin = s, time_back = time_back, time_now = time_now)
		inf_delta = requests.get(req_delta)
		inf_delta = inf_delta.content
		dict_inf_delta = json.loads(inf_delta)
		dict_inf.update(dict_inf_delta)
		print('https://api.coingecko.com/api/v3/coins/{coin}/market_chart/range?vs_currency=usd&from={time_back}&to={time_now}%20'.format(coin = s, time_back = time_back, time_now = time_now))
#		try:
		dict_inf['5min'] = "{:+.2%}".format( ((float(dict_inf['usd']) - float(dict_inf['prices'][-1][1])) / dict_inf['prices'][-1][1]) )
		dict_inf['15min'] ="{:+.2%}".format( ((float(dict_inf['usd']) - float(dict_inf['prices'][int((len(dict_inf['prices']) + 1) / 2)][1])) / dict_inf['prices'][0][1]) )
		dict_inf['30min'] ="{:+.2%}".format( ((float(dict_inf['usd']) - float(dict_inf['prices'][0][1])) / dict_inf['prices'][0][1]) )
		dict_inf['5min_num'] =  ((float(dict_inf['usd']) - float(dict_inf['prices'][-1][1])) / dict_inf['prices'][-1][1])
		dict_inf['15min_num'] = ((float(dict_inf['usd']) - float(dict_inf['prices'][int((len(dict_inf['prices']) + 1) / 2)][1])) / dict_inf['prices'][0][1])
		dict_inf['30min_num'] = ((float(dict_inf['usd']) - float(dict_inf['prices'][0][1])) / dict_inf['prices'][0][1])
#		except Exception as ex:
#		bot.send_message(-587721800, 'checker is completly fucked, error – {ex}'.format(ex = ex))
#			return(lost_dict)
		return(dict_inf)



bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

cnt = 0

async def checker():
	global cnt
	cnt += 1
	res = ''
	a = open("coins.txt", "r")
	a = a.read()
	coins = list(map(str, a.split()))
	for i in range(len(coins)):
		s = coins[i]
		inf = info(s)
		print('check is done \n{s} had some changes: for 5min – {min5}, for 15min – {min15}, for 30min – {min30}'.format(s = s, res = res, min5 = inf['5min'], min15 = inf['15min'], min30 = inf['30min']))
		if (abs(inf['5min_num']) >= 0.05 or abs(inf['15min_num']) >= 0.05 or abs(inf['30min_num']) >= 0.05):
			caco = '{s} had some changes: for 5min – {min5}, for 15min – {min15}, for 30min – {min30}'.format(s = link(s, 'https://www.coingecko.com/en/coins/{s}'.format(s = s)), res = res, min5 = inf['5min'], min15 = inf['15min'], min30 = inf['30min'])
			res += caco + '\n'
			await bot.send_message(-587721800, caco, parse_mode = 'markdown', disable_web_page_preview = True)
	#if (res == ''):
		#await bot.send_message(message.from_user.id, "nothing happend")
	if (cnt == 12):
		await bot.send_message(-587721800, 'checker is working')
		cnt = 0

async def scheduler():
	aioschedule.every(5).minutes.do(checker)
	while True:
		await aioschedule.run_pending()
		await asyncio.sleep(1)

async def on_startup(_):
    asyncio.create_task(scheduler())


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Hello, I am Tony and I will help make you some money ;)")


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("If you want to add coin to watchlist – type /addcoin 'coin_name' \nIf you want to remove coin from watchlist – type /rmcoin 'coin_name'")


@dp.message_handler(commands=['addcoin'])
async def addcoin_answer(message: types.Message):
	if (message.text != "/addcoin"):
		coins.append(message.text[9::])
		a = open("coins.txt", "a")
		a.write('\n')
		a.write(coins[-1])
		await bot.send_message(message.from_user.id, message.text[9:] + " has been added")
	else:
		await bot.send_message(message.from_user.id, "Try again")


@dp.message_handler(commands=['allcoins'])
async def allcoins_answer(message):
	res = ""
	a = open("coins.txt", "r")
	a = a.read()
	coins = list(map(str, a.split()))
	for i in range(len(coins)):
		res = res + "\n" + coins[i]
	await bot.send_message(message.from_user.id, res)



@dp.message_handler(commands=['rmcoin'])
async def rmcoin_answer(message):
	a = open("coins.txt", "r")
	a = a.read()
	perres = message.text[8:]
	if (a.find(perres) == -1):
		await bot.send_message(message.from_user.id, "Try again")
	else:
		a = a.split()
		a.remove(perres)
		m = open("coins.txt", "w")
		result = ''
		for i in range(len(a)):
			result = result + "\n" + a[i]
		print(result)
		m.write(result)
		await bot.send_message(message.from_user.id, message.text[7:] + " has been deleted")


@dp.message_handler(commands=['coinstat'])
async def coinstat_answer(message):
	if (message.text != "/coinstat"):
		s = message.text[10::]
		inf = {}
		inf = info(s)
		print(s)
		print(inf)
		#await bot.send_message(message.from_user.id, str(inf['usd']) + ' price in usd' + '\n' + 'last updated at ' + inf['last_updated_at'] + '\ndeltas: for 5min – {min5}, for 15min – {min15}, for 30min – {min30}'.format(min5 = inf['5min'], min15 = inf['15min'], min30 = inf['30min']) + '\n' + '\n')
		await bot.send_message(message.from_user.id, 'for {coin} {price} – price in usd  \nlast updated at: {last_updated_at} \ndeltas: for 5min – {min5}, for 15min – {min15}, for 30min – {min30}'.format(coin = link(s, 'https://www.coingecko.com/en/coins/{s}'.format(s = s)), price = inf['usd'], last_updated_at = inf['last_updated_at'], min5 = inf['5min'], min15 = inf['15min'], min30 = inf['30min']) + '\n' + '\n', parse_mode='markdown', disable_web_page_preview = True)

@dp.message_handler(commands = ['allstat'])
async def allstat_answer(message):
	res = ''
	a = open("coins.txt", "r")
	a = a.read()
	coins = list(map(str, a.split()))
	for i in range(len(coins)):
		s = coins[i]
		inf = info(s)
		print(inf['prices'])
		res += 'for {coin} {price} – price in usd  \nlast updated at: {last_updated_at} \ndeltas: for 5min – {min5}, for 15min – {min15}, for 30min – {min30}'.format(coin = s, price = inf['usd'], last_updated_at = inf['last_updated_at'], min5 = inf['5min'], min15 = inf['15min'], min30 = inf['30min']) + '\n' + '\n'
		#res += 'for {coin} {price} – price in usd  \nlast updated at: {last_updated_at} \ndeltas: for 5min – {min5}, for 15min – {min15}, for 30min – {min30}'.format(coin = link(s, 'https://www.coingecko.com/en/coins/{s}'.format(s = s)), price = inf['usd'], last_updated_at = inf['last_updated_at'], min5 = inf['5min'], min15 = inf['15min'], min30 = inf['30min']) + '\n' + '\n'
	print(res)
	await bot.send_message(message.from_user.id, res, parse_mode = 'markdown', disable_web_page_preview = True)


if __name__ == '__main__':
	executor.start_polling(dp, on_startup=on_startup)
