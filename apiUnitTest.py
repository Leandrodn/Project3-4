import requests
import unittest

import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb

#Tests the checkIfRegistered function of the api
class testAPICheckIfRegistered(unittest.TestCase):
    #Tests the normal function of the api, expects 208, 'OK' to return
    def test_normal_registered(self):
        response = requests.post('http://145.24.222.243:8050/checkIfRegistered', data={'IBAN':'NI99ABNA14789632'})
        response_data = response.status_code
        self.assertEqual(response_data, 208)
    
    #Tests if the iban is not registered, expects 433, 'Account not registered' to return
    def test_account_not_registered(self):
        response = requests.post('http://145.24.222.243:8050/checkIfRegistered', data={'IBAN':'NI99ABNA00000001'})
        response_data = response.status_code
        self.assertEqual(response_data, 433)

#Tests the login function of the api
class testAPILogin(unittest.TestCase):
    def setUp(self):
        db = MySQLdb.connect(host='145.24.222.243', port=8051, user="primary", passwd="Timmerman123!", db="ABNMANBRO")
        cursor = db.cursor()
        query = "UPDATE accounts SET login = 0 WHERE customerID = 1;"
        cursor.execute(query)
        db.commit()
        query = "UPDATE card SET noOfTries = 0, valid = 1 WHERE cardID = 1;"
        cursor.execute(query)
        db.commit()
        cursor.close()
        db.close()
    
    def tearDown(self):
        db = MySQLdb.connect(host='145.24.222.243', port=8051, user="primary", passwd="Timmerman123!", db="ABNMANBRO")
        cursor = db.cursor()
        query = "UPDATE accounts SET login = 0 WHERE customerID = 1;"
        cursor.execute(query)
        db.commit()
        query = "UPDATE card SET noOfTries = 0, valid = 1 WHERE cardID = 1;"
        cursor.execute(query)
        db.commit()
        cursor.close()
        db.close()    

    #tests the normal function of the api, expects 208, 'OK' to return
    def test_normal_login(self):
        response = requests.post('http://145.24.222.243:8050/login', data={'IBAN':'NI99ABNA14789632', 'pincode':'0bf366a6fdd643807e24b567a94e9ab1f24ef87d9353b3248e2bc42503766275'})
        response_data = response.status_code
        self.assertEqual(response_data, 208)
    
    #tests the login with wrong pincode, expects 435, 'Pincode wrong' to return
    def test_wrong_pincode_login(self):
        response = requests.post('http://145.24.222.243:8050/login', data={'IBAN':'NI99ABNA14789632', 'pincode':'1234'})
        response_data = response.status_code
        self.assertEqual(response_data, 435)
    
    #tests the login with non-existing iban, expects 432, 'Json wrong' to return
    def test_wrong_iban_login(self):
        response = requests.post('http://145.24.222.243:8050/login', data={'IBAN':'NI99ABNA11111111', 'pincode':'0bf366a6fdd643807e24b567a94e9ab1f24ef87d9353b3248e2bc42503766275'})
        response_data = response.status_code
        self.assertEqual(response_data, 433)
    
    #tests if account gets blocked after 3 tries, expects 434, 'Account blocked' to return
    def test_too_many_attempts_login(self):
        for i in range (3):
            response = requests.post('http://145.24.222.243:8050/login', data={'IBAN':'NI99ABNA14789632', 'pincode':'1234'})
        response_data = response.status_code
        self.assertEqual(response_data, 434)

