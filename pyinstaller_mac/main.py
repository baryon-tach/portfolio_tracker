from tkinter import *
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import re
from database_module import *
import os
import sys

# dynamically resize the canvas and the widgets on the main menu
class Dynamic_Canvas(Canvas):
    def __init__(self,parent,**kwargs):


         def resource_path(relative_path):
             if hasattr(sys, '_MEIPASS'):
                 return os.path.join(sys._MEIPASS, relative_path)
             return os.path.join(os.path.abspath("."), relative_path)

         Logo = resource_path("./images/iss056e162811.jpg")
         Canvas.__init__(self,parent,**kwargs)
         self.height = self.winfo_reqheight()
         self.width = self.winfo_reqwidth()

         self.image=Image.open(Logo)
         self.img_copy=self.image.copy()
         self.background_image=ImageTk.PhotoImage(self.image)
         self.create_image(0,0, anchor='nw', image=self.background_image)

         self.bind("<Configure>", self.on_resize)

    def on_resize(self,event):
        # resize image
        self.image=self.img_copy.resize((event.width, event.height))
        self.background_image=ImageTk.PhotoImage(self.image)
        self.create_image(0,0, anchor='nw', image=self.background_image)

        # determine the ratio of old width/height to new width/height
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height

        self.width = event.width
        self.height = event.height
        # resize the canvas
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        self.scale("all",0,0,wscale,hscale)



