import os
import re
import logging
import paramiko
import psycopg2
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

load_dotenv()
token = os.getenv('TOKEN')

db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_username = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')

host = os.getenv('RM_HOST')
port = os.getenv('RM_PORT')
username = os.getenv('RM_USER')
password = os.getenv('RM_PASSWORD')

logging.basicConfig(filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')

def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    return 'findPhoneNumbers'

def findPhoneNumbers(update: Update, context):
    user_input = update.message.text

    phoneNumRegex1 = re.compile(r'8\d{10}') # формат 8XXXXXXXXXX
    phoneNumRegex2 = re.compile(r'8\(\d{3}\)\d{7}') # формат 8(XXX)XXXXXXX
    phoneNumRegex3 = re.compile(r'8 \d{3} \d{3} \d{2} \d{2}') # формат 8 XXX XXX XX XX
    phoneNumRegex4 = re.compile(r'8 \(\d{3}\) \d{3} \d{2} \d{2}') # формат 8 (XXX) XXX XX XX
    phoneNumRegex5 = re.compile(r'8-\d{3}-\d{3}-\d{2}-\d{2}') # формат 8-XXX-XXX-XX-XX
    phoneNumRegex6 = re.compile(r'\+7\d{10}') # формат +7XXXXXXXXXX
    phoneNumRegex7 = re.compile(r'\+7\(\d{3}\)\d{7}') # формат +7(XXX)XXXXXXX
    phoneNumRegex8 = re.compile(r'\+7 \d{3} \d{3} \d{2} \d{2}') # формат +7 XXX XXX XX XX
    phoneNumRegex9 = re.compile(r'\+7 \(\d{3}\) \d{3} \d{2} \d{2}') # формат +7 (XXX) XXX XX XX
    phoneNumRegex10 = re.compile(r'\+7-\d{3}-\d{3}-\d{2}-\d{2}') # формат +7-XXX-XXX-XX-XX

    phoneNumRegexes = [phoneNumRegex1, phoneNumRegex2, phoneNumRegex3, phoneNumRegex4, phoneNumRegex5, phoneNumRegex6, phoneNumRegex7, phoneNumRegex8, phoneNumRegex9, phoneNumRegex10]

    phoneNumberList = []
    for phoneNumRegex in phoneNumRegexes:
        matches = re.findall(phoneNumRegex, user_input)
        for match in matches:
            phoneNumberList.append(match)

    if not phoneNumberList:
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END
    
    phoneNumbersString = ""
    for i in range(len(phoneNumberList)):
        phoneNumbersString += f'{i+1}. {phoneNumberList[i]}\n'

    context.user_data['phoneCount'] = len(phoneNumberList)
    for i in range(len(phoneNumberList)):
        context.user_data[f'phone{i+1}'] = phoneNumberList[i]

    phoneNumbersString += "Хотите записать их в базу? (ДА или НЕТ)\n"
    update.message.reply_text(phoneNumbersString)

    return 'addPhonesInDB'

def addPhonesInDB(update: Update, context):
    user_input = update.message.text.upper()

    if user_input == 'ДА':
        try:
            connection = psycopg2.connect(user=db_username, password=db_password, host=db_host, port=db_port, database=db_name)
            cursor = connection.cursor()
            for i in range(context.user_data.get('phoneCount', 0)):
                phoneNumber = context.user_data.get(f'phone{i+1}', 'phoneERROR')
                cursor.execute(f"INSERT INTO phones(phone) VALUES ('{phoneNumber}');")
            connection.commit()
            update.message.reply_text('Записи успешно добавлены в базу')
        except Exception as error:
            logger.error(f'{error}')
            update.message.reply_text(f'Ошибка: {error}')
        finally:
            return ConversationHandler.END
        
    update.message.reply_text('Записи не были добавлены в базу')
    return ConversationHandler.END

def findEmailsCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска e-mail адресов: ')
    return 'findEmails'

def findEmails(update: Update, context):
    user_input = update.message.text

    emailRegex = re.compile(r'\b[A-Za-z0-9_.]+@[A-Za-z0-9]+\.[A-Za-z]{2,}\b')
    emails = re.findall(emailRegex, user_input)

    if not emails:
        update.message.reply_text('Email адреса не найдены')
        return ConversationHandler.END
    
    emailsString = ""
    for i in range(len(emails)):
        emailsString += f'{i+1}. {emails[i]}\n'

    context.user_data['emailCount'] = len(emails)
    for i in range(len(emails)):
        context.user_data[f'email{i+1}'] = emails[i]

    emailsString += "Хотите записать их в базу? (ДА или НЕТ)\n"
        
    update.message.reply_text(emailsString)

    return 'addEmailsInDB'

def addEmailsInDB(update: Update, context):
    user_input = update.message.text.upper()

    if user_input == 'ДА':
        try:
            connection = psycopg2.connect(user=db_username, password=db_password, host=db_host, port=db_port, database=db_name)
            cursor = connection.cursor()
            for i in range(context.user_data.get('emailCount', 0)):
                mail = context.user_data.get(f'email{i+1}', 'emailERROR')
                cursor.execute(f"INSERT INTO emails(mail) VALUES ('{mail}');")
            connection.commit()
            update.message.reply_text('Записи успешно добавлены в базу')
        except Exception as error:
            logger.error(f'{error}')
            update.message.reply_text(f'Ошибка: {error}')
        finally:
            return ConversationHandler.END
        
    update.message.reply_text('Записи не были добавлены в базу')
    return ConversationHandler.END

def checkPasswordCommand(update: Update, context):
    update.message.reply_text('Введите пароль для проверки на сложность: ')
    return 'checkPassword'

def checkPassword(update: Update, context):
    user_input = update.message.text

    passwordRegex = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()]).{8,}$')

    if re.match(passwordRegex, user_input):
        update.message.reply_text('Пароль сложный')
    else:
        update.message.reply_text('Пароль простой')
    
    return ConversationHandler.END