#Tests the checkAttempts function of the api
class testAPICheckAttempts(unittest.TestCase):
    def setUp(self):
        db = MySQLdb.connect(host='145.24.222.243', port=8051, user="primary", passwd="Timmerman123!", db="ABNMANBRO")
        cursor = db.cursor()
        query = "UPDATE card SET noOfTries = 0, valid = 1 WHERE cardID = 1;"
        cursor.execute(query)
        db.commit()
        cursor.close()
        db.close()
    
    def tearDown(self):
        db = MySQLdb.connect(host='145.24.222.243', port=8051, user="primary", passwd="Timmerman123!", db="ABNMANBRO")
        cursor = db.cursor()
        query = "UPDATE card SET noOfTries = 0, valid = 1 WHERE cardID = 1;"
        cursor.execute(query)
        db.commit()
        cursor.close()
        db.close()

    #Tests the normal function of the api, expects 3 (attempts) to return
    def test_normal_check_attempts(self):
        response = requests.post('http://145.24.222.243:8050/checkAttempts', data={'IBAN':'NI99ABNA14789632'})
        response_data = int(response.text)
        self.assertEqual(response_data, 3)

    #Tests if the amount of attempts goes down one after wrong login, expects 2 (attempts) to return
    def test_wrong_login_attempts(self):
        requests.post('http://145.24.222.243:8050/login', data={'IBAN':'NI99ABNA14789632', 'pincode':'1234'})
        response = requests.post('http://145.24.222.243:8050/checkAttempts', data={'IBAN':'NI99ABNA14789632'})
        response_data = int(response.text)
        self.assertEqual(response_data, 2)
    
    #Tests if the amount of attempts is reset after login, expects 3 (attempts) to return
    def test_reset_attempts(self):
        requests.post('http://145.24.222.243:8050/login', data={'IBAN':'NI99ABNA14789632', 'pincode':'1234'})
        requests.post('http://145.24.222.243:8050/login', data={'IBAN':'NI99ABNA14789632', 'pincode':'0bf366a6fdd643807e24b567a94e9ab1f24ef87d9353b3248e2bc42503766275'})
        response = requests.post('http://145.24.222.243:8050/checkAttempts', data={'IBAN':'NI99ABNA14789632'})
        response_data = int(response.text)
        requests.post('http://145.24.222.243:8050/logout', data={'IBAN':'NI99ABNA14789632'})
        self.assertEqual(response_data, 3)

#Tests the login and Withdraw function of the api, if the iban is blocked
class testAPILoginBlocked(unittest.TestCase):
    def setUp(self):
        db = MySQLdb.connect(host='145.24.222.243', port=8051, user="primary", passwd="Timmerman123!", db="ABNMANBRO")
        cursor = db.cursor()
        query = "UPDATE accounts SET login = 0 WHERE customerID = 1;"
        cursor.execute(query)
        db.commit()
        query = "UPDATE card SET noOfTries = 3, valid = 0 WHERE cardID = 1;"
        cursor.execute(query)
        db.commit()
        cursor.close()
        db.close()
    
    def tearDown(self):
        db = MySQLdb.connect(host='145.24.222.243', port=8051, user="primary", passwd="Timmerman123!", db="ABNMANBRO")
        cursor = db.cursor()
        query = "UPDATE accounts SET login = 0 WHERE customerID = 1;"
        cursor.execute(query)
        db.commit()
        query = "UPDATE card SET noOfTries = 0, valid = 1 WHERE cardID = 1;"
        cursor.execute(query)
        db.commit()
        cursor.close()
        db.close()   

    #Tests the login function, if the account is blocked, expects 434, 'Account blocked' to return
    def test_blocked_account_login(self):
        response = requests.post('http://145.24.222.243:8050/login', data={'IBAN':'NI99ABNA14789632', 'pincode':'0bf366a6fdd643807e24b567a94e9ab1f24ef87d9353b3248e2bc42503766275'})
        response_data = response.status_code
        self.assertEqual(response_data, 434)

    #Tests the withdraw function, if the account is blocked, expects 435, 'Not logged in' to return
    def test_blocked_account_withdraw(self):
        response = requests.post('http://145.24.222.243:8050/withdraw', data={'IBAN':'NI99ABNA14789632', 'amount':'200'})
        response_data = response.status_code
        self.assertEqual(response_data, 436)