# transaction window after clicking on the add_transactions_button
def transaction_window():
    frame=Frame(root)
    frame.place(relwidth=1,relheight=1,relx=0,rely=0)

    # add message box for info in entry
    response=messagebox.askyesno("More Info?", "Would you like information regarding entering the transaction?")
    if response == 1:
        top=Toplevel()
        width=500
        height=500
        top.geometry(f"{str(width)}x{str(height)}")
        top.resizable(False,False)

        info='''~ Name of Security ~
        This refers to the name of stock, not the ticker.
        The program is not case sensitive when inputing the name,
        however please do make sure that the name is correct before entering.
        \n~ Ticker ~
        This is where you put the abbreviation of the stock.
        Similarly to the name, it is not case sensitive.
        \n~ Institution Name ~
        Same concept as "Name of Security."
        \n~ Time of Transaction ~
        This can be left blank if the transaction occured the same day.
        Otherwise please follow the following syntax: YYYY-MM-DD. Note if single
        digit month please add a zero. For example 2022-01-01.
        \n~ Amount of Shares ~
        This app supports fractional shares.
        \n~ Price in USD ~
        Please enter a float - do not enter the dollar sign. If you are selling
        the security make sure to make the number negative. If you are buying
        make sure the number is postive.
        \n~ Transaction Type ~
        This is seeking for the abbreviation for the transaction. For this
        selection the available are as follows:
        Dispose - please enter: D
        Aquire - please enter: A
        '''

        transaction_info=Label(top, text=info, anchor=CENTER, width=width)
        transaction_info.place(relx=0,rely=0,relwidth=1,relheight=1,)

    # create title
    title=Label(frame,text="Transaction Entry")
    title.place(relx=0.4,rely=0,relwidth=0.2,relheight=0.1)

    # labels: name, ticker, institution_name, time of transaction, amount, price_USD
    LABEL_RELY=0.1
    labels=["Name of Security:", "Ticker:", "Institution Name:", "Time of Transaction:", "Amount of Shares:", "Price in USD:", "Transaction Type:"]
    for i in labels:
        my_label=Label(frame,text=i,anchor=W)
        my_label.place(relx=0,rely=LABEL_RELY,relwidth=0.2,relheight=0.1)
        LABEL_RELY=LABEL_RELY+0.1

    # create entries and save the list as a dictionary and insert the transaction
    my_entries=[]
    def get_entry(labels,my_entries):
        entry_dic={}
        for i in range(len(my_entries)):
            entry_dic[labels[i]]=my_entries[i].get()

        # define insert message box function
        def insert_transaction_yes_no(entry_dic):
            text="Add transaction:\n"
            lis=list(entry_dic.items())
            for (key, value) in lis:
                if (key,value) != lis[-1]:
                    phrase="{} {}\n".format(key, value)
                    text+=phrase
                else:
                    phrase="{} {}".format(key,value)
                    text+=phrase

            yes_no=messagebox.askyesno("Add Transaction?", text)

            # verify if date syntax is correct
            def date_time_check(date_time):
                success=None
                date_regex=re.compile('\d\d\d\d-\d\d-\d\d')

                try:
                    date_search=date_regex.search(date_time)
                    date_search=date_search.group()
                    if len(str(date_search)) == 10 or len(date_time) == 0:
                        success=True
                        return success
                except:
                    if len(date_time) == 0:
                        success=True
                        return success
                    else:
                        success=False
                        return success

            # create function to make it automatically negative or positive given transaction type
            def change_sign(trans_type,shares,price):
                if trans_type =="A" and (shares < 0 or price < 0):
                    if shares < 0 and price < 0:
                        shares=shares*(-1)
                        price=price*(-1)
                        return shares, price
                    elif shares > 0 and price < 0:
                        price=price*(-1)
                        return shares, price
                    elif shares < 0 and price > 0:
                        shares=shares*(-1)
                        return shares, price
                elif trans_type=="D" and (shares > 0 or price > 0):
                    if shares > 0 and price > 0:
                        shares=shares*(-1)
                        price=price*(-1)
                        return shares, price
                    elif shares < 0 and price > 0:
                        price=price*(-1)
                        return shares, price
                    elif shares > 0 and price < 0:
                        shares=shares*(-1)
                        return shares, price
                else:
                    return shares, price

            # function to clear after inserting
            def clear(frame):
                for widget in frame.winfo_children():
                    if isinstance(widget, Entry):
                        widget.delete(0,END)

            if yes_no == 1:
                try:
                    # check to see if are numbers
                    shares=float(entry_dic["Amount of Shares:"])
                    price=float(entry_dic["Price in USD:"])
                    # check to see if right type of entry A or D
                    trans_type=str(entry_dic["Transaction Type:"]).upper()
                    # date_time variable
                    date_time=entry_dic["Time of Transaction:"]

                    if len(trans_type)==1 and (trans_type=="A" or trans_type=="D"):
                        shares, price = change_sign(trans_type,shares, price)

                        if date_time_check(date_time) == True:
                            name=str(entry_dic["Name of Security:"]).capitalize()
                            ticker=str(entry_dic["Ticker:"]).upper()
                            institution=str(entry_dic["Institution Name:"]).capitalize()
                            date_time=date_time
                            trans_type=trans_type
                            shares=shares
                            price=price

                            insert_transaction(name, ticker, institution, date_time, trans_type, shares, price)
                            clear(frame)
                            update_transaction_age()
                            update_securities()
                            update_institutions_held()
                        else:
                            messagebox.showerror("Entry Error", 'Invalid entry for "Time of Transaction:" Please try again.')

                    else:
                        messagebox.showerror("Entry Error", 'Invalid entry for "Transaction Type:" Please try again. Consult the manual if needed. Note: Valid entries are A (aquire) and D (dispose).')

                except:
                    messagebox.showerror("Entry Error", '"Amount of Shares:" or "Price in USD:" is not a number. Please try again.')


        # make sure all is entered except for time of transaction
        for key,value in entry_dic.items():
            value=str(value).replace(" ","")
            if (value=="" or value==None) and key != "Time of Transaction:":
                messagebox.showerror("Missing Fields", f"The {key} field is missing a value.")
                break
            else:
                name=str(entry_dic["Name of Security:"])
                ticker=str(entry_dic["Ticker:"])
                institution_name=str(entry_dic["Institution Name:"])
                check_sec=check_security(name,ticker)
                check_insta=check_institution(institution_name)
                if check_sec == None and check_insta == None:
                    response_add=messagebox.askyesno("New Security and Insitution", f"Security name: {name} | Ticker name: {ticker} is a new security and {institution_name} is a new institution. Would you like to add it?")
                    if response_add == 1:
                        # insert_security(name,ticker) and institution
                        insert_security(name,ticker)
                        insert_institution(institution_name)
                        messagebox.showinfo("Security and Institution Added", f"{name} ({ticker}) was added with the institution, {institution_name} to the database.")
                        insert_transaction_yes_no(entry_dic)

                        break
                    else:
                        messagebox.showinfo("Security and Institution Not Added", f"{name} ({ticker}) from {institution_name} was NOT added to the database.")
                        break
                elif check_sec == None:
                    response_add=messagebox.askyesno("New Security", f"Security name: {name} | Ticker name: {ticker} is a new security. Would you like to add it?")
                    if response_add == 1:
                        # insert_security(name,ticker)
                        insert_security(name,ticker)
                        messagebox.showinfo("Security Added", f"{name} ({ticker}) was added to the database.")
                        insert_transaction_yes_no(entry_dic)

                        break
                    else:
                        messagebox.showinfo("Security Not Added", f"{name} ({ticker}) was NOT added to the database.")
                        break
                elif check_insta == None:
                    response_add=messagebox.askyesno("New Insitution", f"Institution name: {institution_name} is a new institution. Would you like to add it?")
                    if response_add == 1:
                        # insert institution
                        insert_institution(institution_name)
                        messagebox.showinfo("Institution Added", f"{institution_name} was added to the database.")
                        insert_transaction_yes_no(entry_dic)

                        break
                    else:
                        messagebox.showinfo("Institution Not Added", f"{institution_name} was NOT added to the database.")
                        break

                else:
                    insert_transaction_yes_no(entry_dic)

                    break


    ENTRY_RELY=0.1
    for i in range(7):
        my_entry=Entry(frame,bd=3,bg="white")
        my_entry.place(relx=0.2,rely=ENTRY_RELY,relwidth=0.8,relheight=0.1)
        ENTRY_RELY=ENTRY_RELY+0.1
        my_entries.append(my_entry)

    # entry button
    entry_button=Button(frame, text="Enter", command= lambda: get_entry(labels,my_entries))
    entry_button.place(relx=0,rely=0.8,relwidth=1,relheight=0.1)


    # return to main menu and exit button
    return_main_button=Button(frame, text="Main Menu", command=frame.destroy)
    exit_button=Button(frame, text="Exit Program", command=root.quit)

    return_main_button.place(relx=0,rely=0.9,relwidth=0.2,relheight=0.1)
    exit_button.place(relx=0.8,rely=0.9,relwidth=0.2,relheight=0.1)





