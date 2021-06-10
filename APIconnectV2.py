import serial
import hashlib
import tkinter as tk
import requests
import smtplib
import time
from datetime import date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas
from datetime import datetime

global charityChoice

amount = 0
arduino2 = serial.Serial('COM3', 9600, timeout=.1)
arduino3 = serial.Serial('COM4', 9600, writeTimeout=0)


def startArduino():
    if arduino2.isOpen() == False:
        arduino2.open()
        arduino3.open()


def rfid():
    global output
    arduino = serial.Serial('COM6', 9600, timeout=.1)
    while True:
        data = arduino.readline()
        output = str(data, 'UTF-8')
        output.replace('b', '')
        if output:
            cardState = requests.post('http://145.24.222.243:8050/checkIfRegistered', data={'IBAN': output}).status_code
            if cardState == 208:
                print(output)
                return True
            elif cardState == 434:
                print("Uw pas is geblokkerd")
                popUp('Card Blocked', 'Card is blocked')
                return False
            elif cardState == 433:
                popUp('Card Unknown', 'Card not registered')
                print("Account niet geregistreed")
                return False
            elif cardState == 432:
                popUp('JSON WRONG', 'internal server error')
                return False
            else:
                return False


def keypad():
    print('Voer uw pincode in')

    pincodeList = []

    pincodeBox = tk.Entry(text='', font=('Century Gothic', 30, 'bold'), fg='black')
    pincodeBox.place(x=730, y=640)
    pincodeBox.delete(0, 'end')

    noOfTriesStart = requests.post('http://145.24.222.243:8050/checkAttempts',
                                   data={'IBAN': output})
    noOfTriesBox = tk.Entry(text='', font=('Century Gothic', 30, 'bold'), fg='black', width=5)
    noOfTriesBox.place(x=1150, y=870)
    if len(noOfTriesStart.text) > 2:
        noOfTriesBox.insert(0, noOfTriesStart.text[1])
    else:
        noOfTriesBox.insert(0, noOfTriesStart.text)
    noOfTriesBox.config(state=tk.DISABLED)
    keypad = ""
    keypadList = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}
    while True:
        keypad = arduino2.read()
        keypad = keypad.decode()
        if keypad in keypadList:
            if len(pincodeList) >= 3:
                pincodeBox.insert(0, '*')
                pincodeList.append(keypad)
                pincode = ''.join(pincodeList)
                hashedPin = hashlib.sha256(pincode.encode('utf8')).hexdigest()
                print(hashedPin)
                APIpin = requests.post('http://145.24.222.243:8050/login',
                                       data={'IBAN': output, 'pincode': hashedPin}).status_code
                if APIpin == 208:
                    print('U bent succesvol ingelogd')
                    return True
                elif APIpin == 435:
                    popUp('Pincode invalid', 'Your pincodes dont match')
                    print('Pincodes komen niet overeen')
                    pincodeBox.delete(0, 'end')
                    pincodeList.clear()

                    noOfTries = requests.post('http://145.24.222.243:8050/checkAttempts',
                                              data={'IBAN': output})
                    print('Aantal pogingen over: ', noOfTries.text)

                    noOfTriesBox.config(state=tk.NORMAL)
                    noOfTriesBox.delete(0, 'end')
                    if len(noOfTries.text) > 2:
                        noOfTriesBox.insert(0, noOfTries.text[1])
                    else:
                        noOfTriesBox.insert(0, noOfTries.text)
                    noOfTriesBox.config(state=tk.DISABLED)

                elif APIpin == 434:
                    pincodeBox.delete(0, 'end')
                    pincodeList.clear()
                    pincodeBox.config(state=tk.DISABLED)
                    popUp('Pincode invalid', 'Number of tries left exceeded, Card blocked')
                    print('Joejoe pas geblokkerd')
                    return False
            else:
                pincodeBox.insert(0, '*')
                pincodeList.append(keypad)
        else:
            if keypad == '*':
                return False
            else:
                pass