#Tests the checkBalance function of the api
class testAPICheckBalance(unittest.TestCase):
    def setUp(self):
        db = MySQLdb.connect(host='145.24.222.243', port=8051, user="primary", passwd="Timmerman123!", db="ABNMANBRO")
        cursor = db.cursor()
        query = "UPDATE accounts SET balance = 500 WHERE customerID = 2;"
        cursor.execute(query)
        db.commit()
        query = "UPDATE card SET noOfTries = 0, valid = 1 WHERE cardID = 0;"
        cursor.execute(query)
        db.commit()
        cursor.close()
        db.close()
        requests.post('http://145.24.222.243:8050/login', data={'IBAN':'NI99ABNA01234567', 'pincode':'03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4'})
    
    def tearDown(self):
        db = MySQLdb.connect(host='145.24.222.243', port=8051, user="primary", passwd="Timmerman123!", db="ABNMANBRO")
        cursor = db.cursor()
        query = "UPDATE accounts SET balance = 100000 WHERE customerID = 2;"
        cursor.execute(query)
        db.commit()
        query = "UPDATE card SET noOfTries = 0, valid = 1 WHERE cardID = 0;"
        cursor.execute(query)
        db.commit()
        cursor.close()
        db.close()
        requests.post('http://145.24.222.243:8050/logout', data={'IBAN':'NI99ABNA01234567'})

    #Tests the normal function, expects the balance to be 500 to return
    def test_normal_check_balance(self):
        response = requests.post('http://145.24.222.243:8050/checkBalance', data={'IBAN':'NI99ABNA01234567'})
        response_data = float(response.text)
        self.assertEqual(response_data, 500)

    #Test check balance, if iban is not logged in, expects 436, 'Not logged in' to return
    def test_not_login_check_balance(self):
        requests.post('http://145.24.222.243:8050/logout', data={'IBAN':'NI99ABNA01234567'})
        response = requests.post('http://145.24.222.243:8050/checkBalance', data={'IBAN':'NI99ABNA01234567'})
        response_data = response.status_code
        self.assertEqual(response_data, 436)

    #Tests if the balance is updated after withdraw, expect the balance 300.5 to return
    def test_after_withdraw_check_balance(self):
        response = requests.post('http://145.24.222.243:8050/withdraw', data={'IBAN':'NI99ABNA01234567', 'amount':'199.5'})
        response = requests.post('http://145.24.222.243:8050/checkBalance', data={'IBAN':'NI99ABNA01234567'})
        response_data = float(response.text)
        self.assertEqual(response_data, 300.5)

#Tests the withdraw function of the api
class testAPIWithdraw(unittest.TestCase):
    def setUp(self):
        db = MySQLdb.connect(host='145.24.222.243', port=8051, user="primary", passwd="Timmerman123!", db="ABNMANBRO")
        cursor = db.cursor()
        query = "UPDATE accounts SET balance = 500 WHERE customerID = 2;"
        cursor.execute(query)
        db.commit()
        query = "UPDATE card SET noOfTries = 0, valid = 1 WHERE cardID = 0;"
        cursor.execute(query)
        db.commit()
        cursor.close()
        db.close()
        requests.post('http://145.24.222.243:8050/login', data={'IBAN':'NI99ABNA01234567', 'pincode':'03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4'})
    
    def tearDown(self):
        db = MySQLdb.connect(host='145.24.222.243', port=8051, user="primary", passwd="Timmerman123!", db="ABNMANBRO")
        cursor = db.cursor()
        query = "UPDATE accounts SET balance = 100000 WHERE customerID = 2;"
        cursor.execute(query)
        db.commit()
        query = "UPDATE card SET noOfTries = 0, valid = 1 WHERE cardID = 0;"
        cursor.execute(query)
        db.commit()
        cursor.close()
        db.close()
        requests.post('http://145.24.222.243:8050/logout', data={'IBAN':'NI99ABNA01234567'})

    #Tests withdraw if not logged in, expects 436, 'Not logged in' to return
    def test_not_login_withdraw(self):
        requests.post('http://145.24.222.243:8050/logout', data={'IBAN':'NI99ABNA01234567'})
        response = requests.post('http://145.24.222.243:8050/withdraw', data={'IBAN':'NI99ABNA01234567', 'amount':'200'})
        response_data = response.status_code
        self.assertEqual(response_data, 436)

    #Tests withdraw if balance is too low, expects 437, 'Balance too low' to return
    def test_balance_low_withdraw(self):
        response = requests.post('http://145.24.222.243:8050/withdraw', data={'IBAN':'NI99ABNA01234567', 'amount':'2000'})
        response_data = response.status_code
        self.assertEqual(response_data, 437)
    
    #Test normal function, expects 208, 'OK' to return
    def test_normal_withdraw(self):
        response = requests.post('http://145.24.222.243:8050/withdraw', data={'IBAN':'NI99ABNA01234567', 'amount':'200'})
        response_data = response.status_code
        self.assertEqual(response_data, 208)
    
    #Test if a negative amount can be withdrawn, expects 432, 'Json wrong' to return
    def test_negative_withdraw(self):
        response = requests.post('http://145.24.222.243:8050/withdraw', data={'IBAN':'NI99ABNA01234567', 'amount':'-200'})
        response_data = response.status_code
        self.assertEqual(response_data, 432)
    
    #Tests if the amount is realy withdrawn, expects balance - 200 to return
    def test_amount_is_withdraw(self):
        response = requests.post('http://145.24.222.243:8050/checkBalance', data={'IBAN':'NI99ABNA01234567'})
        oldBalance = float(response.text)
        requests.post('http://145.24.222.243:8050/withdraw', data={'IBAN':'NI99ABNA01234567', 'amount':'200'})
        response = requests.post('http://145.24.222.243:8050/checkBalance', data={'IBAN':'NI99ABNA01234567'})
        newBalance = float(response.text)
        self.assertEqual(newBalance, (oldBalance - 200))

