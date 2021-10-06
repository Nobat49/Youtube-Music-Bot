from aiogram import Bot, Dispatcher, executor, types
from pytube import Search, YouTube, exceptions
from os import rename, remove
from asyncio import sleep
from time import strftime
import logging

logging.basicConfig(level=logging.INFO, filename='logs.log',
                    format=f'{strftime("%c")} - %(levelname)s - %(message)s')


class Downloader:
    @staticmethod
    def search(request):
        search_results = Search(request)
        return search_results.results[0]

    @staticmethod
    def download(youtube_object):
        youtube_file = youtube_object.streams.filter(only_audio=True, abr="128kbps")[0]
        path = youtube_file.download()
        audio_file = path.replace('mp4', 'mp3')
        rename(path, audio_file)
        return audio_file


class BotBody(Downloader):
    _api_token = # ТОКЕН
    if not _api_token:
        exit("Ошибка, отсутствует токен")
    _bot = Bot(token=_api_token, parse_mode=types.ParseMode.HTML)
    dp = Dispatcher(_bot)

    @dp.message_handler(commands=['start', 'help', 'info'])
    async def helping(self, message: types.Message):
        await message.answer("""Данный бот помогает легко находить треки и добавлять их в свою библиотеку Телеграм
Для того что бы найти трек, нужно написать комманду /find и указать название или ссылку на трек с youtube""")

    @dp.message_handler(commands=['find'])
    async def finder(message: types.Message):

        text = message.text

        if text == '/find':
            await message.reply('Трек указан неверно')
            return
        else:
            request = text.replace('/find ', '')

        if 'youtube.com/watch?v=' in text or 'youtu.be/' in text:
            try:
                youtube = YouTube(request)
            except exceptions.RegexMatchError:
                await message.reply('Трек указан неверно')
                return
        else:
            youtube = Downloader.search(request)

        if youtube.length >= 900:
            await message.reply('Трек превышает 15 минут')
            return

        audio_file = Downloader.download(youtube)

        with open(audio_file, 'rb') as file:
            await message.answer_audio(file)
            file.close()

        await sleep(5)
        remove(audio_file)


Messager = BotBody()

if __name__ == '__main__':
    executor.start_polling(Messager.dp, skip_updates=True)
