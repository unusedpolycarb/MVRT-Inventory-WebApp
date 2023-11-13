from googleapiclient.discovery import build
from google.oauth2 import service_account
import json
from Part import Part
from Container import Container
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, flash, url_for, session

def logUsage(log,program):
    time = datetime.now()
    fpath='logs/'+program+'_Log.txt'
    f=open(fpath,'a+')         #file to log activities of this article method
    f.write('<--------------------------------------------------------------------\n<- MVRT Inventory '+program+' | '+time+'\n')
    f.write(log)
    f.write('<--------------------------------------------------------------------\n\n')
    f.close()

#binary search to find each container
def find_container(main_subcontainer, var_to_search, left, right):
    if left >= right:
        subcontainer = main_subcontainer[list(main_subcontainer)[left]]
        compare = int(subcontainer.get_name()[1:len(subcontainer.get_name())])
        if compare == var_to_search:
            return subcontainer
        else:
            print("Error: Could not find" + var_to_search)
            return None
    else:
        mid = int((left + right)/2)
        subcontainer = main_subcontainer[list(main_subcontainer)[mid]]
        compare = int(subcontainer.get_name()[1:len(subcontainer.get_name())])
        if compare == var_to_search:
            return subcontainer
        else:
            if compare > var_to_search:
                right = mid
                return find_container(main_subcontainer, var_to_search, left, right)
            elif compare < var_to_search:
                left = mid
                return find_container(main_subcontainer, var_to_search, left, right)

#DO NOT CHANGE ANY OF THESE
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'credentials.json'
credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

SPREADSHEET_ID = '1bxXwCWb2kWIikapUZnHK4ae-7c2lemhH6uMWjr3ORi4'
#######################################################################
#Hard Coding Storage Layout#################################################################################################################################################################################
toolbox = {}
gc = {}
bc = {}
other = {}
sessions = {}
all_parts = []
all_toolbox_parts = []
all_gc_parts = []
all_bc_parts = []
all_other_parts = []
ol1 = Container("OL1")
#
NUM_A_BUCKETS = 45
a_containers = {}
for i in range(NUM_A_BUCKETS):
    key = "A{}".format(i + 1)
    a_containers[key] = Container(key)
#
NUM_B_BUCKETS = 36
b_containers = {}
for i in range(NUM_A_BUCKETS):
    key = "B{}".format(i + 1)
    b_containers[key] = Container(key)
#
NUM_C_BUCKETS = 45
c_containers = {}
for i in range(NUM_A_BUCKETS):
    key = "C{}".format(i + 1)
    c_containers[key] = Container(key)
#
SHELVES = 6
for i in range(SHELVES):
    key = "S{}".format(i + 1)
    bc[key] = Container(key)
#
NUM_TOOLBOX_SHELVES = 23
for i in range(NUM_TOOLBOX_SHELVES):
    key = "T{}".format(i + 1)
    toolbox[key] = Container(key)
#
NUM_OTHER = 2
for i in range(NUM_OTHER):
    key = "O{}".format(i + 1)
    other[key] = Container(key)