def realeseInfoCommand(update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('lsb_release -a')
    data = stdout.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]

    update.message.reply_text(data)

def archNameKurnelVersInfoCommand(update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('echo "Architecture: $(uname -m), Hostname: $(hostname), Kernel version: $(uname -r)"')
    data = stdout.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]

    update.message.reply_text(data)

def timeOfWorkInfoCommand(update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('uptime -p')
    data = stdout.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]

    update.message.reply_text(data)

def fileSystemInfoCommand(update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('df -h')
    data = stdout.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]

    update.message.reply_text(data)

def ramInfoCommand(update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('free -h')
    data = stdout.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]

    update.message.reply_text(data)

def mpstatInfoCommand(update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('mpstat')
    data = stdout.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]

    update.message.reply_text(data)

def usersInfoCommand(update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('w')
    data = stdout.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]

    update.message.reply_text(data)

def authInfoCommand(update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('last -n 10')
    data = stdout.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]

    update.message.reply_text(data)

def criticalInfoCommand(update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('journalctl -p crit -n 5')
    data = stdout.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]

    update.message.reply_text(data)

def psInfoCommand(update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('ps aux | head -n 10')
    data = stdout.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]

    update.message.reply_text(data)

def portsInfoCommand(update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('netstat -tulnp')
    data = stdout.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]

    update.message.reply_text(data)

def aptInfoCommand(update: Update, context):
    update.message.reply_text('Введите название пакета или ВСЕ: ')

    return 'aptInfo'

def aptInfo(update: Update, context):

    user_input = update.message.text
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)

    if user_input == 'ВСЕ':
        stdin, stdout, stderr = client.exec_command('dpkg -l | head -n 10')
    else:
        stdin, stdout, stderr = client.exec_command(f'dpkg -l | grep {user_input}')

    data = stdout.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]

    update.message.reply_text(data)
    
    return ConversationHandler.END

