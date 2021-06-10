from flask import Flask
from flask_restful import Resource, Api, reqparse
import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb
import datetime
import requests

app = Flask(__name__)
api = Api(app)

db = MySQLdb.connect(host='145.24.222.243', port=8051, user="1009652", passwd="timmerman123", db="ABNMANBRO")

cursor = db.cursor()

loginTime = {}

#adds the iban and login time to the dictionary of login times
def addLoginTime(key, value):
    loginTime[key] = value

#checks if the iban is loged in, and after that checks if more than two minutes have passed,
#if so, they are logged out, otherwise the current time is added as login time.
def checkLoginTime(key):
    if(loginTime.get(key)):
        logoutTime = loginTime.get(key) + datetime.timedelta(minutes = 2)

        if datetime.datetime.now() < logoutTime:
            addLoginTime(key, datetime.datetime.now())
        else:
            del loginTime[key]
            query = "UPDATE accounts SET login = 0 WHERE iban = %s;"
            cursor.execute(query, key)
            db.commit()

#logs everyone out
def logoutEveryone():
    query = "UPDATE accounts SET login = 0"
    cursor.execute(query)
    db.commit()

#checks if the account of the iban is blocked
def isAccountValid(dataInput):
    query = "SELECT valid FROM card WHERE cardID = (SELECT cardID FROM accounts WHERE iban = %s);"
    cursor.execute(query, dataInput)
    return cursor.fetchone()[0]

#checks if the iban is logged in on the database
def isLoggedIn(dataInput):
    query = "SELECT login FROM accounts WHERE iban = %s;"
    cursor.execute(query, dataInput)
    return cursor.fetchone()[0]

#checks if the iban belongs to ABN-MANBRO or not
def checkBank(dataInput):
    countryCode = dataInput[4:8]
    if countryCode == 'ABNA':
        return True
    else:
        return False

#first checks if the request if for out bank, then checks if the iban is registered with our bank and adds the login time, if so it checks if the card is blocked
#returns 208 if account is registered, 432 if there is a json fault, 433 if not registered and 434 if account is blocked. If the request is not for
#our API, it is forwarded to the country server.
class CheckIfRegistered(Resource): # POST
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('IBAN', required=True)
        args = parser.parse_args()
        try:
            dataInput = str(args.get('IBAN'))
            if(checkBank(dataInput)):
                checkLoginTime(dataInput)
                query = "SELECT firstName FROM customer WHERE customerID = (SELECT customerID FROM accounts WHERE iban = %s);"
                cursor.execute(query, dataInput)
                iban = cursor.fetchone()

                if(iban):
                    if(isAccountValid(dataInput)):
                        return 'OK', 208
                    else :
                        return 'Account blocked', 434
                else :
                    return 'Account not registered', 433
            else:
                response = requests.post('http://145.24.222.156:5001/checkIfRegistered', data={'IBAN': dataInput})
                return response.text, response.status_code
        except Exception as e:
            print(e)
            return 'Json wrong', 432

