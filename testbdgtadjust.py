# Test budget adjustments:
# - Keeps track of budget changes
# - Display all budget adjustments or a subset of budget adjustments (adjustment filter)
# - Save budget adjustments in the same database, and load budget adjustments
# - Plot monthly budget adjustments alongside expenses

import budgeting
import budgetanly

# Create a new budget
proj = budgeting.Project('Test adjustments','USD')
proj.info()

# Make two accounts, one for checking and one for savings
proj.acctmake('checking','USD')
proj.reset('checking',1000.00,(2019,1,1))
proj.acctmake('savings','USD')
proj.reset('savings',1500.00,(2019,1,1))

# Make two budgets, rent and groceries
proj.bdgtmake('Rent')
proj.bdgtmake('Groceries')

# Display budget adjustments (there shouldn't be any because we haven't added anything to the budgets)
proj.dispadj()

print('Add 1000->800 for rent (add then subtract 200), 500 for groceries')
proj.add('Rent',1000.00,(2019,1,1))
proj.subtr('Rent',200.00,(2019,1,1))
proj.add('Groceries',500.00,(2019,1,1))

# Display the budget adjustments (now there should be some)
proj.dispadj()

# Display only adjustments for rent
proj.dispadj({'bdgt':'Rent'})

# Display the available budget (1200.00)
print('Available budget should be 1200')
print('Available budget: ' + proj.availbudget())

# Save the budget
proj.save('test_adj.db')

del proj

# Load a new budget
newproj = budgeting.Project('Test adjustments 2','USD')
newproj.load('test_adj.db')

# Display the budget adjustments
newproj.dispadj()

### Test for plotting
print('Add adjustments in different months (Groceries: 400 in Feb, 500 in Mar)')
newproj.add('Groceries',400.00,(2019,2,1))
newproj.add('Groceries',500.00,(2019,3,1))
# Add transactions in those months
print('Add transactions (Groceries: 450 in Feb, 450 in Mar)')
newproj.spend(450.00,'checking','Groceries',(2019,2,12))
newproj.spend(450.00,'checking','Groceries',(2019,3,5))

# Display both the month-by-month transactions and the budget adjustments
trs = newproj.trfilter({'bdgt':'Groceries'}) # transactions
adjs = newproj.adjfilter({'bdgt':'Groceries'}) # adjustments
plt_nm = 'TestAdjustments.png'
budgetanly.trbdgtcmp(trs,adjs,plt_nm,newproj.currency)

# Lastly, test if making an adjustment without a specified date creates one at today's date
print('Create rent + 300 adjustment today (check the date)')
newproj.add('Rent',300.00)
newproj.dispadj()