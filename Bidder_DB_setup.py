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
import Encryption

conn = sqlite3.connect('.auctionbidderDB.db')
cur = conn.cursor()

try:
    conn.execute('''Drop table Bidder''')
    #save changes
    conn.commit()
    print('Bidder table dropped.')
except:
    print('Bidder table did not exist.')

# create table in database
if (cur.execute('''CREATE TABLE Bidder(
Bidder_ID INTEGER PRIMARY KEY,
Bidder_Name TEXT NOT NULL,
Phone_Number TEXT NOT NULL,
Pre_Qualified_Upper_Limit INTEGER NOT NULL,
App_Role_Level INTEGER NOT NULL,
Login_Password TEXT NOT NULL
);
''')):
    print("Table created successfully.")

# commit and save changes to database
conn.commit()

# Provide default data for table.
data = [( str(Encryption.cipher.encrypt(b'James Bond').decode('utf-8')),
         str(Encryption.cipher.encrypt(b'111-222-007').decode('utf-8')), 300000, 3,
         str(Encryption.cipher.encrypt(b'test123').decode('utf-8'))),

        ( str(Encryption.cipher.encrypt(b'Tina Whitefield').decode('utf-8')),
         str(Encryption.cipher.encrypt(b'333-444-5555').decode('utf-8')), 2500000, 2,
         str(Encryption.cipher.encrypt(b'test654)').decode('utf-8'))),

        ( str(Encryption.cipher.encrypt(b'Tim Jones').decode('utf-8')),
         str(Encryption.cipher.encrypt(b'777-888-9999').decode('utf-8')), 125000, 1,
         str(Encryption.cipher.encrypt(b'test789').decode('utf-8'))),

        ( str(Encryption.cipher.encrypt(b'Jenny Smith').decode('utf-8')),
         str(Encryption.cipher.encrypt(b'3333-222-1111').decode('utf-8')), 10000, 2,
         str(Encryption.cipher.encrypt(b'test321').decode('utf-8'))),

        ( str(Encryption.cipher.encrypt(b'Mike Hatfield').decode('utf-8')),
         str(Encryption.cipher.encrypt(b'555-444-3333').decode('utf-8')), 25000, 1,
         str(Encryption.cipher.encrypt(b'test654').decode('utf-8'))),

        ( str(Encryption.cipher.encrypt(b'Steve Makers').decode('utf-8')),
         str(Encryption.cipher.encrypt(b'999-888-7777').decode('utf-8')), 7500, 3,
         str(Encryption.cipher.encrypt(b'test987').decode('utf-8')))
        ]

# Execute multiple commands at once
cur.executemany('Insert Into Bidder ( Bidder_Name , Phone_Number , Pre_Qualified_Upper_Limit , App_Role_Level , '
                'Login_Password ) Values(?,?,?,?,?)', data)
# commit and save changes to database
conn.commit()

for row in cur.execute('Select * from Bidder;'):
    print(row)

# close database connection
conn.close()
print('Connection closed.')