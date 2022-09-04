from flask import Flask
from flask import render_template
from flask import request
from flask import session
from flask import redirect
from flask import url_for
import json
import time
import requests
from bs4 import BeautifulSoup
import lxml
import random
from datetime import date
import copy
from webui import WebUI

#init
app = Flask(__name__, template_folder='templates', static_folder='statics')
ui = WebUI(app, debug=True) # Create a WebUI instance

app.secret_key = "stocksimulator!?""__"
@app.route("/")
@app.route('/index.html')
def home():
    return render_template('index.html')


@app.route('/sign_up.html', methods = ["POST", "GET"])
def signup():
    username = request.form.get("name")          #gets username from form
    session["password"] = request.form.get("pass")     #gets password from form and stores to a session variable
    with open("user_pass.json", "r") as file:        #Gets data from the user_pass json file and stores to data
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
    session["password"] = request.form.get("pass_input")        #gets password from login form and saves it to a session variable
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
            total_final = "$" + str(total)               #total transaction cost including tax
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
                        if j == password:
                            pop_list.append(i)
                for x in pop_list:
                    data2.pop(x)
                json.dump(data2, file2, indent = 2)
                return render_template("sign_up.html")

@app.route('/sell.html', methods = ["POST", "GET"])
def sell():
    data_list = []
    session["chunked_list"] = []
    session["headers"] = ["Date Purchased", "Stock Symbol", "Amount Paid", "Current Amount", "Profit", "Percent Gain", "Sell"]
    with open("C:\\Users\\joey_\\StockSimulator\\data.json", "r") as file:
        data = json.load(file)
        flag = True
        for i in data:
            for n in data[i].keys():

                if n == session.get("password"):
                    for j in data[i]:
                        for k in data[i][j]:
                            data_list.append(k)
                            for l in data[i][j][k]:
                                data_list.append(l)
                                for m in data[i][j][k][l]:
                                    data1 = float(m) * float(data[i][j][k][l][m])
                                    data_list.append('{:.2f}'.format(data1))       
                                    r_dis = requests.get("https://www.marketwatch.com/investing/stock/" + l)    #gathers stock data again and calculates if the user has enough money to perform this transaction, if no then return the suer does not hve enough funds
                                    html_dis = BeautifulSoup(r_dis.text, 'lxml')
                                    html = html_dis.find(class_ = "intraday__price")
                                    html = html.text
                                    html = html.replace("$", "")
                                    html = html.strip("\n")            
                                    session["total"] = float(html) * float(int(m))
                                    data_list.append('{:.2f}'.format(session.get("total")))              
                                    data2 = float(session.get("total")) - float(m) * float(data[i][j][k][l][m])
                                    data_list.append('{:.2f}'.format(data2))          
                                    data_list.append('{:.2f}'.format(round(round(float(session.get("total")) - float(m) * float(data[i][j][k][l][m]),4) / round(float(m) * float(data[i][j][k][l][m]),4),4)* 100)) 
                                    data_list.append(len(data_list)/ 7 + 1)
                                    flag = True
                else:
                    flag = False
                

        chunked_list = list()
        chunk_size = 7
        for i in range(0, len(data_list), chunk_size):
            chunked_list.append(data_list[i:i+chunk_size])
            session["chunked_list"] = chunked_list
    if flag == False:
        return render_template("sell.html", headings = session.get("headers"), chunked_list = [])
    else:
        return render_template("sell.html", headings = session.get("headers"), chunked_list = session.get("chunked_list"))
    
