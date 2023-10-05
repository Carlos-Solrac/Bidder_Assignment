"""

Name: Carlos Cuellar
Date: 10/22/22
Assignment: 8
Due Date:10/3/22
About this project: Develop code that encrypts data stored in a database for a  small scale  using third-party Python
libraries discussed in the course. Use this database to send encrypted messages with HMAC authentication to a python created server.
Assumptions: Assume correct input.
All work below was performed by Carlos Cuellar
"""

from flask import Flask, render_template, request, session, flash, jsonify
import Encryption, socket, os, string, base64, hmac, hashlib
import sqlite3 as sql
import pandas as pd

app = Flask(__name__)


@app.route('/')
def home():  # Renders homepage
    if not session.get('logged_in'):  # Check for an active logged-in user session and renders a login screen if false.
        return render_template('loginpage.html')
    else:
        return render_template('home.html', name=session['Bidder_Name'])  # Renders homepage with user name.


@app.route('/logout')  # Logout page simply sets all parameters to false or in the cas eof name, sets it to a space.
def logout():
    session['logged_in'] = False
    session['admin'] = False
    session['AppRoleLvl2'] = False
    session['AppRoleLvl1'] = False
    session['Bidder_Name'] = ""
    return home()


@app.route('/sendbid')
def sendbid():
    if not session.get('logged_in'):
        return render_template('loginpage.html')
    else:
        return render_template('sendbid.html', name=session['Bidder_Name'])


@app.route('/sendHMACbid')
def send_HMAC_bid():
    if not session.get('logged_in'):
        return render_template('loginpage.html')
    else:
        return render_template('sendHMACbid.html', name=session['Bidder_Name'])


@app.route('/addbidder')
def addbidder():  # Renders new bidder page
    if not session.get('logged_in'):
        return render_template('loginpage.html')

    elif session.get('admin'):
        return render_template('addbidder.html')
    else:  # Renders the result page with an error of not found if the user is not logged in to a valid session.
        msg = "Page not found."
        return render_template('result.html', msg=msg)


@app.route('/sendbid', methods=['POST'])
def send_bid_msg():
    # Validate user has logged in.
    if not session.get('logged_in'):
        return render_template('loginpage.html')
    else:
        if request.method == 'POST':
            try:
                bidderid = str(session['Bidder_Id'])
                itemid = request.form['Item_Id']
                itembidamount = request.form['Bid_Amount']
                # Set host and port channels.
                HOST, PORT = "localhost", 9999
                # Create a socket connection to speak to the msgserver
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # Connect to the server and send data
                sock.connect((HOST, PORT))
                # msg is meant to hold error messages and success messages.
                msg = " "
                # If either itemid or item amount are invalid we check them individually and provide an error message.
                if not itemid.isnumeric() and not itembidamount.isnumeric():
                    if not itemid.isnumeric():
                        msg = "Error: Item Id must be a numeric value greater than 0."
                    if not itembidamount.isnumeric():
                        msg = msg + "\nError: Item bid amount must be a numeric value greater than 0."
                else:
                    # With item id and bid amount validated we encrypt those values along with the bidders ID and
                    # send it to the message server.
                    itemid = str(Encryption.cipher.encrypt(bytes(itemid, 'utf-8')).decode("utf-8"))
                    itembidamount = str(Encryption.cipher.encrypt(bytes(itembidamount, 'utf-8')).decode("utf-8"))
                    bidderid = str(Encryption.cipher.encrypt(bytes(bidderid, 'utf-8')).decode("utf-8"))
                    # The three parameters are added to one string with a comma delimiter to be split by the message
                    # server.
                    msg = bidderid + "," + itemid + "," + itembidamount
                    sock.sendall(bytes(msg, "utf-8"))
                    sock.close()
                    msg = "Bid sent!"

            except socket.error as e:
                msg = "Error processing bid. Bid not sent.", e
            finally:
                return render_template('result.html', msg=msg)


