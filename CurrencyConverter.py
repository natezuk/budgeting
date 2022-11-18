## Load currency conversion rates ##
import requests
import json
# This runs as soon as the program is imported
try:
    converter_json = requests.get('http://data.fixer.io/api/latest?access_key=ddd2ed361874f31afe4275ecc929aa6d')
    CurrencyInfo = json.loads(converter_json.text)
    del converter_json
    print('Loaded currency info')
except:
    print('Unable to load currency info')