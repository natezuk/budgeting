# Module contains objects and functions needed for budgeting

import datetime
import os
from pysqlcipher3 import dbapi2 as sqlcipher
from CurrencyConverter import CurrencyInfo
# For testing #
#CurrencyInfo = {'base':'USD','rates':{'EUR':0.9}};

## Objects ##
class Project:
    trtab = 18 # tab size for transaction listing
    
    # Create object with a description
    def __init__(self,doc='',currency=''):
        self.__doc__ = doc
        self.currency = currency
        # reset other default variables
        self.acct = []
        self.bdgt = []
        self.trlst = []
        self.trcnt = 0
        self.adjlst = [] # for budget adjustments
        self.adjcnt = 0
    
    def __str__(self): # for printing the object
        return(self.__doc__)
    
    def info(self): # display general info about the project
        print(self.__doc__) # display the budget name
        print('Currency: ' + self.currency) # display the budget currency
        print('Available budget: %.2f' % self.availbudget()) # display the available amount for budgeting
        print('-- Accounts --')
        self.dispall('acct') # display the information on the accounts
        print('-- Budgets --')
        self.dispall('bdgt') # display the information on the budgets
    
    # Make an account or budget with a particular name
    def acctmake(self,nm,currency='',credit=0):
        if currency=='': # if the currency is not defined, use the project's currency
            currency = self.currency
        a = Account(nm,currency,credit)
        # make sure the account is not the same name as any other
        if not self.get(nm,self.acct):
            self.acct.append(a)
        else:
            err = 'An existing account already has the name %s' % (nm)
            raise NameError(err)
        
    def bdgtmake(self,nm):
        b = Budget(nm)
        # make sure the budget is not the same name as any other
        if not self.get(nm,self.bdgt):
            self.bdgt.append(b)
        else:
            err = 'An existing budget already has the name %s' % (nm)
            raise NameError(err)
    
    # Find the index account, budget, or transaction with the value v
    def get(self,v,l):
        'Find the object with name or value nm in list l'
        for ind in range(len(l)):
            if l[ind]==v:
                return(ind)
        return(None) # if not found, return none
    
    def sumtrs(self,flt):
        'Compute the sum of a transactions, and output in the currency of the project'
        trs = self.trfilter(flt)
        return sum(currency_convert(x.value,x.currency,self.currency) for x in trs)
    
    def trfilter(self,flt):
        'Filter the transaction list using the dictionary flt'
        # Each key is the category name to filter
        trtmp = self.trlst
        for k,v in flt.items():
            if k.lower()=='count':
                # Filter based on range of values in v
                try:
                    v = int(v) # if v is an integer
                    if v>=0: # first v transactions
                        cnts = range(v+1)
                    elif v<0: # last v transactions
                        tot = len(self.trlst)
                        cnts = range(tot+v,tot)
                except TypeError: # if v is a list
                    if len(v)==2: # between the two values in v, inclusive
                        cnts = range(v[0],v[1]+1)
                    else:
                        err = 'Value for count can only have up to 2 indexes'
                        raise IndexError(err)
                # Select transactions
                fun = lambda x: x.cnt in cnts
                trtmp = list(filter(fun,trtmp))
            if k.lower()=='type':
                # Include transactions with the same type(s) listed
                fun = lambda x: x.trtype in v
                trtmp = list(filter(fun,trtmp))
            if k.lower()=='value':
                # Include transactions within the range of values in v
                try: # up to v (includes non-integers)
                    v = float(v)
                    fun = lambda x: x.value<=v
                except TypeError:
                    if len(v)==2: # between two values in v, inclusive
                        # If either the first or second value is None, do not limit lower or upper limit of range
                        if v[1] is None:
                            fun = lambda x: x.value>=v[0]
                        elif v[0] is None:
                            fun = lambda x: x.value<=v[1]
                        else:
                            fun = lambda x: x.value<=v[1] and x.value>=v[0]
                    else:
                        err = 'Value for transaction amount can only have up to 2 indexes'
                        raise IndexError(err)
                trtmp = list(filter(fun,trtmp))
            if k.lower()=='acct':
                # Include transactions with the account name
                if isinstance(v,str): # check if it's a single string
                    fun = lambda x: x.F == v or x.T == v
                else: # otherwise, for a list
                    fun = lambda x: x.F in v or x.T in v
                trtmp = list(filter(fun,trtmp))
            if k.lower()=='bdgt':
                # Include transactions with the budget name
                if isinstance(v,str): # check if it's a single string
                    fun = lambda x: x.T == v
                else: # otherwise, for a list
                    fun = lambda x: x.T in v
                trtmp = list(filter(fun,trtmp))
            if k.lower()=='date':
                # Include transactions within range of dates, inclusive
                # Date value must be contained within a list
                # Two values must be specified for the range. If one of those values is
                # None, then used the earliest or latest recorded date. If only one value is
                # specified, get transactions only on that date
                if len(v)==1:
                    fun = lambda x: x.dt == datetime.date(v[0][0],v[0][1],v[0][2])
                elif len(v)==2:
                    if v[0] is None:
                        fun = lambda x: x.dt <= datetime.date(v[1][0],v[1][1],v[1][2])
                    elif v[1] is None:
                        fun = lambda x: x.dt >= datetime.date(v[0][0],v[0][1],v[0][2])
                    else:
                        fun = lambda x: x.dt >= datetime.date(v[0][0],v[0][1],v[0][2]) and x.dt <= datetime.date(v[1][0],v[1][1],v[1][2])
                else:
                    err = 'Value for date must contain either 1 or 2 tuples in a list'
                    raise ValueError(err)   
                trtmp = list(filter(fun,trtmp))
            if k.lower()=='note':
                # Only include transactions with word(s) in their note, insensitive to case
                if isinstance(v,str): # check if it's a single string
                    v = [v]
                fun = lambda x: sum([x.note.lower().find(s.lower())>-1 for s in v])>0
                trtmp = list(filter(fun,trtmp))
        return trtmp
    
    def adjfilter(self,flt):
        'Filter the adjustments list using the dictionary flt'
        # Each key is the category name to filter
        adjtmp = self.adjlst
        for k,v in flt.items():
            if k.lower()=='count':
                # Filter based on range of values in v
                try:
                    v = int(v) # if v is an integer
                    if v>=0: # first v adjustments
                        cnts = range(v+1)
                    elif v<0: # last v adjustments
                        tot = len(self.adjlst)
                        cnts = range(tot+v,tot)
                except TypeError: # if v is a list
                    if len(v)==2: # between the two values in v, inclusive
                        cnts = range(v[0],v[1]+1)
                    else:
                        err = 'Value for count can only have up to 2 indexes'
                        raise IndexError(err)
                # Select transactions
                fun = lambda x: x.cnt in cnts
                adjtmp = list(filter(fun,adjtmp))
        for k,v in flt.items():
            if k.lower()=='bdgt':
                # Include adjustments with the budget name
                if isinstance(v,str): # check if it's a single string
                    fun = lambda x: x.bdgtname == v
                else: # otherwise, for a list
                    fun = lambda x: x.bdgtname in v
                adjtmp = list(filter(fun,adjtmp))
            if k.lower()=='value':
                # Include adjustments within the range of values in v
                try: # up to v (includes non-integers)
                    v = float(v)
                    fun = lambda x: x.value<=v
                except TypeError:
                    if len(v)==2: # between two values in v, inclusive
                        # If either the first or second value is None, do not limit lower or upper limit of range
                        if v[1] is None:
                            fun = lambda x: x.value>=v[0]
                        elif v[0] is None:
                            fun = lambda x: x.value<=v[1]
                        else:
                            fun = lambda x: x.value<=v[1] and x.value>=v[0]
                    else:
                        err = 'Value for transaction amount can only have up to 2 indexes'
                        raise IndexError(err)
                adjtmp = list(filter(fun,adjtmp))
            if k.lower()=='date':
                # Include adjustments within range of dates, inclusive
                # Date value must be contained within a list
                # Two values must be specified for the range. If one of those values is
                # None, then used the earliest or latest recorded date. If only one value is
                # specified, get adjustments only on that date
                if len(v)==1:
                    fun = lambda x: x.dt == datetime.date(v[0][0],v[0][1],v[0][2])
                elif len(v)==2:
                    if v[0] is None:
                        fun = lambda x: x.dt <= datetime.date(v[1][0],v[1][1],v[1][2])
                    elif v[1] is None:
                        fun = lambda x: x.dt >= datetime.date(v[0][0],v[0][1],v[0][2])
                    else:
                        fun = lambda x: x.dt >= datetime.date(v[0][0],v[0][1],v[0][2]) and x.dt <= datetime.date(v[1][0],v[1][1],v[1][2])
                else:
                    err = 'Value for date must contain either 1 or 2 tuples in a list'
                    raise ValueError(err)   
                adjtmp = list(filter(fun,adjtmp))
        return adjtmp
    
    # Display a particular account or budget
    def disp(self,nm,lsnm):
        'Display the info for a particular account or budget'
        l = getattr(self,lsnm)
        ind = self.get(nm,l)
        print(l[ind])
    
    # Display all budgets
    def dispall(self,lsnm):
        'Display all account, budget, or transaction objects in the list l'
        l = getattr(self,lsnm)
        print(lsnm.upper()) # show the list name being displayed
        print('*'*len(lsnm))
        # If it's a transaction list, display a header first
        if lsnm=='trlst':
            header = 'Count\tType\tValue\tFrom\tTo\tDate\tNote'
            undln = '---\t----\t-----\t----\t--\t----\t----'
            print(header.expandtabs(self.trtab))
            print(undln.expandtabs(self.trtab))
        elif lsnm=='adjlst': # same for the adjustments list
            header = 'Count\tBudget\tValue\tDate'
            undln = '-----\t------\t-----\t----'
            print(header.expandtabs(self.trtab))
            print(undln.expandtabs(self.trtab))
        for ii in l:
            print(ii)
        print('') # include a space after the listing
        
    def disptrs(self,flt={}):
        'Display transactions that fit the specified filters'
        # Filter the list here
        l = self.trfilter(flt)
        print('Transactions')
        print('************')
        header = 'Count\tType\tValue\tFrom\tTo\tDate\tNote'
        undln = '---\t----\t-----\t----\t--\t----\t----'
        print(header.expandtabs(self.trtab))
        print(undln.expandtabs(self.trtab))
        for ii in l:
            print(ii)
        print('') # include a space after the listing
        
    def dispadj(self,flt={}):
        'Display adjustments that fit the specified filters'
        # Filter the list here
        l = self.adjfilter(flt)
        print('Adjustments')
        print('***********')
        header = 'Count\tBudget\tValue\tDate'
        undln = '-----\t------\t-----\t----'
        print(header.expandtabs(self.trtab))
        print(undln.expandtabs(self.trtab))
        for ii in l:
            print(ii)
        print('') # include a space after the listing
    
    # Account functions
    def income(self,nm,amnt,d,note=''):
        # find the account with the name 'nm'
        ind = self.get(nm,self.acct)
        # add the income
        self.acct[ind].add(amnt)
        currency = self.acct[ind].currency # get the currency for the account
        # make a transaction
        t = Transaction(self.trcnt,'income',amnt,currency,'',nm,d,note)
        self.trlst.append(t)       
        self.trcnt+=1
        
    # Spend money from an account on a budgeted object, remove money from both
    def spend(self,amnt,anm,bnm,d,note=''):
        # find the account and budget
        ai = self.get(anm,self.acct)
        bi = self.get(bnm,self.bdgt)
        # remove money from the account
        self.acct[ai].subtr(amnt)
        currency = self.acct[ai].currency # get the currency for the account
        # remove money from the budget
        ### I need to account for the different in project and account currencies here (NZ, 5-1-2018)
        bdgt_amnt = currency_convert(amnt,currency,self.currency)
        self.bdgt[bi].subtr(bdgt_amnt)
        # add a transaction to the list
        t = Transaction(self.trcnt,'spend',amnt,currency,anm,bnm,d,note)
        self.trlst.append(t)
        self.trcnt+=1
    
    # Transfer money between accounts
    def transfer(self,amnt,armv,aadd,d,note=''):
        # find the indexes for the two accounts for subtracting (arm)
        # and adding (aad)
        ai = self.get(armv,self.acct)
        aii = self.get(aadd,self.acct)
        # remove money from the account
        self.acct[ai].subtr(amnt)
        currency = self.acct[ai].currency # get the currency for the account
        # add money to the other account
        self.acct[aii].add(amnt)
        # add a transaction to the list
        t = Transaction(self.trcnt,'transfer',amnt,currency,armv,aadd,d,note)
        self.trlst.append(t)
        self.trcnt+=1
        
    # Reset account to a particular value
    def reset(self,nm,amnt,d,note=''):
        # find the index for the account
        ind = self.get(nm,self.acct)
        chng = amnt-self.acct[ind].amount
        # set the amount in the account
        self.acct[ind].reset(amnt)
        currency = self.acct[ind].currency # get the currency for the account
        # add a transaction
        t = Transaction(self.trcnt,'reset',chng,currency,nm,'',d,note) # save the change in the account amount
        self.trlst.append(t)
        self.trcnt+=1
    
    ########################
    ### Budget functions ###
    ########################
    def add(self,nm,amnt,date=None):
        # find the index for the budget
        ind = self.get(nm,self.bdgt)
        # add to the budget
        self.bdgt[ind].add(amnt)
        # save the adjustment
        if not date: # if no date was specified
            today = datetime.date.today() # use today's date
            date = (today.year,today.month,today.day)
            adj = BudgetAdjustment(self.adjcnt,nm,amnt,date)
            self.adjlst.append(adj)
            self.adjcnt+=1
        else:
            adj = BudgetAdjustment(self.adjcnt,nm,amnt,date)
            self.adjlst.append(adj)
            self.adjcnt+=1
        
    def subtr(self,nm,amnt,date=None):
        # find the index for the budget
        ind = self.get(nm,self.bdgt)
        # subtract from the budget
        self.bdgt[ind].subtr(amnt)
        # save the adjustment
        if not date: # if no date was specified
            today = datetime.date.today() # use today's date
            date = (today.year,today.month,today.day)
            adj = BudgetAdjustment(self.adjcnt,nm,-amnt,date)
            self.adjlst.append(adj)
            self.adjcnt+=1
        else:
            adj = BudgetAdjustment(self.adjcnt,nm,-amnt,date)
            self.adjlst.append(adj)
            self.adjcnt+=1
        
    def undotransact(self,cnt):
        'Remove a transaction'
        tr = self.trfilter({'count':[cnt,cnt]})[0]
        # Determine the type of transaction
        tp = tr.trtype
        # Undo the money exchange in the transaction
        if tp=='income':
            # remove money from account
            T = tr.T # to account
            ind = self.get(T,self.acct)
            self.acct[ind].subtr(tr.value)
        if tp=='spend':
            # add money back to account and budget
            F = tr.F # from account
            ind = self.get(F,self.acct)
            self.acct[ind].add(tr.value)
            T = tr.T # to budget
            ind = self.get(T,self.bdgt)
            self.bdgt[ind].add(tr.value)
        if tp=='transfer':
            # add money to 'from' account and remove from 'to' account
            F = tr.F # from account
            ind = self.get(F,self.acct)
            self.acct[ind].add(tr.value)
            T = tr.T # to account
            ind = self.get(T,self.acct)
            self.acct[ind].subtr(tr.value)
        if tp=='reset':
            # treat this like a removal of the 'change' amount from the account
            F = tr.F # from account
            ind = self.get(F,self.acct)
            self.acct[ind].subtr(tr.value)
        # Remove the transaction from trlst
        trind = self.trlst.index(tr) # find the index for the transaction
        self.trlst.pop(trind) # remove the transaction
        print('Transaction ' + str(cnt) + ' of type ' + tp + ' with value ' + \
            str(tr.value) + ' ' + tr.currency + ' has been removed')
        
    def load(self,fn):
        'Load all budget information from a file'
        print('Loading budget from ' + fn + '...')
        # Will overwrite the variables in the current project
        if self.trcnt:
            print('Loading database will overwrite variables in this project.')
            asw = input('Continue? (y/n) ');
            if asw=='n':
                return
        # Reinitialize the project
        self.__init__(self.__doc__,self.currency)
        # Open the database
        db = sqlcipher.connect(fn)
        # ask for the password
        pwd = input('Password: ')
        db.execute('pragma key={}'.format(pwd))
        c = db.cursor() # get the cursor for the database
        # Load project description, currency, and trcnt
        c.execute('select * from projvars')
        vals = c.fetchall()
        self.__doc__ = vals[0][0]
        self.currency = vals[0][1]
        self.trcnt = vals[0][2]
        self.adjcnt = vals[0][3]
        # Load info for each account
        c.execute('select * from accounts')
        vals = c.fetchall()
        for A in vals:
            self.acctmake(A[0],A[2],A[3]) # name, currency, and credit
            self.acct[-1].reset(A[1]) # amount
        # Load info for each budget
        c.execute('select * from budgets')
        vals = c.fetchall()
        for B in vals:
            self.bdgtmake(B[0]) # name
            self.bdgt[-1].add(B[1]) # amount
        # Load info for each transaction
        c.execute('select * from transacts')
        vals = c.fetchall()
        for Tr in vals:
            cnt = Tr[0]
            trtype = Tr[1]
            v = Tr[2]
            cr = Tr[3] # currency
            F = Tr[4]
            T = Tr[5]
            d = (Tr[6],Tr[7],Tr[8])
            note = Tr[9]
            tr = Transaction(cnt,trtype,v,cr,F,T,d,note)
            self.trlst.append(tr)
        # Load info for each adjustment
        c.execute('select * from adjusts')
        vals = c.fetchall()
        for Ad in vals:
            cnt = Ad[0]
            bdgt = Ad[1]
            v = Ad[2]
            d = (Ad[3],Ad[4],Ad[5])
            adj = BudgetAdjustment(cnt,bdgt,v,d)
            self.adjlst.append(adj)
        db.close() # close the database

    def save(self,fn): ###
        'Save all budget information to a file'
        print('Saving budget to ' + fn + '...')
        # Check if the file already exists
        if not os.path.isfile(fn):
            # Load the file
            db = sqlcipher.connect(fn)
            # ask for the password
            pwd = input('New password: ')
            db.execute('pragma key={}'.format(pwd))
            c = db.cursor() # get the cursor to run code to the database
            # Start new accounts table and include accounts
            # Includes currency information (NZ, 5-1-2019)
            c.execute('create table accounts(name text, amount real, currency text, credit real)')
            for A in self.acct:
                c.execute('insert into accounts values (?,?,?,?)',A.listattr())
            # Start new budgets table and include budgets
            c.execute('create table budgets(name text, amount real)')
            for B in self.bdgt:
                c.execute('insert into budgets values (?,?)',B.listattr())
            # Start new transactions table and add transactions
            c.execute('create table transacts(cnt int, trtype text, value real, currency text, '+\
                       'F text, T text, year int, month int, day int, note text)')
            for Tr in self.trlst:
                c.execute('insert into transacts values (?,?,?,?,?,?,?,?,?,?)',Tr.listattr())
            # Start new adjustments table and add adjustments
            c.execute('create table adjusts(cnt int, bdgt text, value real, year int, month int, day int)')
            for Ad in self.adjlst:
                c.execute('insert into adjusts values (?,?,?,?,?,?)',Ad.listattr())
            # Save the project description, currency, and trcnt
            c.execute('create table projvars(projdoc text, currency text, trcnt int, adjcnt int)')
            c.execute('insert into projvars values (?,?,?,?)', \
                      (self.__doc__,self.currency,self.trcnt,self.adjcnt))
        else: # If the database already exists
            # create the database file
            db = sqlcipher.connect(fn)
            # ask for a password
            pwd = input('Password: ')
            db.execute('pragma key={}'.format(pwd))
            # make the cursor for accessing and storing values in database
            c = db.cursor()
            # Search for accounts in table and change values
            for A in self.acct:
                a = A.listattr()
                # If the account exists...
                c.execute('select amount from accounts where name==?',(a[0],))
                chk = c.fetchone()
                if chk:
                    # ...change its value
                    c.execute('update accounts set amount=?, credit=? where name==?',(a[1],a[3],a[0]))
                else: # ...otherwise make a new account
                    c.execute('insert into accounts values (?,?,?,?)',a)
            # Search for budgets and change values
            for B in self.bdgt:
                b = B.listattr()
                # If the budget exists...
                c.execute('select amount from budgets where name==?',(b[0],))
                chk = c.fetchone()
                if chk:
                    # ...change its value
                    c.execute('update budgets set amount=? where name=?',(b[1],b[0]))
                else: # ...otherwise make a new account
                    c.execute('insert into budgets values (?,?)',b)
            # Add transactions that are not in the database yet
            for Tr in self.trlst:
                tr = Tr.listattr()
                # Check if the transaction exists by looking for the id
                c.execute('select value from transacts where cnt==?',(tr[0],))
                chk = c.fetchone()
                if not chk: # if it doesn't exist...
                    # ...add it
                    c.execute('insert into transacts values (?,?,?,?,?,?,?,?,?,?)',tr)
            ## If a transaction has been removed, delete it
            # find transaction counts that are missing
            cnts = [t.cnt for t in self.trlst]
            full = range(self.trcnt)
            missing = [ii for ii in full if ii not in cnts]
            # find the missing transactions in the database
            for m in missing:
                c.execute('select value from transacts where cnt==?',(m,))
                chk = c.fetchone()
                if chk: # if it is there, remove it
                    c.execute('delete from transacts where cnt==?',(m,))  
            # Add adjustments that are not in the database yet
            for Ad in self.adjlst:
                a = Ad.listattr()
                # Check if the transaction exists by looking for the id
                c.execute('select value from adjusts where cnt==?',(a[0],))
                chk = c.fetchone()
                if not chk: # if it doesn't exist...
                    # ...add it
                    c.execute('insert into adjusts values (?,?,?,?,?,?)',a)
            # Update the transaction count
            c.execute('update projvars set trcnt=? where projdoc==?',\
                      (self.trcnt,self.__doc__))
            # Update the adjustments count
            c.execute('update projvars set adjcnt=? where projdoc==?',\
                      (self.adjcnt,self.__doc__))
        # Close the database
        db.commit()
        db.close()

    # General display functions
    def availbudget(self):
        'Return the amount of money available to budget'
        # Compute total value in accounts and budgets
        A = self.total('acct') # total() converts to the currency of the project
        B = self.total('bdgt')
        return(A-B)

    def total(self,lsnm):
        'Return the total amount of money in all accounts or budgets'
        l = getattr(self,lsnm)
        if lsnm=='bdgt':
            amnts = [max([A.amount,0]) for A in l]
        elif lsnm=='acct':
            # convert the accounts to the currency of the project
            amnts = [currency_convert(A.amount,A.currency,self.currency) for A in l]
        else:
            err = 'Name must be either acct or bdgt'
            raise ValueError(err)  
        return(sum(amnts))

    def dispbdgneg(self):
        'Display all budgets that are negative'
        for b in self.bdgt:
            if b.amount<0:
                print(b.name + ': ' + str(b.amount))

