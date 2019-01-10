# -*- coding: utf-8 -*-
import io
import os
import random
import re
import time
import pdfkit
import requests
from wxpy import *


def group_tian_tian(groups):
	'''groups should be one Chat object or a list concluding
			several Chat objects.
		if the owner of one of the Chat objects is abin,then 
			return that object'''
	qun=0
	for l in groups:
		if l.owner.name=='xx'and len(l)==9:
			qun=l
			break
	return qun

#下载图片
def save_pict(url,picture_name):
	try:
		head={
			'user-agent':'MQQBrowser/26 Mozilla/5.0 \
			(Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; \
			CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) \
			Version/4.0 Mobile Safari/533.1'
		}
		html=requests.get(url,timeout=7,headers=head)
		time.sleep(1)

		with open(os.getcwd+'\\png\\'+picture_name,'b') as f:
			f.write(html.content)
	except:
		return 'Error'


def get_html_text(url):
	try:
		head={
			'user-agent':'MQQBrowser/26 Mozilla/5.0 \
			(Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; \
			CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) \
			Version/4.0 Mobile Safari/533.1'
		}
		html=requests.get(url,timeout=7,headers=head)
		time.sleep(1)
		html.encoding=html.apparent_encoding
		return html.text
	except:
		return 

class TopToggle():
	def __init__(self):
		self.top_toggle='1'


save_path=r'D:\python\weixin\articles'
if os.path.exists(save_path) and os.path.isdir(save_path):
	pass
else:
	os.mkdir(save_path)

#过滤不想下载的链接
regx=re.compile(r'.*(ele\.me).*hardware')
#匹配好友将不自动回复
regx_cancel=re.compile('关闭好友[:：](.*)')

pict_path=os.getcwd()+'\\png\\'
#sys.stdin=io.TextIOWrapper(sys.stdin.buffer,encoding='utf-8')
#sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')


bot = Bot(cache_path=True)
bot.enable_puid('wxpy_puid.pkl')  #启用puid标识对象，并指定文件表存数据

myself = bot.self
#my_friend = ensure_one(bot.search('天天'))
my_friend=group_tian_tian(bot.groups())
tuling = Tuling(api_key='19c532fec33946ca809bb393f5bc9e22')

release_come_out=0

#bot.file_helper.send('Hello from wxpy!')
@bot.register(my_friend)
def reply_my_friend(msg):
	global release_come_out
	toggle=1
	bot_off=re.compile(r'xx闭嘴(.*)')
	if msg.type=='Picture' and release_come_out>=50:
		msg.reply_image(os.getcwd()+'\\png\\a.png')
		toggle=0
	custom_text=['出来透口气','嗯哼','又见面了','想我了吗']
	if bot_off.match(msg.text):
		msg.reply('好吧')
		release_come_out=0
	elif msg.text=='xx出来':
		release_come_out=50
	elif release_come_out==59:
		msg.reply(random.sample(custom_text,1)[0])
	if release_come_out>=50 and toggle==1:
		tuling.do_reply(msg)
	else:
		release_come_out+=1



my_mother=bot.friends().search('xx')[0]
@bot.register(my_mother)
def reply_my_mother(msg):
	l=0
	for l in bot.messages:
		if l.memeber.chat.name=='麻麻':
			number+=1
	if number==1:
		reply_content='在学习哦\n----我是机器人xxx'
	elif number ==2:
		reply_content='他一般在吃饭时间前后或睡前会看微信'
	elif number>6:
		reply_content='很急的话就打电话吧---178xxxxxx'
	return reply_content


others=[]
others_exclude=[]
keywords_exclu=['麻麻','xxx']
for n in keywords_exclu:
	others_exclude.extend(bot.friends().search(n))
others = bot.friends()
others.append(bot.file_helper)
options = {
	'images':None,
	'javascript-delay':'100',
	'no-stop-slow-scripts':None
}

#全局变量，用于控制
friend_others={x:0 for x in others}
for n in others_exclude:
	friend_others[n] = -9999
top_on_off = TopToggle() #上帝开关


@bot.register(others,except_self=False)
def reply_my_friends(msg):
	try:
		global friend_others
		#global top_toggle  用类代替比global更安全
		#global friend_others_toggle  多余，优化去除

		if msg.receiver == bot.file_helper and msg.type == 'Text':
			if msg.text == '0':
				top_on_off.top_toggle = msg.text
			elif msg.text == '1':
				top_on_off.top_toggle = msg.text
			elif re.match(regx_cancel,msg.text):
				try:
					cancel_friend = bot.friends().search(re.match(
						regx_cancel,msg.text).group(1))[0]
					friend_others[cancel_friend] = -9999
					return cancel_friend.name+'will not be replied automatically'
				except:
					return 'No such a friend'

		if top_on_off.top_toggle == '0':
			return

		if msg.type == 'Sharing' and msg.receiver == bot.file_helper:
			article_name=msg.text.strip()
			article_path=save_path+'\\'+article_name+'.pdf'
			if re.search(regx,msg.url) or os.path.exists(article_path):
				return '没用的文章或者已经保存过了'
			else:
				try:
					html_text=get_html_text(msg.url)
					if not html_text:
						return 'Error about html'
					replace=html_text.replace('data-src','src')
					#replace绕过腾讯对图片的保护
					pdfkit.from_string(replace,article_path,options=options)
					return 'ok'
				except IOError as e:
					#因为html里引用了css之类会导致wkhtmltopdf有ioerror，但没发现对结果有影响
					return e
		#关闭自动回复
		if msg.text == '0':
			friend_others[msg.sender] = -9999
		elif msg.text == '1':
			friend_others[msg.sender] = 0

		if msg.type == 'Picture' and friend_others[msg.sender] >0:
			select_pict=random.choice(os.listdir(os.getcwd()+'\\png'))
			msg.reply_image(os.getcwd()+'\\png\\'+select_pict)
			return

		friend_others[msg.sender] += 1
		if friend_others[msg.sender] == 1:
			msg.reply('他一般十二点和下午六点左右会留意微信.\
				\n有急事请call电话178xxxxxxxx\n\t---机器人xx')
		elif friend_others[msg.sender] == 2:
			msg.reply('不想机器人说话，请输入数字0；若再输入1，我就又出来啦')
		if friend_others[msg.sender] > 2:
			tuling.do_reply(msg)
	except:
		print('Error')
		bot.file_helper.send('Error')
		raise

embed()
#Bot.logout()

#表情可以在cmd是乱码，可以先解码辨认,再转码即可，如下
#bot.file_helper.send(bot.messages[0].chat.members[-8].name.encode('utf-8').decode('utf-8'))