@app.route('/sendHMACbid', methods=['POST'])
def send_HMAC_bid_msg():
    # Validate user has logged in.
    if not session.get('logged_in'):
        return render_template('loginpage.html')
    else:
        # Obtain the html information of bidder id, itemid, and itembid amount.
        if request.method == 'POST':
            try:
                bidderid = str(session['Bidder_Id'])
                itemid = request.form['Item_Id']
                itembidamount = request.form['Bid_Amount']
                # Set host and port channels.
                HOST, PORT = "localhost", 8888
                # Create a socket connection to speak to the msgserver
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # Connect to the server and send data
                sock.connect((HOST, PORT))
                # msg is meant to hold error messages and success messages.
                msg = " "
                # If either itemid or item amount are invalid we check them individually and provide an error message.
                if not itemid.isnumeric() and not itembidamount.isnumeric():
                    if not itemid.isnumeric():
                        msg = "Error: Item Id must be a numeric value greater than 0."
                    if not itembidamount.isnumeric():
                        msg = msg + "\nError: Item bid amount must be a numeric value greater than 0."
                else:
                    # With item id and bid amount validated we encrypt those values along with the bidders ID and
                    # send it to the message server.
                    encrypted_msg = ""
                    msg_values = [itemid, itembidamount, bidderid]
                    values_string = ','.join(msg_values)
                    for val in msg_values:
                        encrypted_msg = encrypted_msg + str(
                            Encryption.cipher.encrypt(bytes(val, 'utf-8')).decode("utf-8")) + ','
                    # The three parameters are added to one string with a comma delimiter to be split by the message
                    # server.

                    # Use HMAC to create a signature to append to our message.
                    secret_key = b'asd13a2f4dsf56'
                    computed_sig = hmac.new(secret_key, encrypted_msg.encode('utf-8'),
                                            digestmod=hashlib.sha3_512).digest()
                    # Encrypt the given message and append the HMAC tag to it.
                    sent_msg = encrypted_msg.encode('utf-8') + computed_sig
                    sock.sendall(bytes(sent_msg))
                    msg = "Bid sent!"
                    sock.close()

            except socket.error as e:
                msg = "Error processing bid. Bid not sent.", e
            finally:
                return render_template('result.html', msg=msg)


@app.route('/loginpage', methods=['POST'])
def do_login():
    try:
        nm = request.form['Bidder_Name']  # Obtain bidder name from loginpage.html
        pwd = request.form['Login_Password']  # Obtain bidder password from loginpage.html

        # Encrypting the name and password to then use for comparison to the database for login.
        nm = str(Encryption.cipher.encrypt(bytes(nm, 'utf-8')).decode("utf-8"))
        pwd = str(Encryption.cipher.encrypt(bytes(pwd, 'utf-8')).decode("utf-8"))

        with sql.connect(".auctionbidderDB.db") as conn:  # Connect to database and check if our username and password
            # match one in our database.

            conn.row_factory = sql.Row
            cur = conn.cursor()
            sql_select_query = """ SELECT * from Bidder where Bidder_Name = ? and Login_Password = ? """
            cur.execute(sql_select_query, (nm, pwd))

            row = cur.fetchone()
            if (row != None):
                session['logged_in'] = True  # Sets our session to true if the name/pwd pair is in our database.
                session['Bidder_Name'] = str(Encryption.cipher.decrypt(nm.encode('utf-8')))  # Set session name to
                session['Bidder_Id'] = row[0]

                # the decrypted name value provided.

                if int(row['App_Role_Level']) == 1:  # Sets our session admin role to true if the name is an approle 1
                    # in database.
                    session['admin'] = True
                else:
                    session['admin'] = False

                if int(row['App_Role_Level']) == 2:  # Sets our session AppRoleLvl2 role to true if the name is an
                    # approle 2 in database.
                    session['AppRoleLvl2'] = True
                else:
                    session['AppRoleLvl2'] = False

                if int(row['App_Role_Level']) == 3:  # #Sets our session approlelvl3 role to true if the name is an
                    # approle 3 in database.
                    session['AppRoleLvl1'] = True
                else:
                    session['AppRoleLvl1'] = False
            else:
                session['logged_in'] = False  # If the name and pwd are not in the database, the session is not
                # logged in. Advise user to try again.

                flash("Invalid Username or Password. Please try again.")
    except ValueError:
        conn.rollback()
        flash("Error in insert operation.")
    finally:
        conn.close()
    return home()