def data_window():
    frame=Frame(root)
    frame.place(relwidth=1,relheight=1,relx=0,rely=0)
    style=ttk.Style()
    style.theme_use('default')
    style.configure("Treeview",background="#D3D3D3",foreground="black",
        rowheight=25,fieldbackground="#D3D3D3")
    # change selected color
    style.map('Treeview', background=[('selected', "#347083")])
    # create treeview
    tree_frame=Frame(frame)
    tree_frame.place(relx=0,rely=0.05,relheight=0.65,relwidth=1, anchor=NW)
    # create tree
    my_tree=ttk.Treeview(tree_frame, selectmode="extended")
    my_tree.place(relx=0,rely=0,relheight=1,relwidth=1, anchor=NW)
    # scrollbar
    tree_scroll=Scrollbar(tree_frame,orient="vertical",command=my_tree.yview)
    tree_scroll.pack(side=RIGHT,fill=Y)
    # configure scrollbar
    my_tree.configure(yscrollcommand=tree_scroll.set)
    # create strip row tags
    my_tree.tag_configure('oddrow',background='white')
    my_tree.tag_configure('evenrow',background='lightblue')

    # standardized function to get database info
    def query_database(query_db):
        global count
        count=0
        records=query_db()
        for record in records:
            rec=[record[i] for i in range(len(record))]
            rec=tuple(rec)

            if count % 2 == 0:
                my_tree.insert(parent='',index='end',text="",values=rec,tags=('evenrow',))
            else:
                my_tree.insert(parent='',index='end',text="",values=rec,tags=('oddrow',))
            count+=1


    # function to select record
    def select_record(e,entry_dic,*args):
        for entry in entry_dic.values():
            entry.config(state="normal")
            entry.delete(0,END)
        # grab records
        selected=my_tree.focus()
        # grab record value
        values=my_tree.item(selected,'values')
        count=0

        if ("Split" in args):
            for name,entry in entry_dic.items():
                if name == "n_entry":
                    entry.insert(0,values[1])
                elif name == "ticker_entry":
                    entry.insert(0,values[2])
                else:
                    continue
        else:
            for name,entry in entry_dic.items():
                if name == "id_entry" or name == "age_entry" or name == "long_entry":
                    entry.insert(0,values[count])
                    entry.config(state="disabled")
                    count+=1
                else:
                    entry.insert(0,values[count])
                    count+=1


    def update_record(entry_dic):
        selected=my_tree.focus()

        id_entry=entry_dic["id_entry"]
        id_entry.config(state="normal")

        id_value=id_entry.get()
        n_value=entry_dic["n_entry"].get()
        ticker_value=entry_dic["ticker_entry"].get()
        institution_value=entry_dic["institution_entry"].get()
        date_value=entry_dic["date_entry"].get()
        type_value=entry_dic["type_entry"].get()
        from_value=entry_dic["from_entry"].get()
        to_value=entry_dic["to_entry"].get()
        price_value=entry_dic["price_entry"].get()
        amount_value=entry_dic["amount_entry"].get()
        age_value=entry_dic["age_entry"].get()
        long_value=entry_dic["long_entry"].get()


        my_tree.item(selected,text="",values=(
        id_value,
        n_value,
        ticker_value,
        institution_value,
        date_value,
        type_value,
        from_value,
        to_value,
        price_value,
        amount_value,
        age_value,
        long_value

        ))
        id_entry.delete(0,END)
        entry_dic["n_entry"].delete(0,END)
        entry_dic["ticker_entry"].delete(0,END)
        entry_dic["institution_entry"].delete(0,END)
        entry_dic["date_entry"].delete(0,END)
        entry_dic["type_entry"].delete(0,END)
        entry_dic["from_entry"].delete(0,END)
        entry_dic["to_entry"].delete(0,END)
        entry_dic["price_entry"].delete(0,END)
        entry_dic["amount_entry"].delete(0,END)
        entry_dic["age_entry"].delete(0,END)
        entry_dic["long_entry"].delete(0,END)

        update_table(
        id_value,
        n_value,
        ticker_value,
        institution_value,
        date_value,
        type_value,
        from_value,
        to_value,
        price_value,
        amount_value,
        age_value,
        long_value

        )

    # remove all records
    def remove_all():
        for record in my_tree.get_children():
            my_tree.delete(record)


    def stock_split(entry_dic):
        selected=my_tree.focus()

        n_value=(entry_dic["n_entry"].get()).capitalize()
        ticker_value=(entry_dic["ticker_entry"].get()).upper()
        split_value=float(entry_dic["split_entry"].get())

        my_tree.item(selected,text="",values=(
        n_value,
        ticker_value,
        split_value,
        ))

        entry_dic["n_entry"].delete(0,END)
        entry_dic["ticker_entry"].delete(0,END)
        entry_dic["split_entry"].delete(0,END)

        st_split(
        n_value,
        ticker_value,
        split_value,
        )
        remove_all()
        query_database(get_transactions_table)

        messagebox.showinfo("Splitted!", "The stock you have chosen has been splitted.")


    def delete_record(entry_dic):
        selected=my_tree.focus()

        id_entry=entry_dic["id_entry"]
        id_entry.config(state="normal")

        id_value=id_entry.get()

        x=my_tree.selection()[0]
        my_tree.delete(x)


        id_entry.delete(0,END)
        entry_dic["n_entry"].delete(0,END)
        entry_dic["ticker_entry"].delete(0,END)
        entry_dic["institution_entry"].delete(0,END)
        entry_dic["date_entry"].delete(0,END)
        entry_dic["type_entry"].delete(0,END)
        entry_dic["from_entry"].delete(0,END)
        entry_dic["to_entry"].delete(0,END)
        entry_dic["price_entry"].delete(0,END)
        entry_dic["amount_entry"].delete(0,END)
        entry_dic["age_entry"].delete(0,END)
        entry_dic["long_entry"].delete(0,END)

        delete_row(id_value)
        messagebox.showinfo("Deleted!", "Your record has been deleted.")


    # different windows
    def transactions_window():
        # add columns for transactions
        my_tree['columns']=("ID", "Name","Ticker", "Institution","Date","Type","From","To","Price","Amount","Age","Long" )
        # format columns
        my_tree.column("#0", width=0,stretch=NO)
        columns=["ID", "Name","Ticker", "Institution","Date","Type","From","To","Price","Amount","Age","Long" ]
        for i in columns:
            my_tree.column(f"{i}", anchor=CENTER ,width=0)
        # create headings
        my_tree.heading("#0",text="",anchor=W)
        for i in columns:
            my_tree.heading(f"{i}",text=f"{i}",anchor=W)

        count=0
        count1=0
        # add record entry boxes
        data_frame=LabelFrame(frame,text="Record")
        data_frame.place(relx=0,rely=0.7,relheight=0.2,relwidth=1,anchor=NW)

        # on the top
        id_label=Label(data_frame,text="ID")
        id_label.place(relx=0,rely=0,relheight=0.4,relwidth=0.06,anchor=NW)
        id_entry=Entry(data_frame)
        id_entry.place(relx=0.06,rely=0,relheight=0.4,relwidth=0.1,anchor=NW)

        n_label=Label(data_frame,text="Name")
        n_label.place(relx=0.16,rely=0,relheight=0.4,relwidth=0.06,anchor=NW)
        n_entry=Entry(data_frame)
        n_entry.place(relx=0.22,rely=0,relheight=0.4,relwidth=0.1,anchor=NW)

        ticker_label=Label(data_frame,text="Ticker")
        ticker_label.place(relx=0.32,rely=0,relheight=0.4,relwidth=0.06,anchor=NW)
        ticker_entry=Entry(data_frame)
        ticker_entry.place(relx=0.38,rely=0,relheight=0.4,relwidth=0.1,anchor=NW)

        institution_label=Label(data_frame,text="Institution")
        institution_label.place(relx=0.48,rely=0,relheight=0.4,relwidth=0.1,anchor=NW)
        institution_entry=Entry(data_frame)
        institution_entry.place(relx=0.58,rely=0,relheight=0.4,relwidth=0.1,anchor=NW)

        date_label=Label(data_frame,text="Date")
        date_label.place(relx=0.68,rely=0,relheight=0.4,relwidth=0.06,anchor=NW)
        date_entry=Entry(data_frame)
        date_entry.place(relx=0.74,rely=0,relheight=0.4,relwidth=0.1,anchor=NW)

        type_label=Label(data_frame,text="Type")
        type_label.place(relx=0.84,rely=0,relheight=0.4,relwidth=0.06,anchor=NW)
        type_entry=Entry(data_frame)
        type_entry.place(relx=0.9,rely=0,relheight=0.4,relwidth=0.1,anchor=NW)

        # on the bottom
        from_label=Label(data_frame,text="From")
        from_label.place(relx=0,rely=0.6,relheight=0.4,relwidth=0.06,anchor=NW)
        from_entry=Entry(data_frame)
        from_entry.place(relx=0.06,rely=0.6,relheight=0.4,relwidth=0.1,anchor=NW)

        to_label=Label(data_frame,text="To")
        to_label.place(relx=0.16,rely=0.6,relheight=0.4,relwidth=0.06,anchor=NW)
        to_entry=Entry(data_frame)
        to_entry.place(relx=0.22,rely=0.6,relheight=0.4,relwidth=0.1,anchor=NW)

        price_label=Label(data_frame,text="Price")
        price_label.place(relx=0.32,rely=0.6,relheight=0.4,relwidth=0.06,anchor=NW)
        price_entry=Entry(data_frame)
        price_entry.place(relx=0.38,rely=0.6,relheight=0.4,relwidth=0.1,anchor=NW)

        amount_label=Label(data_frame,text="Amount")
        amount_label.place(relx=0.48,rely=0.6,relheight=0.4,relwidth=0.1,anchor=NW)
        amount_entry=Entry(data_frame)
        amount_entry.place(relx=0.58,rely=0.6,relheight=0.4,relwidth=0.1,anchor=NW)

        age_label=Label(data_frame,text="Age")
        age_label.place(relx=0.68,rely=0.6,relheight=0.4,relwidth=0.06,anchor=NW)
        age_entry=Entry(data_frame)
        age_entry.place(relx=0.74,rely=0.6,relheight=0.4,relwidth=0.1,anchor=NW)

        long_label=Label(data_frame,text="Long")
        long_label.place(relx=0.84,rely=0.6,relheight=0.4,relwidth=0.06,anchor=NW)
        long_entry=Entry(data_frame)
        long_entry.place(relx=0.9,rely=0.6,relheight=0.4,relwidth=0.1,anchor=NW)

        # dictionary of entries
        transaction_entries={"id_entry":id_entry,"n_entry":n_entry,"ticker_entry":ticker_entry,
        "institution_entry":institution_entry,"date_entry":date_entry,"type_entry":type_entry,
        "from_entry":from_entry,"to_entry":to_entry,"price_entry":price_entry,"amount_entry":amount_entry,
        "age_entry":age_entry,"long_entry":long_entry}
        # insert transactions table
        query_database(get_transactions_table)
        # add buttons
        button_frame=LabelFrame(frame,text="Commands")
        button_frame.place(relx=0,rely=0.9,relheight=0.1,relwidth=1,anchor=NW)

        update_button=Button(button_frame,text="Update Record",command=lambda:update_record(transaction_entries))
        update_button.place(relwidth=0.20)

        rm_rec_button=Button(button_frame,text="Remove Record",command=lambda:delete_record(transaction_entries))
        rm_rec_button.place(relx=0.25,relwidth=0.20)

        mm_button=Button(button_frame,text="Main Menu",command=frame.destroy)
        mm_button.place(relx=0.5,relwidth=0.20)

        ex_button=Button(button_frame,text="Exit Program",command=root.destroy)
        ex_button.place(relx=0.75,relwidth=0.20)
        # bind the treeview
        my_tree.bind("<ButtonRelease-1>", lambda event: select_record(event,transaction_entries))


    def institutions_held_window():
        # add columns for transactions
        my_tree['columns']=("Institution", "Security", "Amount", "Total Cost", "Cost Basis", "Number Long" )
        # format columns
        my_tree.column("#0", width=0,stretch=NO)
        columns=["Institution", "Security", "Amount", "Total Cost", "Cost Basis", "Number Long"]
        for i in columns:
            my_tree.column(f"{i}", anchor=CENTER ,width=0)
        # create headings
        my_tree.heading("#0",text="",anchor=W)
        for i in columns:
            my_tree.heading(f"{i}",text=f"{i}",anchor=W)


        # add record entry boxes
        data_frame=LabelFrame(frame,text="Record")
        data_frame.place(relx=0,rely=0.7,relheight=0.2,relwidth=1,anchor=NW)

        # on the top
        institution_label=Label(data_frame,text="Institution")
        institution_label.place(relx=0,rely=0,relheight=0.4,relwidth=0.1,anchor=NW)
        institution_entry=Entry(data_frame)
        institution_entry.place(relx=0.1,rely=0,relheight=0.4,relwidth=0.2,anchor=NW)

        security_label=Label(data_frame,text="Security")
        security_label.place(relx=0.3,rely=0,relheight=0.4,relwidth=0.1,anchor=NW)
        security_entry=Entry(data_frame)
        security_entry.place(relx=0.4,rely=0,relheight=0.4,relwidth=0.2,anchor=NW)

        amount_label=Label(data_frame,text="Amount")
        amount_label.place(relx=0.6,rely=0,relheight=0.4,relwidth=0.1,anchor=NW)
        amount_entry=Entry(data_frame)
        amount_entry.place(relx=0.7,rely=0,relheight=0.4,relwidth=0.2,anchor=NW)


        # on the bottom

        total_cost_label=Label(data_frame,text="Total Cost")
        total_cost_label.place(relx=0,rely=0.6,relheight=0.4,relwidth=0.1,anchor=NW)
        total_cost_entry=Entry(data_frame)
        total_cost_entry.place(relx=0.1,rely=0.6,relheight=0.4,relwidth=0.2,anchor=NW)

        cost_basis_label=Label(data_frame,text="Cost Basis")
        cost_basis_label.place(relx=0.3,rely=0.6,relheight=0.4,relwidth=0.1,anchor=NW)
        cost_basis_entry=Entry(data_frame)
        cost_basis_entry.place(relx=0.4,rely=0.6,relheight=0.4,relwidth=0.2,anchor=NW)

        number_long_label=Label(data_frame,text="Long")
        number_long_label.place(relx=0.6,rely=0.6,relheight=0.4,relwidth=0.1,anchor=NW)
        number_long_entry=Entry(data_frame)
        number_long_entry.place(relx=0.7,rely=0.6,relheight=0.4,relwidth=0.2,anchor=NW)

        # dictionary of entries
        transaction_entries={"institution_entry":institution_entry, "security_entry":security_entry,
        "amount_entry":amount_entry, "total_cost_entry":total_cost_entry, "cost_basis_entry":cost_basis_entry,
        "number_long_entry":number_long_entry}

        # insert transactions table
        query_database(get_institutions_held_table)
        # add buttons
        button_frame=LabelFrame(frame,text="Commands")
        button_frame.place(relx=0,rely=0.9,relheight=0.1,relwidth=1,anchor=NW)

        mm_button=Button(button_frame,text="Main Menu",command=frame.destroy)
        mm_button.place(relx=0,relwidth=0.20)

        ex_button=Button(button_frame,text="Exit Program",command=root.destroy)
        ex_button.place(relx=0.8,relwidth=0.20)

        # bind the treeview
        my_tree.bind("<ButtonRelease-1>", lambda event: select_record(event,transaction_entries))


    # create securities table
    def securities_window():
        # add columns for transactions
        my_tree['columns']=("Security", "Ticker", "Amount", "Total Cost", "Cost Basis", "Number Long" )
        # format columns
        my_tree.column("#0", width=0,stretch=NO)
        columns=["Security", "Ticker", "Amount", "Total Cost", "Cost Basis", "Number Long"]
        for i in columns:
            my_tree.column(f"{i}", anchor=CENTER ,width=0)
        # create headings
        my_tree.heading("#0",text="",anchor=W)
        for i in columns:
            my_tree.heading(f"{i}",text=f"{i}",anchor=W)


        # add record entry boxes
        data_frame=LabelFrame(frame,text="Record")
        data_frame.place(relx=0,rely=0.7,relheight=0.2,relwidth=1,anchor=NW)

        # on the top
        security_label=Label(data_frame,text="Security")
        security_label.place(relx=0,rely=0,relheight=0.4,relwidth=0.1,anchor=NW)
        security_entry=Entry(data_frame)
        security_entry.place(relx=0.1,rely=0,relheight=0.4,relwidth=0.2,anchor=NW)

        ticker_label=Label(data_frame,text="Ticker")
        ticker_label.place(relx=0.3,rely=0,relheight=0.4,relwidth=0.1,anchor=NW)
        ticker_entry=Entry(data_frame)
        ticker_entry.place(relx=0.4,rely=0,relheight=0.4,relwidth=0.2,anchor=NW)

        amount_label=Label(data_frame,text="Amount")
        amount_label.place(relx=0.6,rely=0,relheight=0.4,relwidth=0.1,anchor=NW)
        amount_entry=Entry(data_frame)
        amount_entry.place(relx=0.7,rely=0,relheight=0.4,relwidth=0.2,anchor=NW)


        # on the bottom

        total_cost_label=Label(data_frame,text="Total Cost")
        total_cost_label.place(relx=0,rely=0.6,relheight=0.4,relwidth=0.1,anchor=NW)
        total_cost_entry=Entry(data_frame)
        total_cost_entry.place(relx=0.1,rely=0.6,relheight=0.4,relwidth=0.2,anchor=NW)

        cost_basis_label=Label(data_frame,text="Cost Basis")
        cost_basis_label.place(relx=0.3,rely=0.6,relheight=0.4,relwidth=0.1,anchor=NW)
        cost_basis_entry=Entry(data_frame)
        cost_basis_entry.place(relx=0.4,rely=0.6,relheight=0.4,relwidth=0.2,anchor=NW)

        number_long_label=Label(data_frame,text="Long")
        number_long_label.place(relx=0.6,rely=0.6,relheight=0.4,relwidth=0.1,anchor=NW)
        number_long_entry=Entry(data_frame)
        number_long_entry.place(relx=0.7,rely=0.6,relheight=0.4,relwidth=0.2,anchor=NW)

        # dictionary of entries
        transaction_entries={"security_entry":security_entry, "ticker_entry":ticker_entry,
        "amount_entry":amount_entry, "total_cost_entry":total_cost_entry, "cost_basis_entry":cost_basis_entry,
        "number_long_entry":number_long_entry}

        # insert transactions table
        query_database(get_security_table)
        # add buttons
        button_frame=LabelFrame(frame,text="Commands")
        button_frame.place(relx=0,rely=0.9,relheight=0.1,relwidth=1,anchor=NW)

        mm_button=Button(button_frame,text="Main Menu",command=frame.destroy)
        mm_button.place(relx=0,relwidth=0.20)

        ex_button=Button(button_frame,text="Exit Program",command=root.destroy)
        ex_button.place(relx=0.8,relwidth=0.20)

        # bind the treeview
        my_tree.bind("<ButtonRelease-1>", lambda event: select_record(event,transaction_entries))



    # stock split window
    def stock_split_window():
        # add columns for transactions
        my_tree['columns']=("ID", "Name","Ticker", "Institution","Date","Type","From","To","Price","Amount","Age","Long" )
        # format columns
        my_tree.column("#0", width=0,stretch=NO)
        columns=["ID", "Name","Ticker", "Institution","Date","Type","From","To","Price","Amount","Age","Long" ]
        for i in columns:
            my_tree.column(f"{i}", anchor=CENTER ,width=0)
        # create headings
        my_tree.heading("#0",text="",anchor=W)
        for i in columns:
            my_tree.heading(f"{i}",text=f"{i}",anchor=W)

        count=0
        count1=0
        # add record entry boxes
        data_frame=LabelFrame(frame,text="Record")
        data_frame.place(relx=0,rely=0.7,relheight=0.2,relwidth=1,anchor=NW)

        # on the top

        n_label=Label(data_frame,text="Name:")
        n_label.place(relx=0,rely=0,relheight=0.4,relwidth=0.2,anchor=NW)
        n_entry=Entry(data_frame)
        n_entry.place(relx=0.2,rely=0,relheight=0.4,relwidth=0.25,anchor=NW)

        ticker_label=Label(data_frame,text="Ticker:")
        ticker_label.place(relx=0.45,rely=0,relheight=0.4,relwidth=0.2,anchor=NW)
        ticker_entry=Entry(data_frame)
        ticker_entry.place(relx=0.65,rely=0,relheight=0.4,relwidth=0.25,anchor=NW)


        # on the bottom
        split_label=Label(data_frame,text="Split Amount (?:1):")
        split_label.place(relx=0,rely=0.6,relheight=0.4,relwidth=0.3,anchor=NW)
        split_entry=Entry(data_frame)
        split_entry.place(relx=0.3,rely=0.6,relheight=0.4,relwidth=0.5,anchor=NW)


        # dictionary of entries
        transaction_entries={"n_entry":n_entry,"ticker_entry":ticker_entry,
        "split_entry":split_entry,}
        # insert transactions table
        query_database(get_transactions_table)
        # add buttons
        button_frame=LabelFrame(frame,text="Commands")
        button_frame.place(relx=0,rely=0.9,relheight=0.1,relwidth=1,anchor=NW)

        mm_button=Button(button_frame,text="Main Menu",command=frame.destroy)
        mm_button.place(relx=0,relwidth=0.20)

        split_button=Button(button_frame,text="Split",command=lambda:stock_split(transaction_entries))
        split_button.place(relx=0.4, relwidth=0.2)


        ex_button=Button(button_frame,text="Exit Program",command=root.destroy)
        ex_button.place(relx=0.8,relwidth=0.20)

        # bind the treeview
        my_tree.bind("<ButtonRelease-1>", lambda event: select_record(event,transaction_entries,"Split"))









    # drop down menu to change table within the database that is being showcased
    def selected(event):
        myLabel=Label(frame,text=clicked.get())
        if clicked.get() == "Transactions":
            remove_all()
            transactions_window()
        elif clicked.get() == "Institutions Held":
            remove_all()
            institutions_held_window()
        elif clicked.get() == "Securities":
            remove_all()
            securities_window()
        elif clicked.get() == "Stock Split":
            remove_all()
            stock_split_window()




    options=[
        "Transactions",
        "Institutions Held",
        "Securities",
        "Stock Split"
    ]
    clicked=StringVar()
    clicked.set(options[0])
    # get the initial window
    if clicked.get()=="Transactions":
        transactions_window()
    drop=OptionMenu(frame,clicked,*options,command=selected)
    drop.place(relx=0,rely=0,relheight=0.05,relwidth=1)





