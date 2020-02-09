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
tr = proj.trfilter({'bdgt':bdgt})
adj = proj.adjfilter({'bdgt':bdgt})

# Plot the monthly expenditures
plt_nm = '_'.join(bdgt)
budgetanly.trbdgtcmp(tr,adj,plt_nm,currency)