@app.route('/addrec', methods=['POST', 'GET'])
def addrec():  # Renders page to add bidder information
    if not session.get('logged_in'):
        return render_template('loginpage.html')
    elif session.get('admin'):  # Checks the user is an admin before allowing the adding function.
        if request.method == 'POST':
            try:

                # Required to encrypt Name, Phone Number, and Password. Encrypted right after validating input.

                nm = request.form['Bidder_Name']
                phonenum = request.form['Phone_Number']
                prequalified = request.form['Pre_Qualified_Upper_Limit']
                rolelevel = request.form['App_Role_Level']
                pwd = request.form['Login_Password']

                with sql.connect(".auctionbidderDB.db") as con:  # Connect to our Bidder db
                    cur = con.cursor()
                    # Insert html page data into our database with place-holders of ?

                    msg = ""
                    # Below are data input validation checks. Any incorrect input will append a error msg to our msg
                    # variable. After the checks, if the msg variable has anything in it, we go to an excepot state.
                    if isBlank(nm):
                        msg = "You cannot enter an blank name."
                    else:
                        nm = str(Encryption.cipher.encrypt(bytes(nm, 'utf-8')).decode("utf-8"))
                    if isBlank(phonenum):
                        msg = msg + "\nYou cannot enter an blank phone number."
                    else:
                        phonenum = str(Encryption.cipher.encrypt(bytes(phonenum, 'utf-8')).decode("utf-8"))
                    if isBlank(prequalified):
                        msg = msg + "\nThe prequalified upper limit must be greater than 0."
                    elif int(prequalified) < 0:
                        msg = msg + "\nThe prequalified upper limit must be greater than 0."
                    if isBlank(rolelevel):
                        msg = msg + "\nThe app role level must be between 1-3."
                    elif int(rolelevel) < 1 or int(rolelevel) > 3:
                        msg = msg + "\nThe app role level must be between 1-3."
                    if isBlank(pwd):
                        msg = msg + "You cannot enter an blank password."
                    else:
                        pwd = str(Encryption.cipher.encrypt(bytes(pwd, 'utf-8')).decode("utf-8"))
                    if len(msg) > 0 or msg.isspace():
                        raise ValueError

                    else:
                        cur.execute(
                            "INSERT INTO Bidder (Bidder_Name,Phone_Number,Pre_Qualified_Upper_Limit,"
                            "App_Role_Level, "
                            "Login_Password  ) VALUES(?,?,?,?,?)",
                            (nm, phonenum, prequalified, rolelevel, pwd)
                        )

                        con.commit()  # Save changes
                        msg = "Successfully added record."

            except ValueError:
                msg = msg + "Error in insert operation."
                con.rollback()  # Roll back changes if there is an error with insertion.

            finally:
                con.close()  # Close connection after performing changes
                return render_template("result.html", msg=msg)
                # Take user to a result page to let them know if the operation was
                # successful or not.

    else:
        msg = "Page not found."
        return render_template('result.html', msg=msg)


@app.route('/bidderlist')
def listbidders():
    if not session.get('logged_in'):
        return render_template('loginpage.html')
    elif session.get('admin') or session.get('AppRoleLvl2'):
        conn = sql.connect(".auctionbidderDB.db")  # The bidder database
        conn.row_factory = sql.Row  # Create rows for a table

        cur = conn.cursor()  # Initiate a cursor
        cur.execute("""Select * from Bidder""")  # Obtain data from our database table Bidder
        df = pd.DataFrame(cur.fetchall(),
                          columns=['Bidder_ID', 'Bidder_Name', 'Phone_Number', 'Pre_Qualified_Upper_Limit',
                                   'App_Role_Level', 'Login_Password'])

        # Convert name to an array
        df = convertDataframeToArray(df, 'Bidder_Name')
        df = convertDataframeToArray(df, 'Phone_Number')
        conn.close()

        return render_template('list.html', rows=df)  # Return a html page of a table with our data
    else:
        msg = "Page not found."
        return render_template('result.html', msg=msg)


@app.route('/auctionitemlist')
def list_auction_items():
    if not session.get('logged_in'):
        return render_template('loginpage.html')
    conn = sql.connect(".auctionbidderDB.db")  # The bidder database
    conn.row_factory = sql.Row  # Create rows for a table

    cur = conn.cursor()  # Initiate a cursor
    cur.execute("""Select * from AuctionItem """)  # Obtain data from our database table Bidder
    df = pd.DataFrame(cur.fetchall(),
                      columns=['Item_ID', 'Item_Name', 'Item_Description', 'Lowest_Bid_Limit',
                               'Highest_Bidder_Id', 'Highest_Bidder_Amount'])
    conn.close()

    return render_template('auctionitemlist.html', rows=df)  # Return a html page of a table with our data


def isBlank(string):
    # this function checks for an empty string or one with only spaces in it.
    if string.isspace() or len(string) == 0:
        return True
    return False


def convertDataframeToArray(dataframe, colname):
    # This function takes in a pandas dataframe table with set columns and a column name. It then decrypts the values in
    # specified column and returns the dataframe.

    index = 0
    for string in dataframe[colname]:
        string = str(Encryption.cipher.decrypt(string))
        dataframe._set_value(index, colname, string)
        index += 1
    return (dataframe)


if __name__ == '__main__':
    app.secret_key = os.urandom(13)
    app.run(debug=True)