def transfer_window():
    frame=Frame(root)
    frame.place(relwidth=1,relheight=1,relx=0,rely=0)

    my_entries=[]
    def get_entry(labels,my_entries):
        entry_dic={}
        for i in range(len(my_entries)):
            entry_dic[labels[i]]=my_entries[i].get()

        # variables
        trans_to=entry_dic["Transfer To:"]
        check_trans_to=check_institution(trans_to)
        trans_from=entry_dic["Transfer From:"]
        check_trans_from=check_institution(trans_from)
        name = entry_dic["Name of Security:"]
        ticker = entry_dic["Ticker:"]
        check_amount=check_shares(name, ticker, trans_from)
        check_sec=check_security(name, ticker)
        org_cost = float(entry_dic["Original Cost:"])

        # function to clear after inserting
        def clear(frame):
            for widget in frame.winfo_children():
                if isinstance(widget, Entry):
                    widget.delete(0,END)


        # function for inserting with message
        def insert_transaction_yes_no(entry_dic, trans_type, trans_f_t):
            text="Add transaction:\n"
            lis=list(entry_dic.items())
            for (key, value) in lis:
                if (key,value) != lis[-1]:
                    phrase="{} {}\n".format(key, value)
                    text+=phrase
                else:
                    phrase="{} {}".format(key,value)
                    text+=phrase

            yes_no=messagebox.askyesno("Add Transaction?", text)
            if yes_no == 1:
                insert_transaction(entry_dic["Name of Security:"], entry_dic["Ticker:"], trans_f_t, "", trans_type, shares, org_cost )
                clear(frame)

        # function for inserting institution
        def insert_institution_yes_no(institution):
            text="Add Institution - " + institution
            yes_no=messagebox.askyesno("Add Institution?", text)
            if yes_no==1:
                insert_institution(institution)


        # check to see if security, ticker, amount, and institution exists
        if check_amount == None:
            check_amount=0
        try:
            if float(entry_dic["Amount:"]) <= float(check_amount[0]):
                if check_sec != None:
                    if check_trans_to != None:
                        if check_trans_from != None:
                            # insert transfer from
                            trans_type="TF"
                            shares=float(entry_dic["Amount:"])
                            if shares < 0:
                                insert_transaction_yes_no(entry_dic, trans_type, trans_from)
                            else:
                                shares=shares*-1
                                insert_transaction_yes_no(entry_dic, trans_type, trans_from)
                            # insert transfer to
                            trans_type="TT"
                            shares=float(entry_dic["Amount:"])
                            if shares > 0:
                                insert_transaction_yes_no(entry_dic, trans_type, trans_to)
                            else:
                                shares=shares*-1
                                insert_transaction_yes_no(entry_dic, trans_type, trans_to)
                        else:
                            insert_institution_yes_no(trans_from)
                    else:
                        add_inst=f"Add {entry_dic['Transfer To:']}?"
                        yes_no_I=messagebox.askyesno("Add Institution?", add_inst)
                        if yes_no_I == 1:
                            insert_institution(entry_dic["Transfer To:"])
                            if check_trans_from != None:
                                # insert transfer from
                                trans_type="TF"
                                shares=float(entry_dic["Amount:"])
                                if shares < 0:
                                    insert_transaction_yes_no(entry_dic)
                                else:
                                    shares=shares*-1
                                    insert_transaction_yes_no(entry_dic)
                                # insert transfer to
                                trans_type="TT"
                                shares=float(entry_dic["Amount:"])
                                if shares > 0:
                                    insert_transaction_yes_no(entry_dic)
                                else:
                                    shares=shares*-1
                                    insert_transaction_yes_no(entry_dic)
                            else:
                                insert_institution_yes_no(trans_to)
                else:
                    # print("Invalid name or ticker.")
                    messagebox.showerror("Error", "Invalid name or ticker.")
            else:
                # print("number too large")
                messagebox.showerror("Error", "Amount entered is too large.")
            update_transaction_age()
            update_securities()
            update_institutions_held()
        except:
            # print("Amount entered is not a number")
            messagebox.showerror("Error", "Amount entered is not a number.")














    # label names: security name, ticker, amount, transfer from, transfer to, date, enter
    LABEL_RELY=0.1
    labels=["Name of Security:", "Ticker:", "Amount:", "Transfer From:", "Transfer To:", "Date:", "Original Cost:"]
    for i in labels:
        my_label=Label(frame,text=i,anchor=W)
        my_label.place(relx=0,rely=LABEL_RELY,relwidth=0.2,relheight=0.1)
        LABEL_RELY=LABEL_RELY+0.1


    ENTRY_RELY=0.1
    for i in range(len(labels)):
        my_entry=Entry(frame,bd=3,bg="white")
        my_entry.place(relx=0.2, rely=ENTRY_RELY, relwidth=0.8, relheight=0.1)
        ENTRY_RELY=ENTRY_RELY+0.1
        my_entries.append(my_entry)

    # add exit, return to main menu, and enter buttons
    return_main_button=Button(frame, text="Main Menu", command=frame.destroy)
    exit_button=Button(frame, text="Exit Program", command=root.quit)
    enter_button=Button(frame, text="Enter", command=lambda: get_entry(labels, my_entries))

    return_main_button.place(relx=0,rely=0.9,relwidth=0.2,relheight=0.1)
    exit_button.place(relx=0.8,rely=0.9,relwidth=0.2,relheight=0.1)
    enter_button.place(relx=0.2, rely=0.9, relwidth=0.6, relheight=0.1)