#
gc["A"] = a_containers
gc["B"] = b_containers
gc["C"] = c_containers
#End Hard Coding Here ########################################################################################################################################## ################################################
list_parts = []
service = build('sheets', 'v4', credentials=credentials)
sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                            range="Index").execute()
#result = service.spreadsheets().values().update(
#    spreadsheetId=SPREADSHEET_ID, range="Fasteners",
#    valueInputOption="USER_ENTERED").execute()
format = json.dumps(result)
result = json.loads(format)
headers = result["values"][0][0:5]
for i in range(1, len(result["values"])):
    data = result["values"][i][0:6]
    if not len(data) == 0:
        part = Part(data[0], data[1], data[2], data[3], data[4], data[5])
        list_parts.append(part)
        if data[5][0] == "A":
            main_subcontainer = a_containers
            all_gc_parts.append(part)
        if data[5][0] == "B":
            main_subcontainer = b_containers
            all_gc_parts.append(part)
        if data[5][0] == "C":
            main_subcontainer = c_containers
            all_gc_parts.append(part)
        if data[5][0] == "T":
            main_subcontainer = toolbox
            all_toolbox_parts.append(part)
        if data[5][0] == "S":
            main_subcontainer = bc
            all_bc_parts.append(part)
        if data[5][0] == "O":
            main_subcontainer = other
            all_other_parts.append(part)
        sc = find_container(main_subcontainer, int(part.get_location()[1:len(part.get_location())]), 0, len(main_subcontainer.keys()))
        sc.add({"name": part.get_name(),
                "quantity": part.get_quantity(),
                "unit": part.get_unit(),
                "link": part.get_link(),
                "needtobuy": part.get_status()})

for key in toolbox.keys():
    toolbox[key] = toolbox[key].get_contents()

toolbox_json = json.dumps(toolbox)
app = Flask(__name__)
app.secret_key = "ADITHYAJATINAKASHJAINAM"
app.permanent_session_lifetime = timedelta(hours = 3)

@app.route("/")
def login():
    if bool(session) == True:
        return redirect(url_for("homepage"))
    else:
        return render_template("index.html", methods = ["POST"])

@app.route("/authentication", methods = ["GET", "POST"])
def check_login():
    if request.method == "POST":
        username = request.form["username"]
        pwd = request.form["pwd"]
        combo = str(username + pwd)
        combo = combo.strip()
        is_matched = False
        with open("logins.txt", "r") as file:
            for line in file:
                line = str(line).strip()
                if combo == line:
                    is_matched = True

        if is_matched == True:
            sessions["username"] = username
            sessions["password"] = pwd
            sessions["time"] = str(datetime.now())
            f=open("log.txt",'a+')         #file to log activities of this article method
            f.write("MVRT Inventory " + "logged in by " + sessions["username"] + " at " + sessions["time"] + "\n")
            f.close()
            session.permanent = True
            return redirect(url_for("homepage"))
        else:
            f=open("log.txt",'a+')         #file to log activities of this article method
            f.write("Attempted login by " + " at " + str(datetime.now()) + "\n")
            f.close()
            flash("Your username or password is incorrect.")
            return redirect(url_for("login"))

@app.route("/home", methods = ["GET", "POST"])
def homepage():
    if bool(session) == True:
        return render_template("home.html")
    else:
        return redirect(url_for("login"))

@app.route("/input-processing", methods = ["GET", "POST"])
def check_input():
    if bool(session) == False:
        return redirect(url_for("login"))

    if request.method == "POST":
        if not request.form["Inventory"] == None:
            return redirect(url_for("inventory"))
        elif not request.form["Transactions"] == None:
            return redirect(url_for("transactions"))
        elif not request.form["Log"] == None:
            return redirect(url_for("log"))
        else:
            logUsage("Buttons on home.html do not work", "check_input")

@app.route("/inventory", methods = ["GET", "POST"])
def inventory():
    if bool(session) == False:
        return redirect(url_for("login"))

    return render_template("inventory_selection.html")

@app.route("/transactions", methods = ["GET", "POST"])
def transactions():
    if bool(session) == False:
        return redirect(url_for("login"))

    return render_template("transactions.html")

@app.route("/transactionlogs", methods = ["GET", "POST"])
def log():
    if bool(session) == False:
        return redirect(url_for("login"))

    return render_template("logs.html")

@app.route("/logout")
def logout():
    sessions.clear()
    session.clear()
    flash("You have successfully logged out.")
    return redirect(url_for("login"))

@app.route("/toolbox-inventory")
def toolbox_inventory():
    if bool(session) == False:
        return redirect(url_for("login"))

    return render_template("toolbox_inventory.html", toolbox = toolbox, toolbox_json = toolbox_json)