class Transaction:
    # Variables
    cnt = 0
    trtype = ''
    trtab = 18
    value = 0
    currency = ''
    F = ''
    T = ''
    dt = None
    note = ''
    
    def __init__(self,cnt,trtype,value,currency,F,T,d,note=''):
        'Create a transaction object'
        self.cnt = cnt # transaction count, for indexing
        self.value = value # amount in the transaction
        self.trtype = trtype # transaction type
        self.currency = currency # currency of the transaction
        self.F = F # from account/budget
        self.T = T # to account/budget
        self.dt = datetime.date(d[0],d[1],d[2])
        self.note = note
        
    def __repr__(self):
        return(str(self.value))
    
    def __str__(self):
        'Displaying a transaction with print'
        msg = str(self.cnt) + '\t' + self.trtype + '\t' + \
            '%.2f' % self.value + ' ' + self.currency + '\t' + self.F + '\t' + \
            self.T + '\t' + str(self.dt) + '\t' + \
            self.note
        return(msg.expandtabs(self.trtab))
    
    def __add__(self, other):
        try:
            # convert to the same currency
            other_value = currency_convert(other.value,other.currency,self.currency)
            return(self.value+other_value)
        except AttributeError:
            return(self.value+float(other))
        
    def __radd__(self, other):
        return(self.value+float(other))
    
    # check if the transaction has the same value as other
    def __eq__(self,other):
        try:
            # convert to the same currency
            other_value = currency_convert(other.value,other.currency,self.currency) 
            return(self.value==other_value)
        except AttributeError:
            return(self.value==other)
        
    def listattr(self):
        'Make a tuple of the transaction variables'
        a = (self.cnt,self.trtype,self.value,self.currency,self.F,self.T,\
             self.dt.year,self.dt.month,self.dt.day,self.note)
        return(a)