#firsts checks bank, then checks login time, then checks if account is valid, then checks if the pincode is correct, if not, it adds one to the amount of tries
#if it is correct, it sets the account to logged in and resets the amount of tries. If the amount of tries is 3, the account is blocked.
#returns 208 if everything is OK, 432 if there is a json fault, 434 if account is blocked and 435 if pincode is wrong. If the request is not for
#our API, it is forwarded to the country server.
class Login(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('IBAN', required=True)
        parser.add_argument('pincode', required=True)
        args = parser.parse_args()
        try:
            dataInput = str(args.get('IBAN'))
            if(checkBank(dataInput)):
                checkLoginTime(dataInput)
                query = "SELECT firstName FROM customer WHERE customerID = (SELECT customerID FROM accounts WHERE iban = %s);"
                cursor.execute(query, dataInput)
                iban = cursor.fetchone()

                if(iban):
                    if isAccountValid(dataInput):
                        query = "SELECT pinCode FROM card WHERE cardID = (SELECT cardID FROM accounts WHERE iban = %s);"
                        cursor.execute(query, dataInput)
                        pinCodeData = cursor.fetchone()

                        if(pinCodeData[0] == str(args.get('pincode'))):
                            query = "UPDATE accounts SET login = 1 WHERE iban = %s;"
                            cursor.execute(query, dataInput)
                            db.commit()
                            query = "UPDATE card SET noOfTries = 0 WHERE cardID = (SELECT cardID FROM accounts WHERE iban = %s);"
                            cursor.execute(query, dataInput)
                            db.commit()
                            addLoginTime(dataInput, datetime.datetime.now())
                            return 'OK', 208
                        else:
                            query = "SELECT noOfTries FROM card WHERE cardID = (SELECT cardID FROM accounts WHERE iban = %s);"
                            cursor.execute(query, dataInput)
                            noOfTries = int(cursor.fetchone()[0])
                            noOfTries += 1
                            dataInputTuple = (noOfTries, dataInput)
                            if noOfTries >= 3:
                                query = "UPDATE card SET noOfTries = %s, valid = 0 WHERE cardID = (SELECT cardID FROM accounts WHERE iban = %s);"
                                cursor.execute(query, dataInputTuple)
                                db.commit()
                                return 'Account blocked', 434
                            else :
                                query = "UPDATE card SET noOfTries = %s WHERE cardID = (SELECT cardID FROM accounts WHERE iban = %s);"
                                cursor.execute(query, dataInputTuple)
                                db.commit()
                                return 'Pincode wrong', 435
                    else :
                        return 'Account blocked', 434
                else:
                    return 'Account not registered', 433
            else:
                response = requests.post('http://145.24.222.156:5001/login', data={'IBAN': dataInput, 'pincode': str(args.get('pincode'))})
                return response.text, response.status_code

        except Exception as e:
            print(e)
            return 'Json wrong', 432

#first checks bank, and login time, if everything is correct returns the amount of triesleft, 208, and 432 if there is a json fault. If the request is not for
#our API, it is forwarded to the country server.
class CheckAttempts(Resource): # POST
    def post(self):
        parser = reqparse.RequestParser() 
        parser.add_argument('IBAN', required=True)
        args = parser.parse_args()
        try:
            dataInput = str(args.get('IBAN'))
            if(checkBank(dataInput)):
                checkLoginTime(dataInput)
                query = "SELECT noOfTries FROM card WHERE cardID = (SELECT cardID FROM accounts WHERE iban = %s);"
                cursor.execute(query, dataInput)
                noOfTries = int(cursor.fetchone()[0])
                triesLeft = 3 - noOfTries
                return triesLeft, 208
            else: 
                response = requests.post('http://145.24.222.156:5001/checkAttempts', data={'IBAN': dataInput})
                return response.text, response.status_code

        except Exception as e:
            print(e)
            return 'Json wrong', 432 # Bad request

#first checks if the amount is a valid number (not negative), then checks the bank and the login time, then checks if the iban is logged in and will
#check if the balance is high enough for the withdraw, then it will update the accout's balance and add the transaction to the database
#returns 208 if everything is OK, 437 if the balance is too low, 436 if iban is not logged in and 432 if there is a json fault.
class Withdraw(Resource): # POST
    def post(self):
        parser = reqparse.RequestParser() 
        parser.add_argument('IBAN', required=True)
        parser.add_argument('amount', required = True)
        args = parser.parse_args()
        try:
            if float(args.get('amount')) <= 0:
                raise ValueError()
            
            dataInput = str(args.get('IBAN'))
            if(checkBank(dataInput)):
                checkLoginTime(dataInput)

                if isLoggedIn(dataInput):
                    query = "SELECT balance FROM accounts WHERE iban = %s;"
                    cursor.execute(query, dataInput)
                    oldAmount = float(cursor.fetchone()[0])
                    newAmount = oldAmount - float(args.get('amount'))

                    if newAmount < 0:
                        return 'Balance too low', 437

                    
                    query = "UPDATE accounts SET balance = %s WHERE iban = %s;"
                    dataInputTuple = (newAmount, dataInput)
                    cursor.execute(query, dataInputTuple)
                    db.commit()

                    query = "SELECT MAX(transactionID) FROM transactions;"
                    cursor.execute(query)
                    transactionID = 1 + int(cursor.fetchone()[0])


                    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                    datInputTuple = (transactionID, dataInput, float(args.get('amount')), date)
                    query = 'INSERT INTO `transactions` (`transactionID`, `transactionType`, `iban`, `amount`, `transactionDate`) VALUES (%s, "withdraw", %s, %s, %s);'
                    cursor.execute(query, datInputTuple)
                    db.commit()
                    return 'OK', 208
                else:
                    return 'Not logged in', 436
            else:
                response = requests.post('http://145.24.222.156:5001/withdraw', data={'IBAN': dataInput, 'amount': str(args.get('amount'))})
                return response.text, response.status_code

        except Exception as e:
            print(e)
            return 'Json wrong', 432 # Bad request
    
#first checks bank, then checks login time, if the iban is logged in, it returns the balance, 209.
#returns 209 if everything is OK, 436 if not logged in and 432 if json is wrong.
class CheckBalance(Resource): # POST
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('IBAN', required=True)
        args = parser.parse_args()
        try:
            dataInput = str(args.get('IBAN'))
            if(checkBank(dataInput)):
                checkLoginTime(dataInput)

                if isLoggedIn(dataInput):
                    query = "SELECT balance FROM accounts WHERE iban = %s;"
                    cursor.execute(query, dataInput)
                    amount = float(cursor.fetchone()[0])
                    return amount, 209
                else :
                    return 'Not logged in', 436
            else:
                response = requests.post('http://145.24.222.156:5001/checkBalance', data={'IBAN': dataInput})
                return response.text, response.status_code

        except Exception as e:
            print(e)
            return 'Json wrong', 432 # Bad request

#first checks bank, then updates login time and sets the login on false in the database.
#returns 208 if everything OK, 432 if json fault.
class Logout(Resource): # POST
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('IBAN', required=True)
        args = parser.parse_args()
        try:
            dataInput = str(args.get('IBAN'))
            if(checkBank(dataInput)):
                checkLoginTime(dataInput)
                query = "UPDATE accounts SET login = 0 WHERE iban = %s;"
                cursor.execute(query, dataInput)
                db.commit()
                return 'OK', 208
            else:
                response = requests.post('http://145.24.222.156:5001/logout', data={'IBAN': dataInput})
                return response.text, response.status_code
                
        except Exception as e:
            print(e)
            return 'Json wrong', 432 # Bad request

#first updates login time then returns a list with the receipt info
#returns 208 if everything OK and 432 if json wrong.
class Receipt(Resource): # POST
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('IBAN', required=True)
        args = parser.parse_args()
        try:
            dataInput = str(args.get('IBAN'))
            checkLoginTime(dataInput)
            query = "SELECT MAX(transactionID) FROM transactions WHERE iban = %s;"
            cursor.execute(query, dataInput)
            transactionID = (cursor.fetchone()[0])

            query = "SELECT cardID FROM accounts WHERE iban = %s;"
            cursor.execute(query, dataInput)
            cardID = (cursor.fetchone()[0])

            query = "SELECT `e-mail` FROM customer WHERE customerID = (SELECT customerID FROM accounts WHERE iban = %s);"
            cursor.execute(query, dataInput)
            email = (cursor.fetchone()[0])
            returnList = [transactionID, cardID, email]
            return returnList, 208
        except Exception as e:
            print(e)
            return 'Json wrong', 432 # Bad request

#first checks bank and sends withdraw request to sending IBAN, if withdraw is succesfull, it adds the amount to the targetIBAN
#and updates the balance and adds the transaction to the database
#returns 208 if everything OK, 436 if not logged in, 437 if balance is to low and 432 if json wrong.
class Transfer(Resource): # POST
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('IBAN', required=True)
        parser.add_argument('targetIBAN', required=True)
        parser.add_argument('amount', required=True)
        args = parser.parse_args()
        try:
            if float(args.get('amount')) <= 0:
                raise ValueError()
            
            dataInput = str(args.get('IBAN'))
            targetIBAN = str(args.get('targetIBAN'))
            if(checkBank(targetIBAN)):
                if(checkBank(dataInput)):
                    response = requests.post('http://145.24.222.243:8050/withdraw', data={'IBAN': dataInput, 'amount': str(args.get('amount'))})
                else:
                    response = requests.post('http://145.24.222.156:5001/withdraw', data={'IBAN': dataInput, 'amount': str(args.get('amount'))})

                if(response.status_code == 208):

                    targetIBAN = str(args.get('targetIBAN'))
                    query = "SELECT balance FROM accounts WHERE iban = %s;"
                    cursor.execute(query, targetIBAN)
                    oldAmount = int(cursor.fetchone()[0])
                    newAmount = oldAmount + int(args.get('amount'))

                    query = "UPDATE accounts SET balance = %s WHERE iban = %s;"
                    dataInputTuple = (newAmount, targetIBAN)
                    cursor.execute(query, dataInputTuple)
                    db.commit()

                    query = "SELECT MAX(transactionID) FROM transactions;"
                    cursor.execute(query)
                    transactionID = 1 + int(cursor.fetchone()[0])

                    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                    datInputTuple = (transactionID + 1, targetIBAN, float(args.get('amount')), date)
                    query = 'INSERT INTO `transactions` (`transactionID`, `transactionType`, `iban`, `amount`, `transactionDate`) VALUES (%s, "transfer", %s, %s, %s);'
                    cursor.execute(query, datInputTuple)
                    db.commit()
                    return 'OK', 208
                else:
                    return response.text, response.status_code
            else:
                response = requests.post('http://145.24.222.156:5001/transfer', data={'IBAN': dataInput, 'targetIBAN': str(args.get('targetIBAN')), 'amount': str(args.get('amount'))})
                return response.text, response.status_code
        except Exception as e:
            print(e)
            return 'Json wrong', 432 # Bad request


api.add_resource(CheckIfRegistered, '/checkIfRegistered') 
api.add_resource(Login, '/login')
api.add_resource(CheckAttempts, '/checkAttempts') 
api.add_resource(Withdraw, '/withdraw')
api.add_resource(CheckBalance, '/checkBalance')
api.add_resource(Logout, '/logout')
api.add_resource(Receipt, '/receipt')
api.add_resource(Transfer, '/transfer')

if __name__ == '__main__':
    logoutEveryone()
    app.run(host = '0.0.0.0', port=8050, debug=True)
