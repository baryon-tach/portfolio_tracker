import sqlite3
import os
import sys

# establish connection with db and run queries
# def resource_path(relative_path):
#     if hasattr(sys, '_MEIPASS'):
#         return os.path.join(sys._MEIPASS, relative_path)
#     return os.path.join(os.path.abspath("."), relative_path)

# db = resource_path("./portfolio.db")
# connection = sqlite3.connect(f"{db}")
target_dir = "~/Applications/AppData/Local/Tolio/db"

connection = sqlite3.connect(os.path.expanduser(target_dir + "/portfolio.db"))

cur = connection.cursor()

# create the necessary tables if it does not currently exist
def initiate_db():
    # securities table: security_id, name, ticker, amount_held, total_cost, cost_basis, number_long
    cur.execute('''CREATE TABLE IF NOT EXISTS Securities (security_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name TEXT NOT NULL UNIQUE, ticker TEXT UNIQUE NOT NULL, amount_held REAL, total_cost REAL,
    cost_basis REAL, number_long REAL);''')

    # transaction_names table: transaction_type_id, transaction_type, transaction_abbreviation
    cur.execute('''CREATE TABLE IF NOT EXISTS Transaction_names (transaction_type_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    transaction_type TEXT UNIQUE NOT NULL, transaction_abbreviation TEXT UNIQUE NOT NULL);''')
    # insert the default transactions: dispose (D) and acquire (A)
    try:
        cur.execute('''INSERT INTO Transaction_names (transaction_type, transaction_abbreviation) VALUES
        ("dispose", "D"), ("acquire", "A"), ("transfer_from", "TF"), ("transfer_to", "TT");''')
    except:
        pass

    # institutions table: institution_id, institution_name
    cur.execute('''CREATE TABLE IF NOT EXISTS Institutions (institution_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    institution_name TEXT UNIQUE NOT NULL);''')
    # insert the default institutions: computershare / fidelity
    try:
        cur.execute('''INSERT INTO Institutions (institution_name) VALUES ("Fidelity"),
        ("Computershare");''')
    except:
        pass

    # institutions_held table: institution_id, security_id, amount_held, total_cost, cost_basis, number_long
    cur.execute('''CREATE TABLE IF NOT EXISTS Institutions_held (institution_id INTEGER NOT NULL,
    security_id INTEGER NOT NULL, amount_held REAL, total_cost REAL, cost_basis REAL, number_long REAL,
    PRIMARY KEY (institution_id, security_id),
    FOREIGN KEY (institution_id) REFERENCES Institutions(institution_id),
    FOREIGN KEY (security_id) REFERENCES Securities(security_id));''')

    # transactions table: transaction_id, security_id, name, ticker, institution_id, timestamp, transaction_abbreviation, amount, price_USD
    cur.execute('''CREATE TABLE IF NOT EXISTS Transactions(transaction_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, security_id INTEGER NOT NULL,
    name TEXT NOT NULL, ticker TEXT NOT NULL, institution_id INTEGER NOT NULL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, transaction_abbreviation TEXT NOT NULL,
    amount REAL NOT NULL, price_USD REAL NOT NULL, transfer_from TEXT, transfer_to TEXT, age_transaction INTEGER, long REAL,
    FOREIGN KEY(institution_id) REFERENCES Institutions(institution_id)
    FOREIGN KEY(security_id) REFERENCES Securities(security_id),
    FOREIGN KEY(transaction_abbreviation) REFERENCES Transaction_names(transaction_abbreviation));''')

    connection.commit()

"""To input the transactions, there are the requirements for the insert
query but also the function that is used to insert the data must be able
to indentify if a security is new or not. If so, it will be routed to another
function that will input with the initiation process for the securities table.
With all of the initial values except for the identifiers as 0 or null.
For the graphic interface all of necessary inputs must be visible for the
user to enter."""

# determine if security exists
def check_security(name, ticker):
    name=name.capitalize()
    ticker=ticker.upper()
    security=cur.execute(f"SELECT * FROM Securities WHERE name='{name}' and ticker='{ticker}'")
    security=cur.fetchone()
    return security

# determine if institution exists
def check_institution(institution_name):
    institution_name=institution_name.capitalize()
    institution=cur.execute(f"SELECT * FROM Institutions WHERE institution_name='{institution_name}'")
    institution=cur.fetchone()
    return institution

# check amount of shares
def check_shares(name, ticker, trans_from):
    name=name.capitalize()
    ticker=ticker.upper()
    trans_from=trans_from.capitalize()

    security_id=cur.execute(f"SELECT security_id from Securities WHERE name='{name}' AND ticker='{ticker}'")
    security_id=cur.fetchone()[0]
    institution_id=cur.execute(f"SELECT institution_id from Institutions WHERE institution_name='{trans_from}'")
    institution_id=cur.fetchone()[0]

    shar=cur.execute(f"SELECT amount_held FROM Institutions_held WHERE institution_id='{institution_id}' AND security_id='{security_id}'")
    shar=cur.fetchone()
    return shar

