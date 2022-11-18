# Loads the budget and plots a particular expenditure over time
# Specify the budget name after -c on the command line

import budgeting
import budgetanly
import sys

bdgtnm = sys.argv[1]
bdgt = [x for x in sys.argv[2:len(sys.argv)]] # list of budgets to include in plot

# Load the budget
proj = budgeting.Project('')
proj.load(bdgtnm)

# Get the currency of the project
currency = proj.currency

# Load the expenditures
tr = proj.trfilter({'bdgt':bdgt,'date':[(2021,5,1),(2022,12,31)]})

# Plot the monthly expenditures
plt_nm = '_'.join(bdgt)
[md,lq,uq] = budgetanly.trplot(tr,plt_nm+'.png',currency)
# includes median, 25% quantile, and 75% quantile

# Display the average monthly transactions
print('Monthly expenditure (0:s): {1:.0f} [{2:.0f} {3:.0f}]'.format(currency,md,lq,uq))
