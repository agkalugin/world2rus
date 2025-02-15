{\rtf1\ansi\ansicpg1251\cocoartf2821
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import os\
from aiogram import Bot, Dispatcher, types\
from aiogram.utils import executor\
\
# \uc0\u1055 \u1086 \u1083 \u1091 \u1095 \u1072 \u1077 \u1084  \u1090 \u1086 \u1082 \u1077 \u1085  \u1080 \u1079  \u1087 \u1077 \u1088 \u1077 \u1084 \u1077 \u1085 \u1085 \u1099 \u1093  \u1086 \u1082 \u1088 \u1091 \u1078 \u1077 \u1085 \u1080 \u1103 \
TOKEN = os.getenv("BOT_TOKEN")\
\
bot = Bot(token=TOKEN)\
dp = Dispatcher(bot)\
\
@dp.message_handler(commands=['start'])\
async def start(message: types.Message):\
    await message.answer("\uc0\u1055 \u1088 \u1080 \u1074 \u1077 \u1090 ! \u1054 \u1090 \u1087 \u1088 \u1072 \u1074 \u1100  \u1089 \u1089 \u1099 \u1083 \u1082 \u1091  \u1085 \u1072  \u1090 \u1086 \u1074 \u1072 \u1088 .")\
\
@dp.message_handler()\
async def handle_order(message: types.Message):\
    # \uc0\u1055 \u1088 \u1080 \u1084 \u1077 \u1088  \u1086 \u1090 \u1087 \u1088 \u1072 \u1074 \u1082 \u1080  \u1091 \u1074 \u1077 \u1076 \u1086 \u1084 \u1083 \u1077 \u1085 \u1080 \u1103  \u1072 \u1076 \u1084 \u1080 \u1085 \u1091 \
    admin_id = 123456789  # \uc0\u1047 \u1072 \u1084 \u1077 \u1085 \u1080  \u1085 \u1072  \u1089 \u1074 \u1086 \u1081  ID\
    await bot.send_message(admin_id, f"\uc0\u1053 \u1086 \u1074 \u1099 \u1081  \u1079 \u1072 \u1082 \u1072 \u1079 :\\n\{message.text\}")\
    await message.answer("\uc0\u1042 \u1072 \u1096  \u1079 \u1072 \u1082 \u1072 \u1079  \u1087 \u1088 \u1080 \u1085 \u1103 \u1090 ! \u1057 \u1087 \u1072 \u1089 \u1080 \u1073 \u1086 .")\
\
if __name__ == '__main__':\
    executor.start_polling(dp, skip_updates=True)}