# insert a new security in database: all is needed is name and ticker
def insert_security(name, ticker):
    name=name.capitalize()
    ticker=ticker.upper()
    cur.execute(f"INSERT INTO Securities (name, ticker) VALUES ('{name}', '{ticker}')")
    # print(f"Inserted new security - {name} - with ticker - {ticker}. ")
    connection.commit()

# insert a new institution in database, all is needed is the name
def insert_institution(institution_name):
    institution_name=institution_name.capitalize()
    cur.execute(f"INSERT INTO Institutions (institution_name) VALUES ('{institution_name}')")
    print(f"Inserted new institution - {institution_name}.")
    connection.commit()

# insert a new transaction type
def insert_transaction_type(new_transaction_type, new_transaction_abb):
    cur.execute(f'''INSERT INTO Transaction_names (transaction_type, transaction_abbreviation)
    VALUES ({new_transaction_type}, {new_transaction_abb})''')
    connection.commit()
    # most likely will never use

# insert a new transaction: security_id, name, ticker, institution_id, timestamp, transaction_abbreviation, amount, price_USD
def insert_transaction(name, ticker, institution, date_time, trans_type, shares, price):
    institution=institution.capitalize()
    institution_id=cur.execute(f"SELECT institution_id from Institutions WHERE institution_name='{institution}'")
    institution_id=cur.fetchone()[0]

    name=name.capitalize()
    ticker=ticker.upper()
    security_id=cur.execute(f"SELECT security_id from Securities WHERE name='{name}' AND ticker='{ticker}'")
    security_id=cur.fetchone()[0]
    if trans_type == 'A' or trans_type == 'TT':
        if len(date_time) == 0:
            cur.execute(f"INSERT INTO Transactions (security_id,name, ticker, institution_id, timestamp, transaction_abbreviation, amount, price_USD) VALUES ('{security_id}','{name}','{ticker}','{institution_id}', datetime(CURRENT_TIMESTAMP, 'localtime'),'{trans_type}','{shares}','{price}')")
            connection.commit()
        else:
            cur.execute(f"INSERT INTO Transactions (security_id,name, ticker, institution_id, timestamp, transaction_abbreviation, amount, price_USD) VALUES ('{security_id}','{name}','{ticker}','{institution_id}','{date_time}','{trans_type}','{shares}','{price}')")
            connection.commit()
    elif trans_type == 'D' or trans_type == 'TF':
        price=-price
        if len(date_time) == 0:
            cur.execute(f"INSERT INTO Transactions (security_id,name, ticker, institution_id, timestamp, transaction_abbreviation, amount, price_USD, long) VALUES ('{security_id}','{name}','{ticker}','{institution_id}', datetime(CURRENT_TIMESTAMP, 'localtime'),'{trans_type}','{shares}','{price}', '{shares}')")
            connection.commit()
        else:
            cur.execute(f"INSERT INTO Transactions (security_id,name, ticker, institution_id, timestamp, transaction_abbreviation, amount, price_USD, long) VALUES ('{security_id}','{name}','{ticker}','{institution_id}','{date_time}','{trans_type}','{shares}','{price}', '{shares}')")
            connection.commit()


# update tables
# update transaction age
def update_transaction_age():
    age=cur.execute('''SELECT transaction_id, timestamp,
    CASE
        WHEN strftime('%m', date('now')) > strftime('%m', date(timestamp)) THEN strftime('%Y', date('now')) - strftime('%Y', date(timestamp))
        WHEN strftime('%m', date('now')) = strftime('%m', date(timestamp)) THEN
            CASE
                WHEN strftime('%D', date('now')) >= strftime('%D', date(timestamp)) THEN strftime('%Y', date('now')) - strftime('%Y', date(timestamp))
                ELSE strftime('%Y', date('now')) - strftime('%Y', date(timestamp)) - 1
            END
    WHEN strftime('%m', date('now')) < strftime('%m', date(timestamp)) THEN strftime('%Y', date('now')) - strftime('%Y', date(timestamp)) - 1
    END AS 'age' FROM Transactions''')
    age=cur.fetchall()
    for id, time, aage in age:
        cur.execute(f"UPDATE Transactions SET age_transaction='{aage}' WHERE transaction_id='{id}'")
        connection.commit()
        # add the stocks that are long
        cur.execute(f"UPDATE Transactions SET long=(SELECT amount FROM Transactions WHERE age_transaction > 0 and transaction_abbreviation='A') WHERE transaction_id='{id}' AND transaction_abbreviation='A' AND age_transaction > 0")
        connection.commit()
    # make sure negative age is gone
    cur.execute(f"UPDATE Transactions SET age_transaction=0 WHERE age_transaction < 0")

    connection.commit()

