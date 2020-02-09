# Test budgetanly

import budgeting
import budgetanly

# Create a new project
proj = budgeting.Project('Test project','USD')

# Make a checking account
proj.acctmake('checking')
# Add 500 dollars
proj.income('checking',2000,(2016,11,1))

# Make a rent budget
proj.bdgtmake('rent')
# Put 300 dollars in
proj.add('rent',1000)

# Spend 200, 100, 200, and 300 on 11/2016, 1/2017, 2/2017, and 2/2017
proj.spend(200,'checking','rent',(2016,11,2),'paid rent!')
proj.spend(100,'checking','rent',(2017,1,5))
proj.spend(200,'checking','rent',(2017,2,14))
proj.spend(200,'checking','rent',(2017,2,26))

trs = proj.trfilter({'bdgt':'rent'})

budgetanly.trplot(trs,'test.png',proj.currency) # plot the rent transactions by month
# Should display everything in USD

# Plot the revenue per month
exptr = proj.trfilter({'type':'spend'})
inctr = proj.trfilter({'type':'income'})
budgetanly.revplot(exptr,inctr,'testrev.png',proj.currency)