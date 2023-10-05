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


import sqlite3

conn = sqlite3.connect('.auctionbidderDB.db')
cur = conn.cursor()

try:
    conn.execute('''Drop table AuctionItem''')
    # save changes
    conn.commit()
    print('AuctionItem table dropped.')
except:
    print('AuctionItem table did not exist.')

# create table in database
if (cur.execute('''CREATE TABLE AuctionItem(
Item_Id INTEGER NOT NULL,
Item_Name TEXT NOT NULL,
Item_Description TEXT NOT NULL,
Lowest_Bid_Limit INTEGER NOT NULL,
Highest_Bidder_Id INTEGER NOT NULL,
Highest_Bidder_Amount INTEGER NOT NULL,
CONSTRAINT _AuctionItemPK PRIMARY KEY (Item_Id)
);
''')):
    print("Table created successfully.")

# commit and save changes to database
conn.commit()
# Execute multiple commands at once
# Default data values
data = [(1, 'Holy Grail', 'A cup providing eternal youth.', 3000, 0, 0),
        (2, 'Excalibur', 'Legendary sword of King Arthur.', 100, 0, 0),
        (3, 'Rabbit of Caerbannog', 'A felled beast of unimaginable power.', 2000, 0, 0),
        (4, 'Dragon Egg', 'Just a dragon egg.', 5000, 0, 0),
        (5, 'Holy Hand Grenade of Antioch', 'A holy weapon once belonging to Brother Maynard.', 25000, 0, 0)]
cur.executemany('''Insert Into AuctionItem Values (?,?,?,?,?,?) ''', data)

# commit and save changes to database
conn.commit()

for row in cur.execute('Select * from AuctionItem;'):
    print(row)

# close database connection
conn.close()
print('Connection closed.')