#Tests the logout function of the api
class testAPILogout(unittest.TestCase):
    def setUp(self):
        db = MySQLdb.connect(host='145.24.222.243', port=8051, user="primary", passwd="Timmerman123!", db="ABNMANBRO")
        cursor = db.cursor()
        query = "UPDATE accounts SET balance = 500 WHERE customerID = 2;"
        cursor.execute(query)
        db.commit()
        query = "UPDATE card SET noOfTries = 0, valid = 1 WHERE cardID = 0;"
        cursor.execute(query)
        db.commit()
        cursor.close()
        db.close()
        requests.post('http://145.24.222.243:8050/login', data={'IBAN':'NI99ABNA01234567', 'pincode':'03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4'})
    
    def tearDown(self):
        db = MySQLdb.connect(host='145.24.222.243', port=8051, user="primary", passwd="Timmerman123!", db="ABNMANBRO")
        cursor = db.cursor()
        query = "UPDATE accounts SET balance = 100000 WHERE customerID = 2;"
        cursor.execute(query)
        db.commit()
        query = "UPDATE card SET noOfTries = 0, valid = 1 WHERE cardID = 0;"
        cursor.execute(query)
        db.commit()
        cursor.close()
        db.close()
        requests.post('http://145.24.222.243:8050/logout', data={'IBAN':'NI99ABNA01234567'})

    #Tests the normal logout function, expects 208, 'OK' to return
    def test_normal_logout(self):
        response = requests.post('http://145.24.222.243:8050/logout', data={'IBAN':'NI99ABNA01234567'})
        response_data = response.status_code
        self.assertEqual(response_data, 208)
    
    #Test if the logout worked, expects 436, 'Not logged in' to return
    def test_worked_logout(self):
        requests.post('http://145.24.222.243:8050/logout', data={'IBAN':'NI99ABNA01234567'})
        response = requests.post('http://145.24.222.243:8050/withdraw', data={'IBAN':'NI99ABNA01234567', 'amount':'200'})
        response_data = response.status_code
        self.assertEqual(response_data, 436)