class Account:
    # Variables
    name = ''
    amount = 0
    currency = ''
    credit = 0
    negfail = ''
    
    # Initialize the account
    def __init__(self,name,currency,credit=0):
        self.name = name
        self.currency = currency
        self.credit = credit # stores amount of available credit, if it's a credit card
        if credit!=0:
            self.negfail = '!! Subtraction failed. Amount in ' + self.name + \
                      ' will be beyond credit limit.'
        else:
            self.negfail = '!! Subtraction failed. Amount in ' + self.name + \
                      ' will be negative.'
    
    # for display
    def __repr__(self):
        return(self.name)
    
    # for display with print
    def __str__(self):
        msg = '%s: %.2f %s' % (self.name, self.amount, self.currency)
        #msg = self.name + ': ' + str(self.amount) + ' ' + str(self.currency)
        return(msg) 
    
    # check if the account same name as other
    def __eq__(self,other):
        try:
            return(self.name==other.name)
        except AttributeError:
            return(self.name==other)
        
    def listattr(self):
        'Make a tuple of the account variables'
        a = (self.name,self.amount,self.currency,self.credit)
        return(a)
    
    # Add money to the account
    def add(self,amnt):
        self.amount = self.amount+amnt
    
    # Remove money from the account
    def subtr(self,amnt):
        a = self.amount-amnt
        if self.credit: # check if credit account
            if self.credit+a<0:
                raise TransactionError(self.negfail)
            else:
                self.amount = a
        else:
            if a<0:
                raise TransactionError(self.negfail)
            else:
                self.amount = a
                
    # Reset account to a particular value
    def reset(self,amnt):
        self.amount = amnt
        