def amountKeypad():
    global amount

    amountBox = tk.Entry(text='test', font=('Century Gothic', 30, 'bold'), fg='black')
    amountBox.place(x=730, y=640)
    amountList = []
    amountBox.delete(0, 'end')
    numbers = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}
    while True:
        keypad = arduino2.read()
        keypad = keypad.decode()
        if keypad:
            if keypad == 'A':
                amount = ''.join(amountList)
                print(amount)
                amount = int(amount)
                if amount % 10 == 0:
                    amountState = requests.post('http://145.24.222.243:8050/checkBalance',
                                                data={'IBAN': output})
                    if amountState.status_code == 209:
                        if float(amountState.text.replace("'", "").replace('\n', '').replace('"', '').replace("\\",
                                                                                                              "").replace(
                            "n", "")) > amount and amount < 500:
                            return 0
                        elif float(amountState.text.replace("'", "").replace('\n', '').replace('"', '').replace("\\",
                                                                                                                "").replace(
                            "n", "")) < amount:
                            print("Niet genoeg geld")
                            popUp('Balance', 'Not enough balance')
                            amountList.clear()
                            amountBox.delete(0, 'end')

                        elif amount >= 500:
                            popUp('Invalid amount', 'This ATM has a max of 490')
                            amountList.clear()
                            amountBox.delete(0, 'end')
                    elif amountState.status_code == 432:
                        popUp('JSON WRONG', 'internal server error')
                    elif amountState.status_code == 436:
                        print("Niet ingelogd")
                        popUp('Login Error', 'Not logged in')
                        return 3

                else:
                    amountList.clear()
                    popUp('Invalid Amount', 'The amount is invalid, choose a number that ends with a zero')
                    amountBox.delete(0, 'end')
            elif keypad == '*':
                return 1
            elif keypad == '#':
                return 2
            elif keypad in numbers:
                amountBox.insert('end', keypad)
                amountList.append(keypad)


def fastAmount():
    amountState = requests.post('http://145.24.222.243:8050/checkBalance',
                                data={'IBAN': output})
    if amountState.status_code == 209:
        if float(amountState.text.replace("'", "").replace('\n', '').replace('"', '').replace("\\", "").replace("n",
                                                                                                                "")) > amount:
            return 0
        else:
            popUp('Balance', 'Not enough balance')
            return 2
    elif amountState.status_code == 432:
        popUp('JSON WRONG', 'internal server error')
    elif amountState.status_code == 436:
        print("Niet ingelogd")
        popUp('Login Error', 'Not logged in')
        return 1


