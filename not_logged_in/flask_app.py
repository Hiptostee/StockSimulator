from flask import Flask
from flask import render_template
from flask import request
from flask import session
import json
import time
import requests
from bs4 import BeautifulSoup
import lxml
import random
from datetime import date

#init
app = Flask(__name__, template_folder='templates', static_folder='statics')
app.secret_key = "stocksimulator!?""__"
@app.route("/")
@app.route('/index.html')
def home():
    return render_template('index.html')


@app.route('/sign_up.html', methods = ["POST", "GET"])
def signup():
    username = request.form.get("name")          #gets username from form
    session["password"] = request.form.get("pass")     #gets password from form and stores to a session variable
    with open("C:\\Users\\joey_\\StockSimulator\\user_pass.json", "r") as file:        #Gets data from the user_pass json file and stores to data
        data = json.load(file)
    if session.get("password") in data.keys():          #tries to validate signup information
        if session.get("password") == None:                #if there is no data in the user signup orm, set the output to nothing becuase if there is nothing it defaults to something unwanted
            output = ""
        else:                                 #if there is data in the user signupt form, but the password is aleready in the data, then render sign_up.html with the output that says the username or password is already taken
            output = "Password or Username Already Taken"
        return render_template("sign_up.html", output = output)

    else:
        if session.get("password") == None:              #if there is no data in the user signup orm, set the output to nothing becuase if there is nothing it defaults to something unwanted
            output = ""
            return render_template("sign_up.html", output = output)
        else:
            with open("C:\\Users\\joey_\\StockSimulator\\user_pass.json", "w") as file:         #if the password is available, save data into user_pass.json as follows: {password:{username:10000}}
                data[session.get("password")] = ({username:10000})
                json.dump(data, file)
            return render_template("homepage.html")   #redirect to logged in pages after signup is validated

@app.route('/aboutus.html')              #redirects to about us page
def about():
    return render_template('aboutus.html')

@app.route('/login.html', methods = ["POST", "GET"])
def login():
    username = request.form.get("user_input")                     #gets username from login form
    session["password"] = request.form.get("pass_input")                      #gets password from login form and saves it to a session variable
    with open("C:\\Users\\joey_\\StockSimulator\\user_pass.json", "r") as file:
        data = json.load(file)                                                    #loads user-pass.json and gathers data
    if session.get("password") in data.keys():                             #if password in the data, then log the user in and redirect to homepage
        return render_template("homepage.html")
    else:
        if session.get("password") == None:                             #if the form is submitted empty by page refreshing, set output to nothing to avoid unwanted outputs
            output = ""
        else:
            output = "Login Failed"                                     #if password is not in data, then display login failed and prompt the user to try again
        return render_template("login.html", output = output)


@app.route('/help.html')
def help():
    return render_template('help.html')

@app.route('/aboutus2.html')
def about2():
    return render_template('aboutus2.html')

@app.route('/help2.html')
def help2():
    return render_template('help2.html')
@app.route('/homepage.html')
def homepage():
    return render_template('homepage.html')

@app.route('/buy.html', methods = ["POST", "GET"])
def buy():

    stock_name = request.form.get('user_input_buy')
    amount_of_stock = request.form.get("pass_input_buy")

    with open("C:\\Users\\joey_\\StockSimulator\\user_pass.json", "r") as file:
        data = json.load(file)

    if stock_name == None or amount_of_stock == None:
        return render_template("buy.html")

    else:
        try:                                                                                                    #trys to find all transaction details from user input
            r_dis = requests.get("https://www.marketwatch.com/investing/stock/" + stock_name)      #Gets the price of the stock of the users choice
            html_dis = BeautifulSoup(r_dis.text, 'lxml')
            html = html_dis.find(class_ = "intraday__price")
            html = html.text
            html = html.replace("$", "")
            html = html.strip("\n")
            html = float(html)
            total = round(html * float(amount_of_stock), 2)
            with open("C:\\Users\\joey_\\StockSimulator\\user_pass.json","r") as file:
                data = json.load(file)
                for i in data.keys():
                    if i == session.get("password"):
                        for j in data[i].values():                             #finds the worth of the users account and multiplies by 1% to get the tax rate
                            tax = 0.01 * float(j)
            total_final = "$" + str(round((total + tax), 2))               #total transaction cost including tax
            stock_symbol = stock_name                               #stock symbol
            price = "$" + str(html)                           #price per indavidual stock
            amount = amount_of_stock                               #amount of shares purchased


        except:                               #if cant find all transaction details, display this message and prompt the user to try again with a new stock name or number of shares
            return render_template("buy.html", error = "Stock Not Found, or Number of Shares Invalid")


        with open("C:\\Users\\joey_\\StockSimulator\\user_pass.json","r") as file:
            r_dis = requests.get("https://www.marketwatch.com/investing/stock/" + stock_name)    #gathers stock data again and calculates if the user has enough money to perform this transaction, if no then return the suer does not hve enough funds
            html_dis = BeautifulSoup(r_dis.text, 'lxml')
            html = html_dis.find(class_ = "intraday__price")
            html = html.text
            html = html.replace("$", "")
            html = html.strip("\n")
            html = float(html)
            total = round(html * float(amount_of_stock), 2)
            data = json.load(file)
            for i in data.keys():
                if i == session.get("password"):
                    for j in data[i].values():
                        total2 = (j - total)
                        if total2 < 0:
                            return render_template("buy.html", error = "You do not have enough funds")
        with open("C:\\Users\\joey_\\StockSimulator\\user_pass.json","w") as file:         #update user account value after valid transaction
            for i in data.keys():
                if i == session.get("password"):
                    for k,v in data[i].items():
                        data[i][k] = total2
                        json.dump(data, file)

        rando = random.randint(100000,999999)
        with open("C:\\Users\\joey_\\StockSimulator\\data.json", "r") as file:
            data = json.load(file)

        with open("C:\\Users\\joey_\\StockSimulator\\data.json", "w") as file:
            data[rando] = ({session.get('password'):{str(date.today()):{stock_name:{amount_of_stock:html}}}})         #add user transaction details to data.json
            json.dump(data, file, indent = 2)


        return render_template("buy.html", total = total_final, stock_symbol = stock_name, price = price, amount = amount_of_stock)      #render buy.html after all values have been satisfied

@app.route('/delete_account.html', methods = ["POST", "GET"])
def delete():
    password = request.form.get("user_input")
    pop_list = []
    with open("C:\\Users\\joey_\\StockSimulator\\user_pass.json", "r") as file:
        data = json.load(file)
    with open("C:\\Users\\joey_\\StockSimulator\\data.json", "r") as file2:
        data2 = json.load(file2)
        if password not in data:
            return render_template("delete_account.html", output = "Password Not Found")
        else:
            with open("C:\\Users\\joey_\\StockSimulator\\user_pass.json", "w") as file:
                data.pop(password)
                json.dump(data, file)
            with open("C:\\Users\\joey_\\StockSimulator\\data.json", "w") as file2:
                for i in data2.keys():
                    for j in data2[i]:
                        print(j)
                        if j == password:
                            pop_list.append(i)
                for x in pop_list:
                    data2.pop(x)
                json.dump(data2, file2, indent = 2)
                return render_template("sign_up.html")

                            
            
            


if __name__ == '__main__':
    app.run()
