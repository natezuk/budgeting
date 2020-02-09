#!/usr/bin/env python
# Test the transaction filtering function

import budgeting

# Create a budgeting project
proj = budgeting.Project('','USD')

print('Creating accounts and budgets...')

# Create two accounts, checking=500 and savings=750
proj.acctmake('checking')
proj.reset('checking',500.00,(2016,12,1))
proj.acctmake('savings')
proj.reset('savings',750.00,(2016,12,1))

# Create 2 budgets, Rent=200, Food=100
proj.bdgtmake('Rent')
proj.add('Rent',200)
proj.bdgtmake('Food')
proj.add('Food',100)

# Spend 150 on rent from checking on 5-12-2016 in rochester
proj.spend(150.00,'checking','Rent',(2016,12,5),'rochester')

# Spend 50 on food (groceries) from savings on 20-12-2016
proj.spend(50.00,'savings','Food',(2016,12,20),'groceries, rochester')

# Transfer 500 from savings to checking on 3-1-2017
proj.transfer(500.00,'savings','checking',(2017,1,3))

# Spend 40 on restaurant in boston using checking on 5-1-2017
proj.spend(40.00,'checking','Food',(2017,1,5),'restaurant, boston')

# Show all transactions
print('Displaying all transactions...')
# 6 transactions, 2 resets, 3 expenditures, 1 transfer
proj.disptrs()

## Filter based on transaction count
print('Showing the first 3 transactions...')
proj.disptrs({'count':2})
print('Showing the last 3 transactions...')
proj.disptrs({'count':-3})
print('Showing transactions 2-5...')
proj.disptrs({'count':[2, 5]})

## Filter based on type
print('Showing expenditures...')
proj.disptrs({'type':'spend'})

## Filter based on value
print('Showing expenditures < $100...')
proj.disptrs({'type':'spend','value':100})
print('Showing transactions > $300...')
proj.disptrs({'value':[300, None]})
print('Showing transactions between $100 and $200...')
proj.disptrs({'value':[100, 200]})

## Filter based on account or budget
print('Showing checking transactions...')
proj.disptrs({'acct':'checking'})
print('Showing food transactions...')
proj.disptrs({'bdgt':'Food'})
print('Showing transactions for rent and food...')
proj.disptrs({'bdgt':['Rent','Food']})

## Filter based on date
print('Showing transactions before 1-1-2017...')
proj.disptrs({'date':[None,(2017,1,1)]})
print('Showing transactions on 1-1-2017 (there are none)...')
proj.disptrs({'date':[(2017,1,1)]})
print('Showing transactions after 1-1-2017...')
proj.disptrs({'date':[(2017,1,1),None]})

## Filter based on note
print('Showing transactions in rochester and groceries...')
proj.disptrs({'note':['rochester','groceries']})
print('Showing transactions in boston')
proj.disptrs({'note':'boston'})