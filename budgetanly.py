# Stores code to analyze a budget object
# Use budgeting.py to create the budget object

import matplotlib.pyplot as plt
import numpy as np
from CurrencyConverter import CurrencyInfo # gets the currency conversion info
from budgeting import currency_convert

def trplot(trlist,pltnm,currency):
    'Plots the transactions in trlist by month. Saves the plot in the file pltnm.'
    
    ### Need to include the currency
    # Get the range of dates in the list
    dt = [x.dt for x in trlist]
    mnthyr = np.array([(x.month-1)+x.year*12 for x in dt])
        # stores month and year as (month-1) + year*12
    
    # Create an array to store the average amount
    unq = np.arange(np.amin(mnthyr),np.amax(mnthyr)+1) # contains all possible year-month pairings
    trbymnth = np.zeros(unq.shape) # will store average transaction amounts
    
    amnt = np.array([currency_convert(x.value,x.currency,currency) for x in trlist]) # get the amounts for each transaction
    for ii in range(unq.size):
        usedt = mnthyr==unq[ii] # get transactions with specific year-month pair
        trbymnth[ii] = np.sum(amnt[usedt]) # add the transactions together
  
    # Compute the average monthly expenses
    md = np.median(trbymnth) # median (avoids outlier months)
    lq = np.percentile(trbymnth,25) # 25% quantile
    uq = np.percentile(trbymnth,75) # 75% quantile
    
    # Plot the average by month
    fig, ax = plt.subplots()
    ax.plot(unq,trbymnth,'k')
    ax.set(xlabel='Month-Year',ylabel='Expense (' + currency + ')')
    # Create the xtick label array 'Month-Year'
    xtk = ['{0}-{1}'.format(np.mod(x,12)+1,np.int_(np.floor(x/12))) for x in unq]
    plt.xticks(unq,xtk,rotation=45)
    # Make the title
    tle = pltnm + ': {0:.0f} [{1:.0f} {2:.0f}]'.format(md,lq,uq)
    plt.title(tle)
    # Make sure there's no clipping
    fig.set_tight_layout(True)
    # Save the figure
    fig.savefig(pltnm)

    # Return the average monthly expenses
    return [md,lq,uq]
    
def revplot(explist,inclist,pltnm,currency):
    'Plots the average revenue per month, given the expense list and income list.'
    
    ### Need ot include the 
    # Concatenate the two lists, but invert the value of expenses
    amnt = np.array([-currency_convert(x.value,x.currency,currency) for x in explist] + \
                    [currency_convert(x.value,x.currency,currency) for x in inclist])
    trlist = explist + inclist;
    
    # Get the range of dates in the transaction list
    dt = [x.dt for x in trlist]
    mnthyr = np.array([(x.month-1)+x.year*12 for x in dt])
        # stores month and year as (month-1) + year*12
    
    # Create an array to store the average amount
    unq = np.arange(np.amin(mnthyr),np.amax(mnthyr)+1) # contains all possible year-month pairings
    trbymnth = np.zeros(unq.shape) # will store average transaction amounts
    
    for ii in range(unq.size):
        usedt = mnthyr==unq[ii] # get transactions with specific year-month pair
        trbymnth[ii] = np.sum(amnt[usedt]) # average the transactions together
   
    # Compute the average monthly revenue
    md = np.median(trbymnth) # median (avoids outlier months)
    lq = np.percentile(trbymnth,25) # 25% quantile
    uq = np.percentile(trbymnth,75) # 75% quantile
    
    # Plot the average by month
    fig, ax = plt.subplots()
    # plot dashed line for 0
    ax.plot(unq,np.zeros(unq.shape),'k--')
    ax.plot(unq,trbymnth,'k')
    ax.set(xlabel='Month-Year',ylabel='Revenue (' + currency + ')')
    # Create the xtick label array 'Month-Year'
    xtk = ['{0}-{1}'.format(np.mod(x,12)+1,np.int_(np.floor(x/12))) for x in unq]
    plt.xticks(unq,xtk,rotation=45)
    # Make the title for the plot
    tle = 'Monthly revenue: {0:.0f} [{1:.0f} {2:.0f}]'.format(md,lq,uq)
    plt.title(tle)
    # Make sure there's no clipping
    fig.set_tight_layout(True)
    # Save the figure
    fig.savefig(pltnm)

    return [md,lq,uq]

def trbdgtcmp(trlist,adjlist,pltnm,currency):
    'Plots the transactions in trlist by month. Saves the plot in the file pltnm.'
    
    ### Need to include the currency
    # Get the range of dates in the list
    dt_tr = [x.dt for x in trlist]
    mnthyr_tr = np.array([(x.month-1)+x.year*12 for x in dt_tr])
        # stores month and year as (month-1) + year*12
    dt_adj = [x.dt for x in adjlist]
    mnthyr_adj = np.array([(x.month-1)+x.year*12 for x in dt_adj])
    allmnthyr = np.hstack((mnthyr_tr,mnthyr_adj))
    
    # Create an array to store the average amount
    unq = np.arange(np.amin(allmnthyr),np.amax(allmnthyr)+1) # contains all possible year-month pairings
    trbymnth = np.zeros(unq.shape) # will store average transaction amounts
    adjbymnth = np.zeros(unq.shape) # will stor average adjustments
    
    tr_amnt = np.array([currency_convert(x.value,x.currency,currency) for x in trlist]) # get the amounts for each transaction
    adj_amnt = np.array([x.value for x in adjlist])
    for ii in range(unq.size):
        usedt_tr = mnthyr_tr==unq[ii] # get transactions with specific year-month pair
        trbymnth[ii] = np.sum(tr_amnt[usedt_tr]) # add the transactions together
        usedt_adj = mnthyr_adj==unq[ii] # ...and same for adjustments
        adjbymnth[ii] = np.sum(adj_amnt[usedt_adj])
  
    # Compute the average monthly expenses
    md_tr = np.median(trbymnth) # median (avoids outlier months)
    lq_tr = np.percentile(trbymnth,25) # 25% quantile
    uq_tr = np.percentile(trbymnth,75) # 75% quantile
    md_adj = np.median(adjbymnth) 
    lq_adj = np.percentile(adjbymnth,25)
    uq_adj = np.percentile(adjbymnth,75)
    
    # Plot the average by month
    fig, ax = plt.subplots()
    tr_line, = ax.plot(unq,trbymnth,'k')
    adj_line, = ax.plot(unq,adjbymnth,'r')
    ax.set(xlabel='Month-Year',ylabel='Expense (' + currency + ')')
    ax.legend((tr_line,adj_line),('Transactions','Adjustments'))
    # Create the xtick label array 'Month-Year'
    xtk = ['{0}-{1}'.format(np.mod(x,12)+1,np.int_(np.floor(x/12))) for x in unq]
    plt.xticks(unq,xtk,rotation=45)
    # Make the title
    plt.title(pltnm)
    # Make sure there's no clipping
    fig.set_tight_layout(True)
    # Save the figure
    fig.savefig(pltnm)