class Budget:
    # Variables
    name = ''
    amount = 0
    negfail = ''
    
    # Initialize the budget
    def __init__(self,name):
        ### Check if name is a string
        self.name = name
        self.negfail = 'Amount in ' + name + ' category is negative'
    
    # for budget display in python
    def __repr__(self):
        return(self.name)
    
    # for budget display with print
    def __str__(self):
        msg = '%s: %.2f' % (self.name, self.amount)
        return(msg)
        #return(self.name + ': ' + str(self.amount)) 
    
    # check if the budget is the same as other by name
    def __eq__(self,other):
        try:
            return(self.name==other.name)
        except AttributeError:
            return(self.name==other)
    
    def listattr(self):
        'Make a tuple of the budget variables'
        a = (self.name,self.amount)
        return(a)
    
    # Add money to the budget
    def add(self,amnt):
        self.amount = self.amount+amnt
    
    # Remove money from the account
    def subtr(self,amnt):
        a = self.amount-amnt
        if a<0:
            print(self.negfail + ': ' + str(a))
        self.amount = a 
        
class BudgetAdjustment:
    'Keep track of budget adjustments, so I can analyze my predicted budgets each month'
    bdgtname=''
    value=0
    dt=None
    cnt=0
    trtab=18
    
    def __init__(self,cnt,bdgtname,value,d):
        self.cnt = cnt
        self.bdgtname = bdgtname
        self.value = value
        self.dt = datetime.date(d[0],d[1],d[2])
        
    # for display in python
    def __repr__(self):
        return(str(self.value))
    
    # for printing
    def __str__(self):
        msg = str(self.cnt) + '\t' + self.bdgtname + '\t' + '%.2f' % self.value + '\t' + str(self.dt)
        return(msg.expandtabs(self.trtab))
    
    # for adding to a budget adjustment value
    def __add__(self, other):
        try:
            return(self.value+other.value)
        except AttributeError:
            return(self.value+float(other))
        
    def __radd__(self, other):
        return(self.value+float(other))
    
    # check if the budget adjustment has the same value
    def __eq__(self,other):
        try:
            return(self.value==other.value)
        except AttributeError:
            return(self.value==other)
        
    def listattr(self):
        'Make a tuple of the adjustments variables'
        a = (self.cnt,self.bdgtname,self.value,self.dt.year,self.dt.month,self.dt.day)
        return(a)
        
## Currency conversion
def currency_convert(amnt,base,conv):
    'Convert a currency value from one currency type to another'
    # get the value for the base currency
    if CurrencyInfo['base']==base:
        rateB = 1.00
    else:
        try:
            rateB = CurrencyInfo['rates'][base]
        except:
            err = 'Unknown currency ' + base
            raise ValueError(err)
    # get the value for the conversion currency
    if CurrencyInfo['base']==conv:
        rateC = 1.00
    else:
        try:
            rateC = CurrencyInfo['rates'][conv]
        except:
            err = 'Unknown currency' + conv
            raise ValueError(err)
    # convert the monetary amount
    conv_amnt = amnt*rateC/rateB
    return conv_amnt
        
## Errors ##
class Error(Exception):
    pass

class TransactionError(Error):
    def __init__(self,msg):
        self.msg = msg