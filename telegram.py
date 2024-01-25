import requests
import config

def sendTelegram(message, group):

    if group == '3-10':
        requests.post(f'https://api.telegram.org/bot{config.bot_token}/sendMessage?chat_id={config.chat_id_3_10}&text={message}')
    elif group == '10-20':
        requests.post(f'https://api.telegram.org/bot{config.bot_token}/sendMessage?chat_id={config.chat_id_10_20}&text={message}')
    elif group == '20-50':
        requests.post(f'https://api.telegram.org/bot{config.bot_token}/sendMessage?chat_id={config.chat_id_20_50}&text={message}')
    elif group == '+50':
        requests.post(f'https://api.telegram.org/bot{config.bot_token}/sendMessage?chat_id={config.chat_id_50}&text={message}')
    elif group == 'volat':
        requests.post(f'https://api.telegram.org/bot{config.bot_token}/sendMessage?chat_id={config.volat}&text={message}')
    elif group == 'fiat':
        requests.post(f'https://api.telegram.org/bot{config.bot_token}/sendMessage?chat_id={config.fiat}&text={message}')


def sendTelegramArbitrageBotOk(message):
    requests.post(f'https://api.telegram.org/bot{config.bot_token}/sendMessage?chat_id={config.dev}&text={message}')
