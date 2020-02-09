#!/usr/bin/env python
# Test suite for budgeting module

import budgeting

def disptotals(proj):
    msg = 'Total in all accounts = ' + str(proj.total('acct')) + '\n' + \
        'Total available to budget = ' + str(proj.availbudget())
    return(msg)

# Create a new project
proj = budgeting.Project('Test project','USD')
print(disptotals(proj))

# Make a checking account
proj.acctmake('checking')
# Add 500 dollars
proj.income('checking',500,(2016,11,1))

# Make a rent budget
proj.bdgtmake('rent')
# Put 300 dollars in
proj.add('rent',300)

# The total amount in all accounts is 500
# The total amount available to budget is 200
print(disptotals(proj))

# Spend 200 dollars from checking for rent on 11/2/2016
proj.spend(200,'checking','rent',(2016,11,2),'paid rent!')

# Total in accounts = 300, total available to budget is 200
print(disptotals(proj))

# Display the number of transactions (should be 2)
print(len(proj.trlst))
# Display the transaction counter (should be 2)
print(proj.trcnt)

# Display the last transaction
print(proj.trlst[-1])
# Display the amount in the checking account
proj.disp('checking','acct')
# Display the amount in the rent budget
proj.disp('rent','bdgt')

# Try spending another 600 on rent
# It should fail because the account would go below 0
try:
    proj.spend(600,'checking','rent',[2016,11,3],'too much rent...')
except budgeting.TransactionError:
    print('Transaction error')
    
# Make a new account
proj.acctmake('savings')
# Add another 1000 dollars
proj.reset('savings',1000,(2016,11,5))
# Transfer 500 from savings to checking, no comment
proj.transfer(500,'savings','checking',[2016,11,5])
# Display the amounts in each account (500 in savings, 800 in checking)
proj.disp('savings','acct')
proj.disp('checking','acct')

# Now try paying the rent, it should work
# A notification that we've gone over budget will be displayed
proj.spend(600,'checking','rent',[2016,11,5],'okay, paying rent now')
# Total in accounts = 700, total available to budget is 700
print(disptotals(proj))
# Display budgets that are negative
print('The following budgets are negative:')
proj.dispbdgneg()

# Make a credit card account with 1000 credit
proj.acctmake('credit','',1000)
# Make a travel budget
proj.bdgtmake('travel')
# Add 300 to travel
proj.add('travel',300)
# Spend 150 from credit on travel
proj.spend(150,'credit','travel',[2016,12,4])
# And remove 100 from travel afterwards
proj.subtr('travel',100)
# Total in accounts = 550, total available to budget is 550
print(disptotals(proj))

# Display all accounts
proj.dispall('acct')
# Display all transactions
proj.dispall('trlst')