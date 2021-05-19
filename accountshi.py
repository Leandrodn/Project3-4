import serial
import mysql.connector
import hashlib
import tkinter as tk

database = mysql.connector.connect(host="remotemysql.com", user="5J9rC1RF8E", passwd="U8IIWXIJZT", db="5J9rC1RF8E")
cursor = database.cursor()
arduino2 = serial.Serial('COM3', 9600, timeout=.1)


def rfid():
    global output
    arduino = serial.Serial('COM9', 9600, timeout=.1)
    while True:
        data = arduino.readline()
        output = str(data, 'UTF-8')
        output.replace('b', '')
        if output:
            print(output)
            cursor.execute("SELECT iban FROM accounts WHERE iban = %s", (output,))
            iban = cursor.fetchall()
            return


def keypad():
    cursor.execute("SELECT pinCode FROM card, accounts WHERE accounts.iban = %s AND card.cardID = accounts.cardID"
                   , (output,))
    SQLpincodeList = cursor.fetchall()
    SQLpincode = SQLpincodeList[0]
    print(SQLpincode[0])
    print('Voer uw pincode in')

    pincodeList = []
    noOfTries = 0

    cursor.execute("SELECT vallid FROM card, accounts WHERE accounts.iban = %s AND card.cardID = accounts.cardID"
                   , (output,))
    cardStateList = cursor.fetchall()
    cardState = cardStateList[0]

    pincodeBox = tk.Entry(text='test', font=('Century Gothic', 30, 'bold'), fg='black')
    pincodeBox.place(x=730, y=640)
    if cardState[0] == 1:
        while True:
            keypad = arduino2.read()
            keypad = keypad.decode()
            if keypad:
                if len(pincodeList) == 3:
                    pincodeBox.insert(0, '*')
                    pincodeList.append(keypad)
                    pincode = ''.join(pincodeList)
                    hashed = hashlib.sha256(pincode.encode('utf8')).hexdigest()
                    print(hashed)
                    if hashed == SQLpincode[0]:
                        cursor.execute(
                            "UPDATE card SET noOfTries = 0 WHERE pinCode = %s"
                            , (SQLpincode[0],))
                        database.commit()
                        print('U bent succesvol ingelogd')
                        return True
                    else:
                        print('Pincodes komen niet overeen')
                        pincodeBox.delete(0, 'end')
                        pincodeList.clear()
                        noOfTries += 1
                        cursor.execute(
                            "UPDATE card SET noOfTries = %s WHERE pinCode = %s"
                            , (noOfTries, SQLpincode[0]))
                        database.commit()
                        print('Aantal pogingen: ', noOfTries)
                        if noOfTries >= 3:
                            print('Joejoe pas geblokkerd')
                            cursor.execute(
                                "UPDATE card SET vallid = 0 WHERE pinCode = %s"
                                , (SQLpincode[0],))
                            database.commit()
                            return False
                else:
                    pincodeBox.insert(0, '*')
                    pincodeList.append(keypad)
    else:
        print("uw pas is geblokkerd, neem contact op met de database meneer")


def amountKeypad():
    global amount

    amountBox = tk.Entry(text='test', font=('Century Gothic', 30, 'bold'), fg='black')
    amountBox.place(x=730, y=640)
    amountList = []

    amountBox.delete(0, 'end')
    while True:
        keypad = arduino2.read()
        keypad = keypad.decode()
        if keypad:
            if keypad == 'A':
                amountList.append(keypad)
                amount = ''.join(amountList)
                return
            else:
                amountBox.insert('end', keypad)
                amountList.append(keypad)


if __name__ == "__main__":
    rfid()
    keypad()
    amountKeypad()