# update securities
def update_securities():
    # create list of securities
    get_securities=cur.execute("SELECT security_id FROM securities;")
    get_securities=cur.fetchall()
    get_securities=[x[0] for x in get_securities]

    for security_id in get_securities:
        age=cur.execute(f"SELECT SUM(long) FROM Transactions WHERE security_id='{security_id}' ")
        age=cur.fetchall()
        age=[x[0] for x in age]
        cur.execute(f"UPDATE Securities SET number_long='{age[0]}' WHERE security_id='{security_id}'")

        amount=cur.execute(f"SELECT SUM(amount), SUM(price_USD), (SUM(price_USD)/SUM(amount)) FROM Transactions WHERE security_id='{security_id}'")
        amount=cur.fetchall()
        for sum_amount, sum_price, cost_basis in amount:
            cur.execute(f"UPDATE Securities SET amount_held='{sum_amount}', total_cost='{sum_price}', cost_basis='{round(cost_basis, 3)}' WHERE security_id='{security_id}'")

        connection.commit()

# update institutions held: institution_id, security_id, amount_held, total_cost, cost_basis, number_long
def update_institutions_held():
    get_institution_id=cur.execute(f"SELECT DISTINCT institution_id, security_id FROM Transactions")
    get_institution_id=cur.fetchall()
    for institution_id, security_id in get_institution_id:
        cur.execute(f"INSERT OR IGNORE INTO Institutions_held (institution_id, security_id) VALUES ('{institution_id}','{security_id}')")
        get_data=cur.execute(f"SELECT SUM(amount), SUM(price_USD), (SUM(price_USD)/(SUM(amount))), SUM(long) FROM Transactions WHERE institution_id='{institution_id}' AND security_id='{security_id}'")
        get_data=cur.fetchall()
        (amount_held, total_cost, cost_basis, age)=get_data[0]

        cur.execute(f"UPDATE Institutions_held SET amount_held='{amount_held}', total_cost='{total_cost}', cost_basis='{cost_basis}', number_long='{age}' WHERE institution_id='{institution_id}' AND security_id='{security_id}'")
    connection.commit()


# get transactions table for tree view
def get_transactions_table():
    get_trans=cur.execute("""SELECT
    t.transaction_id, t.name, t.ticker, i.institution_name, t.timestamp,
    t.transaction_abbreviation, t.transfer_from, t.transfer_to, t.price_USD, t.amount,
    t.age_transaction, t.long
    FROM Institutions as i INNER JOIN Transactions AS t ON i.institution_id=t.institution_id
    INNER JOIN Transaction_names AS tn ON t.transaction_abbreviation=tn.transaction_abbreviation""")
    get_trans=get_trans.fetchall()
    # print(get_trans)
    return get_trans

# get institutions_held table for tree view
def get_institutions_held_table():
    get_insta=cur.execute("""
    SELECT i.institution_name, s.name, ih.amount_held, ih.total_cost, ih.cost_basis,
    ih.number_long
    FROM Securities as s INNER JOIN Institutions_held AS ih ON s.security_id=ih.security_id
    INNER JOIN Institutions AS i USING(institution_id)

    """)
    get_insta=get_insta.fetchall()
    # print(get_insta)
    return get_insta

# get the securities table
def get_security_table():
    get_sec=cur.execute("""
    SELECT name, ticker, amount_held, total_cost, cost_basis, number_long
    FROM Securities
    """)
    return get_sec

# update table from transactions table
def update_table(*args):
    print(args)
    name=args[1].capitalize()
    ticker=args[2].upper()
    institution=args[3].capitalize()


    security_id=cur.execute(f"SELECT security_id FROM Securities WHERE ticker = '{ticker}' AND name = '{name}' ")
    security_id=security_id.fetchone()[0]
    institution_id=cur.execute(f"SELECT institution_id FROM Institutions WHERE institution_name='{institution}'")
    institution_id=institution_id.fetchone()[0]

    cur.execute(f"""UPDATE Transactions SET security_id = :sec_id, name = :name, ticker = :ticker, institution_id = :institution_id,
    timestamp = :timestamp, transaction_abbreviation = :trans_abb, amount = :amount,
    price_USD = :price, transfer_from = :trans_from ,transfer_to = :trans_to WHERE transaction_id = :trans_id
    """,{
    "sec_id": security_id,
    "name": name,
    "ticker": ticker,
    "institution_id": institution_id,
    "timestamp": args[4],
    "trans_abb": args[5],
    "amount": args[9],
    "price": args[8],
    "trans_from": args[6],
    "trans_to": args[7],
    "trans_id": args[0]

    })
    connection.commit()
    update_transaction_age()
    update_securities()
    update_institutions_held()

# delete transaction row
def delete_row(id):
    cur.execute(f"DELETE FROM Transactions WHERE transaction_id={id}")
    connection.commit()
    update_transaction_age()
    update_securities()
    update_institutions_held()

# stock split
def st_split(name, ticker, split:float):
    cur.execute(f"UPDATE Transactions SET amount=amount*{split} WHERE name='{name}' AND ticker='{ticker}' ")
    connection.commit()
    update_transaction_age()
    update_securities()
    update_institutions_held()



if __name__ =="__main__":
    initiate_db()
    update_transaction_age()
    update_securities()
    update_institutions_held()