@app.route('/stock_sell', methods = ["GET", "POST"])
def sell_stock():
    
    number_list = []
    data = list(request.form.keys())
    data = data[0]
    chunked_list = session.get("chunked_list")
    chunked_list.pop(int(data))
    
    with open("C:\\Users\\joey_\\StockSimulator\\data.json", "r") as file:
        data2 = json.load(file)
        data2_copy = copy.copy(data2)
        x = 0
        flag = True
        flag2 = True;
        if flag == True:
            for i in data2_copy:
                for n in data2_copy[i].keys():
                    if n == session.get("password"):
                        for j in data2_copy[i]:
                            for k in data2_copy[i][j]:
                                for l in data2_copy[i][j][k]:
                                    for m in data2_copy[i][j][k][l]:
                                        r_dis = requests.get("https://www.marketwatch.com/investing/stock/" + l)    #gathers stock data again and calculates if the user has enough money to perform this transaction, if no then return the suer does not hve enough funds
                                        html_dis = BeautifulSoup(r_dis.text, 'lxml')
                                        html = html_dis.find(class_ = "intraday__price")
                                        html = html.text
                                        html = html.replace("$", "")
                                        html = html.strip("\n")            
                                        session["total"] = float(html)
                                        data1 = float(m) * session.get("total")
                                        number_list.append(data1)

            with open("C:\\Users\\joey_\\StockSimulator\\user_pass.json","r") as file:
                data3 = json.load(file)
                data3_copy = copy.copy(data3)
            with open("C:\\Users\\joey_\\StockSimulator\\user_pass.json","w") as file: 
                for i in data3_copy.keys():
                    if i == session.get("password"):
                        for k,v in data3_copy[i].items():
                            data3[i][k] = data3_copy[i][k] + number_list[int(data)]
                            json.dump(data3, file)
                            flag = False
        
        for i in data2_copy:
            if flag2 == True:
                for n in data2_copy[i].keys():
                    if n == session.get("password"):
                        if x == int(data):
                            with open("C:\\Users\\joey_\\StockSimulator\\data.json", "w") as file:
                                data2.pop(i)
                                json.dump(data2, file, indent = 2)
                                flag2 = False
                        else:
                            x = x + 1
                            continue


        return redirect(url_for('sell'))

@app.route('/portfolio.html', methods = ["POST", "GET"])
def portfolio():
    with open("C:\\Users\\joey_\\StockSimulator\\data.json") as file:
        data = json.load(file)
        data_list = []
        portolist = list()
        portolist2 = list()
        headers = ["Stock Symbol", "Shares Owned", "Original Amount", "Current Amount", "Profit", "Percent Gain"]
        for i in data:
            for n in data[i].keys():
                if n == session.get("password"):
                    for j in data[i]:
                        for k in data[i][j]:
                            for l in data[i][j][k]:
                                data_list.append(l)
                                for m in data[i][j][k][l]:
                                    data_list.append(m)       
                                    r_dis = requests.get("https://www.marketwatch.com/investing/stock/" + l)    #gathers stock data again and calculates if the user has enough money to perform this transaction, if no then return the suer does not hve enough funds
                                    html_dis = BeautifulSoup(r_dis.text, 'lxml')
                                    html = html_dis.find(class_ = "intraday__price")
                                    html = html.text 
                                    html = html.replace("$", "")
                                    html = html.strip("\n")            
                                    total = float(html) * float(int(m))
                                    data_list.append(total)

        chunked_list = list()
        chunk_size = 3
        for i in range(0, len(data_list), chunk_size):
            chunked_list.append(data_list[i:i+chunk_size])
        
        for i in range(len(chunked_list)):
            portolist.append(chunked_list[i][0])
            portolist2.append(chunked_list[i][1])
        portodict = dict()
        starting_list = list()
        for i in range(len(portolist)):
            if portolist[i] in portodict:
                portodict[portolist[i]] = int(portodict[portolist[i]]) + int(portolist2[i])
            else:
                portodict[portolist[i]] = portolist2[i]
        for i in range(len(list(portodict.keys()))):
            t = 0
            m = 0
            starting_list.append(list(portodict.keys())[i])#stock symbol
            starting_list.append(list(portodict.values())[i])#how many shares
            r_dis = requests.get("https://www.marketwatch.com/investing/stock/" + list(portodict.keys())[i])    #gathers stock data again and calculates if the user has enough money to perform this transaction, if no then return the suer does not hve enough funds
            html_dis = BeautifulSoup(r_dis.text, 'lxml')
            html = html_dis.find(class_ = "intraday__price")
            html = html.text
            html = html.replace("$", "")
            html = html.strip("\n")
            total = float(html) * float(int(list(portodict.values())[i]))
            for x in range(len(session.get("chunked_list"))):
                if session.get("chunked_list" )[x][1] == list(portodict.keys())[i]:
                    m = m + float(session.get("chunked_list")[x][2])
                    t = t + float(session.get("chunked_list")[x][4])
                else:
                    m = m
                    t = t
            starting_list.append(m)
            starting_list.append(total) #how much worth now
            starting_list.append(t)
            starting_list.append('{:.2f}'.format(((total -  m) / m) * 100))  
                                                                                        
        chunked_list = list()
        chunk_size = 6
        total_profit = 0

        for i in range(0, len(starting_list), chunk_size):
            chunked_list.append(starting_list[i:i+chunk_size])
        return render_template("portfolio.html", headings = headers, chunked_list = chunked_list)
            
            
if __name__ == '__main__':
     app.run()
