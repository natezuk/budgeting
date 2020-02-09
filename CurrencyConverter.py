## Load currency conversion rates ##
import requests
import json
# This runs as soon as the program is imported
# The current code is set up to use fixer.io's currency exchange rates
try:
    converter_json = requests.get('http://data.fixer.io/api/latest?access_key=<insert_access_key_here>')
    CurrencyInfo = json.loads(converter_json.text)
    del converter_json
    print('Loaded currency info')
except:
    print('Unable to load currency info')