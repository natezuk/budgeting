# Loads the budget and plots a particular expenditure over time
# Specify the budget name after -c on the command line

import budgeting
import budgetanly
import sys

# Load the budget
bdgtnm = sys.argv[1];
proj = budgeting.Project('')
proj.load(bdgtnm)

# Get the currency of the project
currency = proj.currency

# Load and plot the expenditures for 
exptr = proj.trfilter({'type':'spend','date':[(2018,12,1),None]})
inctr = proj.trfilter({'type':'income','date':[(2018,12,1),None]})
[md,lq,uq] = budgetanly.revplot(exptr,inctr,'Revenue.png',currency)

print('Total revenue: {}'.format(sum(inctr)-sum(exptr)))
print('Monthly revenue: {0:.0f} [{1:.0f} {2:.0f}]'.format(md,lq,uq))