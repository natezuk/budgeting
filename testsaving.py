# Test suite for budget saving and loading
import budgeting
import os

def disptotals(proj):
    msg = 'Total in all accounts = ' + str(proj.total('acct')) + '\n' + \
        'Total available to budget = ' + str(proj.availbudget())
    return(msg)

# If the testing database exists, delete it
fn = 'test.db'
if os.path.isfile(fn):
    os.remove(fn)

# Create project
proj = budgeting.Project('Test project','USD')

# Create two accounts, checking and savings, with 1000 and 2000 each
proj.acctmake('checking')
proj.reset('checking',1000.50,(2016,11,5))
proj.acctmake('savings')
proj.reset('savings',2000.25,(2016,11,5))

# Create two budgets, rent and travel, with 1000 and 500 each
proj.bdgtmake('rent')
proj.add('rent',1000)
proj.bdgtmake('travel')
proj.add('travel',500)

# Save the project (should ask for a password)
proj.save(fn)
print('Saved budget')

# Load the project with a new name (should ask for a password)
newproj = budgeting.Project('This will be replaced')
newproj.load(fn)
print('Loaded budget')

# Spend money from checking on travel
newproj.spend(500,'checking','travel',(2016,12,3),'to san diego')

# Spend mondy from checking on rent
newproj.spend(500,'checking','rent',(2016,12,3),'groceries')

# Transfer money from savings to checking
newproj.transfer(1000,'savings','checking',(2016,12,4))

# Display info about budget
print(disptotals(newproj)) # total in accounts: 2000.75, total to budget, 1500.75

# Show the transactions before saving
newproj.dispall('trlst') # display all transactions (there should be 2 resets, 2 spends, and 1 transfer)

# Save the project with the original file name
newproj.save(fn)
print('Saved budget')

# Create a new project, make an account, and add income
ovwrproj = budgeting.Project('This will be overwritten')
ovwrproj.acctmake('oldacct')
ovwrproj.income('oldacct',300,(2016,12,1),'will be overwritten')

# Load the saved project into the newly created project variable
ovwrproj.load(fn)
print('Loaded overwriting budget')

# Display info
print(disptotals(ovwrproj)) # total in accounts: 2000.75, total to budget, 1500.75

# Remove the 'spend' transaction
ovwrproj.undotransact(2)

# Display all transactions (transaction 2 should be missing, spend 500 from checking)
ovwrproj.dispall('trlst')
# Display accounts (checking: 1500.50, savings: 1000.25)
ovwrproj.dispall('acct')
# Display budgets (rent: 500, travel: 500)
ovwrproj.dispall('bdgt')

# Try removing transaction 2 again
try:
    ovwrproj.undotransact(2)
except:
    print('Transaction 2 removal failed')
    
# Display info
print(disptotals(ovwrproj)) # total in accounts: 2500.75, total to budget, 1500.75