# test function when running this script as main
def main():
    global root
    root = Tk()
    WIDTH=900
    HEIGHT=500


    TITLE="Portfolio Tracker"

    root.title(f"{TITLE}")
    root.geometry(f"{str(WIDTH)}x{str(HEIGHT)}")
    root.configure(background="black")
    root.minsize(WIDTH,HEIGHT)

    mycanvas = Dynamic_Canvas(root,width=WIDTH, height=HEIGHT, highlightthickness=0)
    mycanvas.pack(fill=BOTH, expand=YES)

    # adding widgets
    # creating the buttons for the main menu
    add_transactions_button=Button(root, text="Add Transaction", command=transaction_window)
    see_data_button=Button(root, text="Data", command=data_window)

    add_transfer_button=Button(root, text="Transfer Institution",command=transfer_window)
    exit_program_button=Button(root, text="Exit Program", command=root.quit)
    # adding buttons to canvas
    add_trans_window=mycanvas.create_window(350,120, anchor='nw', window=add_transactions_button, width=200, height=35)
    see_data_window=mycanvas.create_window(350,170, anchor='nw', window=see_data_button, width=200, height=35)

    add_transfer_window=mycanvas.create_window(350,230, anchor='nw', window=add_transfer_button, width=200, height=35)
    exit_program_window=mycanvas.create_window(350,280, anchor='nw', window=exit_program_button, width=200, height=35)



    # tag all of the drawn widgets
    mycanvas.addtag_all("all")
    root.mainloop()

if __name__ == "__main__":
    initiate_db()
    main()