def bills():
    global notes
    global notes50
    global notes20
    global notes10
    notes50 = 0
    notes20 = 0
    notes10 = 0

    if amount % 10 == 0:
        notes50 = amount // 50
        notes20 = ((amount - (notes50 * 50)) // 20)
        notes10 = ((amount - (notes50 * 50) - (notes20 * 20)) // 10)
        print("briefjes van 50 ", notes50)
        print("briefjes van 20 ", notes20)
        print("briefjes van 10 ", notes10)
        notes = f"{notes50}x 50,-, {notes20}x 20,-, {notes10}x 10,- [A]"
        return True
    else:
        print("kan niet")
        return False


def balance():
    APIbalance = requests.post('http://145.24.222.243:8050/checkBalance',
                               data={'IBAN': output})
    balance = ''
    balanceBox = tk.Entry(textvariable=balance, font=('Century Gothic', 30, 'bold'), fg='black')
    balanceBox.delete(0, 'end')
    if APIbalance.status_code == 209:
        balance = APIbalance.text.replace('"', '').replace("\\", "").replace("n", "").replace("'", "").replace('\n', '')
        balanceBox.insert("end", balance)
        balanceBox.config(state='readonly')
        balanceBox.place(x=1100, y=500)
        return balance
    elif APIbalance.status_code == 436:
        popUp('login error', 'U are not logged in')
        print("niet ingelogd")


def withdraw():
    amountState = requests.post('http://145.24.222.243:8050/withdraw',
                                data={'IBAN': output, 'amount': amount}).status_code
    if amountState == 208:
        return 0
    elif amountState == 436:
        print("Niet ingelogd")
        popUp('Login Error', 'Not logged in')
        return 1
    elif amountState == 432:
        popUp('JSON WRONG', 'internal server error')


def charity():
    if charityChoice == 1:
        APIcharity = requests.post('http://145.24.222.243:8050/transfer', data={'IBAN': output,
                                                                                'targetIBAN': 'NI46ABNA41125139',
                                                                                'amount': amount})


def APIlogout():
    while True:
        APIlogout = requests.post('http://145.24.222.243:8050/logout', data={'IBAN': output}).status_code
        if APIlogout == 208:
            print("U bent succesvol uitgelogd")
            break


def popUp(title, text):
    top = tk.Toplevel()
    top.title(title)
    tk.Message(top, text=text, padx=20, pady=20, font=('Century Gothic', 30, 'bold')).pack()
    top.after(2000, top.destroy)


def transactionNo():
    global transNo
    with open('transNo.txt', 'r+') as f:
        transNo = int(str(f.read()))
        print(transNo)
        f.seek(0)
        f.truncate(0)
        transNo += 1
        f.write(str(transNo))
        f.close()


def digitalReceipt():
    APIreceipt = requests.post('http://145.24.222.243:8050/receipt', data={'IBAN': output}).text
    receiptInfoList = list(eval(APIreceipt))  # element 0 = transID, 1 = cardId, 2 = email
    now = datetime.now()
    iban = output[-4:]

    # dd/mm/YY H:M:S
    date_str = now.strftime("%d/%m/%Y")
    time_str = now.strftime("%H:%M")

    canvas = Canvas(f"TransactionReceipt-{transNo}.pdf", pagesize=A4)
    canvas.drawImage("images/logov2.png", 2.5 * inch, 9.25 * inch)
    canvas.drawString(1 * inch, 9 * inch,
                      '-----------------------------------------------------------------------------'
                      '------------------------------------')
    canvas.drawString(1 * inch, 8.75 * inch,
                      'Date:' + date_str + '                                                           '
                                           '                              Time: ' + time_str)
    canvas.drawString(1 * inch, 8.5 * inch,
                      '-----------------------------------------------------------------------------'
                      '------------------------------------')
    canvas.drawString(1 * inch, 8.25 * inch, 'ATM #: 88')
    canvas.drawString(1 * inch, 8 * inch, f'Transaction #: {transNo}')
    canvas.drawString(1 * inch, 7.75 * inch, f'Iban #: XXXX-XXXX-XXXX-{iban}')
    canvas.drawString(1 * inch, 7.5 * inch, f'Card #: {receiptInfoList[1]}')
    canvas.drawString(1 * inch, 7.25 * inch, f'Amount: {amount},-')
    if charityChoice == 0:
        canvas.drawString(1 * inch, 7 * inch, f'Type: withdraw')
    else:
        canvas.drawString(1 * inch, 7 * inch, f'Type: Charity')
    canvas.drawString(1 * inch, 6.75 * inch,
                      '-----------------------------------------------------------------------------'
                      '------------------------------------')
    canvas.drawString(1 * inch, 6.5 * inch, 'Thank you for using the service of ABN-MANBRO')
    canvas.drawString(1 * inch, 6.25 * inch, 'Have a nice day!')
    canvas.save()

    email_user = 'ABNMANBRO@gmail.com'
    email_password = 'Timmerman?88'
    email_send = receiptInfoList[2]

    subject = 'Transactiebon'

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = email_send
    msg['Subject'] = subject

    body = 'Dear customer,\nThank you for your transaction at ABN-MANBRO.\nYou will find your receipt in the attachment.\nHave a nice day!\n\nKind regards,\nABN-MANBRO'
    msg.attach(MIMEText(body, 'plain'))

    filename = f'TransactionReceipt-{transNo}.pdf'
    attachment = open(filename, 'rb')

    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= " + filename)

    msg.attach(part)
    text = msg.as_string()
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email_user, email_password)

    server.sendmail(email_user, email_send, text)

    server.quit()


def printReceipt():
    popUp('RECEIPT', 'May take a while')
    sendChoice(2)
    # Get time
    now = datetime.now()
    currentTime = now.strftime("%H:%M")
    # Get date
    today = date.today()
    currentDay = today.strftime("%d-%m-%Y")
    currentTransaction = transNo
    currentAccount = output
    currentCard = output[-3:]
    currentAmount = amount
    while True:
        outputChoice = "d," + currentDay
        writeOut(outputChoice)
        outputChoice = "t," + currentTime
        writeOut(outputChoice)
        outputChoice = "o," + str(currentTransaction)
        writeOut(outputChoice)
        outputChoice = "a," + str(currentAccount[-4:])
        writeOut(outputChoice)
        outputChoice = "c," + str(currentCard)
        writeOut(outputChoice)
        outputChoice = "h," + str(currentAmount)
        writeOut(outputChoice)
        break
    print('ik ben klaar')
    return


def sentNotes():
    print('fawaka')
    sendChoice(1)
    print('broeder')
    while True:
        outputChoice = "q," + str(notes50) + "," + str(notes20) + "," + str(notes10)
        for i in range(4):
            writeOut(outputChoice)
        break


def writeOut(x):
    print("x: ", x)
    outputChoice = x
    outputBytes = str.encode(outputChoice)
    arduino3.write(outputBytes)
    time.sleep(1)


def sendChoice(choice):
    temp = 9
    if choice == 1:
        outputChoice = 'm'
    elif choice == 2:
        outputChoice = 'r'
    while (True):

        for i in range(4):
            print("output: ", outputChoice)
            writeOut(outputChoice)

        break


def endArduino():
    if arduino2.isOpen() == True:
        arduino2.close()
        arduino3.close()