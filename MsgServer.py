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

import socketserver
import Encryption
import sqlite3 as sql
from flask import flash


class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # self.request	is	the	TCP	socket	connected	to	the	client
        self.data = self.request.recv(4096).strip()
        print("{}	sent message:	".format(self.client_address[0]))
        # msg holds the received bytes. It is decoded into a  string and split by ','
        msg = (self.data).decode('UTF-8').split(',')
        # msg values are decrypted and placed into new variables for future use.
        self.bidderid = str(Encryption.cipher.decrypt(msg[0]))
        self.itemid = str(Encryption.cipher.decrypt(msg[1]))
        self.bidamount = str(Encryption.cipher.decrypt(msg[2]))
        status_msg = (bid_validation(self.bidderid, self.itemid, self.bidamount))
        print("Bidder id: ", self.bidderid, " Item Id: ", self.itemid, "Bid amount: ", self.bidamount)
        print(status_msg)


def bid_validation(bidderid, itemid, bidamount):
    # this function takes in the bid information received by the serve rin the handle function of the
    # MYTCPHANDLER class and validates the values and checks if the bid is valid. If it's valid, the database is
    # updated.
    try:

        with sql.connect(".auctionbidderDB.db") as conn:  # Connect to database and check if our username and password
            # Msg holds our error or success msgs to be returned.
            msg = ""
            # match one in our database.
            conn.row_factory = sql.Row
            cur = conn.cursor()
            sql_select_query = """ SELECT * from Bidder where Bidder_Id = ? """
            cur.execute(sql_select_query, (bidderid))
            bidder_row = cur.fetchone()

            if bidder_row is None:
                msg = "Error, invalid bidderid. Bid not registered."
            sql_select_query = """ SELECT * from AuctionItem where Item_Id = ? """
            cur.execute(sql_select_query, (itemid))
            auction_row = cur.fetchone()
            # Input validation of item id, bidder id, and bid amount. Error msgs are added to the msg variable for
            # each failed validation and returned to the calling function.
            if auction_row is None:
                msg = "Error, invalid item id. Bid not registered."
            elif int(bidamount) > bidder_row['Pre_Qualified_Upper_Limit']:
                msg = msg + "\nThe bid amount is greater than your Pre Qualified Upper Limit. Bid not registered. "
            elif int(bidamount) < auction_row['Lowest_Bid_Limit']:
                msg = msg + "\nBid less than lowest bid limit. Bid not registered."
            elif int(bidamount) > auction_row['Highest_Bidder_Amount']:
                print("\nBid greater than the highest bid. Bid registered.")
            if len(msg) == 0:
                # Update the databases if all the parameters are valid inputs.
                cur.execute(f"UPDATE AuctionItem SET Lowest_Bid_Limit = {int(bidamount)}, Highest_Bidder_Id = "
                            f"{int(bidderid)}, Highest_Bidder_Amount = {int(bidamount)} WHERE Item_Id = {int(itemid)} ")
                conn.commit()  # Save changes
                msg = "Successfully added record."

    except Exception:
        msg = "Error: Bid not registered."
        conn.rollback()
    finally:
        conn.close()
    return msg


if __name__ == "__main__":
    try:
        HOST, PORT = "localhost", 9999
        #	Create	the	server,	binding	to	localhost	on	port	9999
        server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)
        # Activate	the	server;	this	will	keep	running	until	you
        #	interrupt	the	program	with	Ctrl-C
        server.serve_forever()
    except server.error as e:
        print("Error:", e)
        exit(999)
    finally:
        server.close()