def servicesInfoCommand(update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('systemctl list-units --type=service | head -n 10')
    data = stdout.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]

    update.message.reply_text(data)

def getReplLogsCommand(update: Update, context):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=username, password=password, port=port)
        stdin, stdout, stderr = client.exec_command('grep "replication" /var/log/postgresql/postgresql-14-main.log | tail -n 20')
        data = stdout.read()
        client.close()
        data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
        update.message.reply_text(data)
    except Exception as error:
        logger.error(f'{error}')
        update.message.reply_text(f'Ошибка: {error}')

def getEmailsCommand(update: Update, context):
    try:
        connection = psycopg2.connect(user=db_username, password=db_password, host=db_host, port=db_port, database=db_name)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM emails;")
        data = cursor.fetchall()
        outputString = ""
        for row in data:
           outputString += str(row) + "\n"
        update.message.reply_text(outputString)
    except Exception as error:
        logger.error(f'{error}')
        update.message.reply_text(f'Ошибка: {error}')

def getPhoneNumbersCommand(update: Update, context):
    try:
        connection = psycopg2.connect(user=db_username, password=db_password, host=db_host, port=db_port, database=db_name)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM phones;")
        data = cursor.fetchall()
        outputString = ""
        for row in data:
            outputString += str(row) + "\n"
        update.message.reply_text(outputString)
    except Exception as error:
        logger.error(f'{error}')
        update.message.reply_text(f'Ошибка: {error}')

def echo(update: Update, context):
    update.message.reply_text(update.message.text)

def main():
    updater = Updater(token, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчики диалога
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            'addPhonesInDB': [MessageHandler(Filters.text & ~Filters.command, addPhonesInDB)]
        },
        fallbacks=[]
    )

    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailsCommand)],
        states={
            'findEmails': [MessageHandler(Filters.text & ~Filters.command, findEmails)],
            'addEmailsInDB': [MessageHandler(Filters.text & ~Filters.command, addEmailsInDB)]
        },
        fallbacks=[]
    )

    convHandlerCheckPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', checkPasswordCommand)],
        states={
            'checkPassword': [MessageHandler(Filters.text & ~Filters.command, checkPassword)],
        },
        fallbacks=[]
    )

    convHandlerAptList = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', aptInfoCommand)],
        states={
            'aptInfo': [MessageHandler(Filters.text & ~Filters.command, aptInfo)],
        },
        fallbacks=[]
    )

		
    dp.add_handler(CommandHandler("start", start))

    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmails)
    dp.add_handler(convHandlerCheckPassword)

    dp.add_handler(CommandHandler("get_release", realeseInfoCommand))
    dp.add_handler(CommandHandler("get_uname", archNameKurnelVersInfoCommand))
    dp.add_handler(CommandHandler("get_uptime", timeOfWorkInfoCommand))

    dp.add_handler(CommandHandler("get_df", fileSystemInfoCommand))
    dp.add_handler(CommandHandler("get_free", ramInfoCommand))
    dp.add_handler(CommandHandler("get_mpstat", mpstatInfoCommand))
    dp.add_handler(CommandHandler("get_w", usersInfoCommand))

    dp.add_handler(CommandHandler("get_auths", authInfoCommand))
    dp.add_handler(CommandHandler("get_critical", criticalInfoCommand))

    dp.add_handler(CommandHandler("get_ps", psInfoCommand))
    dp.add_handler(CommandHandler("get_ss", portsInfoCommand))
    dp.add_handler(convHandlerAptList)
    dp.add_handler(CommandHandler("get_services", servicesInfoCommand))

    dp.add_handler(CommandHandler("get_repl_logs", getReplLogsCommand))
		
    dp.add_handler(CommandHandler("get_emails", getEmailsCommand))
    dp.add_handler(CommandHandler("get_phone_numbers", getPhoneNumbersCommand))
    
	# Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
		
	# Запускаем бота
    updater.start_polling()

	# Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()