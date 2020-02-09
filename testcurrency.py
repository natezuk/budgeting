#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Test:
# - Budget creation in a particular currency (this is the currency in which the overall budget is displayed)
# - Creating accounts in different currencies
# - Currency conversion in a budget
# - Saving and loading budget currency information
# Delete test.db before running this, if it exists in the directory
import budgeting
import os

# Create a project in euro
proj = budgeting.Project('Test currency','EUR')

# Make sure the currency is displayed when the project information is checked
proj.info()

# Create one US account for $1000, and a Europe account for €1500
proj.acctmake('US checking','USD')
proj.reset('US checking',1000.00,(2019,1,1))
proj.acctmake('EU checking') # Assumes the currency of the account is the same as the currency of the project
proj.reset('EU checking',1500.00,(2019,1,1))

# Make two budget categories for Groceries and Student loans
proj.bdgtmake('Groceries')
proj.add('Groceries',400.00)
proj.bdgtmake('Student loans')
proj.add('Student loans',300.00)

# Display the conversion factor between USD and EUR, so that I can double check that the conversion is correct
budgeting.currency_convert(1.00,'USD','EUR')

# Make a transaction from the EU account
proj.spend(200.00,'EU checking','Groceries',(2019,1,4),'grocery store')

# Make a transaction from the US account
proj.spend(250.00,'US checking','Student loans',(2019,1,2),'')

# Display the transactions (it should include the currencies as well)
proj.disptrs()

# Check the expenses of the accounts
# The account's currency should also be displayed
proj.dispall('acct')
proj.dispall('bdgt')

# Check the available budget
# This should automatically convert accounts in different currencies to the currency for the project
avail = proj.availbudget()
print('Available budget = ' + str(avail) + ' ' + proj.currency)
# This should be around 1708 EUR, depending upon the conversion factor at the time

# Save the project
proj.save('test.db')

# Clear the old project
del proj

# Make a new project
newproj = budgeting.Project('Test currency 2','USD')

# Load the old project, and make sure that the currency is overwritted with EUR
newproj.load('test.db')
newproj.info()

# Try removing the US transaction (it should display the currency of the transaction)
newproj.undotransact(3)
newproj.info()