#Tests the tranfer function of the api
class testAPITransfer(unittest.TestCase):
    def setUp(self):
        db = MySQLdb.connect(host='145.24.222.243', port=8051, user="primary", passwd="Timmerman123!", db="ABNMANBRO")
        cursor = db.cursor()
        query = "UPDATE accounts SET balance = 500 WHERE customerID = 2;"
        cursor.execute(query)
        db.commit()
        query = "UPDATE card SET noOfTries = 0, valid = 1 WHERE cardID = 0;"
        cursor.execute(query)
        db.commit()
        cursor.close()
        db.close()
        requests.post('http://145.24.222.243:8050/login', data={'IBAN':'NI99ABNA01234567', 'pincode':'03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4'})
        requests.post('http://145.24.222.243:8050/login', data={'IBAN':'NI99ABNA20011306', 'pincode':'f89328f7804b950087f0fabde05183a45be91aaca59f8d029bb1932bfbc87bc7'})
    
    def tearDown(self):
        db = MySQLdb.connect(host='145.24.222.243', port=8051, user="primary", passwd="Timmerman123!", db="ABNMANBRO")
        cursor = db.cursor()
        query = "UPDATE accounts SET balance = 100000 WHERE customerID = 2;"
        cursor.execute(query)
        db.commit()
        query = "UPDATE card SET noOfTries = 0, valid = 1 WHERE cardID = 0;"
        cursor.execute(query)
        db.commit()
        cursor.close()
        db.close()
        requests.post('http://145.24.222.243:8050/logout', data={'IBAN':'NI99ABNA01234567'})
        requests.post('http://145.24.222.243:8050/logout', data={'IBAN':'NI99ABNA20011306'})

    #Tests tranfer if not logged in, expects 436, 'Not logged in' to return
    def test_not_login_transfer(self):
        requests.post('http://145.24.222.243:8050/logout', data={'IBAN':'NI99ABNA01234567'})
        response = requests.post('http://145.24.222.243:8050/transfer', data={'IBAN':'NI99ABNA01234567', 'targetIBAN':'NI99ABNA20011306', 'amount':'200'})
        response_data = response.status_code
        self.assertEqual(response_data, 436)

    #Tests transfer if balance too low, expects 437, 'Balance too low' to return
    def test_balance_low_transfer(self):
        response = requests.post('http://145.24.222.243:8050/transfer', data={'IBAN':'NI99ABNA01234567', 'targetIBAN':'NI99ABNA20011306', 'amount':'2000'})
        response_data = response.status_code
        self.assertEqual(response_data, 437)
    
    #Tests the normal function, expects 208, 'OK' to return
    def test_normal_transfer(self):
        response = requests.post('http://145.24.222.243:8050/transfer', data={'IBAN':'NI99ABNA01234567', 'targetIBAN':'NI99ABNA20011306', 'amount':'200'})
        response_data = response.status_code
        self.assertEqual(response_data, 208)
    
    #Tests the transfer of negative amount, expects 432, 'Json wrong' to return
    def test_negative_transfer(self):
        response = requests.post('http://145.24.222.243:8050/transfer', data={'IBAN':'NI99ABNA01234567', 'targetIBAN':'NI99ABNA20011306', 'amount':'-200'})
        response_data = response.status_code
        self.assertEqual(response_data, 432)

    #Tests if the amount is taken from the account after transfer, expects (oldbalance - 200) to return
    def test_amount_is_taken_transfer(self):
        response = requests.post('http://145.24.222.243:8050/checkBalance', data={'IBAN':'NI99ABNA01234567'})
        oldBalance = float(response.text)
        requests.post('http://145.24.222.243:8050/transfer', data={'IBAN':'NI99ABNA01234567', 'targetIBAN':'NI99ABNA20011306', 'amount':'200'})
        response = requests.post('http://145.24.222.243:8050/checkBalance', data={'IBAN':'NI99ABNA01234567'})
        newBalance = float(response.text)
        self.assertEqual(newBalance, (oldBalance - 200))
    
    #Tests if the amount is transfered to target account, expects (oldBalance + 200) to return
    def test_amount_is_transfer(self):
        response = requests.post('http://145.24.222.243:8050/checkBalance', data={'IBAN':'NI99ABNA20011306'})
        oldBalance = float(response.text)
        requests.post('http://145.24.222.243:8050/transfer', data={'IBAN':'NI99ABNA01234567', 'targetIBAN':'NI99ABNA20011306', 'amount':'200'})
        response = requests.post('http://145.24.222.243:8050/checkBalance', data={'IBAN':'NI99ABNA20011306'})
        newBalance = float(response.text)
        self.assertEqual(newBalance, (oldBalance + 200))
    

if __name__=='__main__':
    unittest.main()