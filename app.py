from flask import Flask, render_template
import requests
import json
from datetime import datetime


app = Flask(__name__)
app.config['DEBUG'] = True
tableData = [["Current Time", "Calls OI", "Puts OI", "PCR"]]

def getChainAnalysis():
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; '
                'x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'}


    main_url = "https://www.nseindia.com/"
    response = requests.get(main_url, headers=headers)
    cookies = response.cookies


    ## NIFTY code
    url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    nifty_oi_data = requests.get(url, headers=headers, cookies=cookies)
    json_object = json.loads(nifty_oi_data.text)
    filteredRecordsForCurrentExpiry = json_object["filtered"]["data"]
    
    multiple = 50
    at_the_money_strike = multiple * round(json_object["records"]["underlyingValue"] / multiple)
    

    _OTMcloseStrikePricesCE = filter(lambda c: c["strikePrice"] >= at_the_money_strike and c["strikePrice"] <= (at_the_money_strike + 500), filteredRecordsForCurrentExpiry)

    _OTMcloseStrikePricesPE = filter(lambda c: c["strikePrice"] <= at_the_money_strike and c["strikePrice"] >= (at_the_money_strike - 500), filteredRecordsForCurrentExpiry)

    allCE = [["Strike", "Price", "OI", "Change in OI"]]
    allPE = [["Strike", "Price", "OI", "Change in OI"]]

    lstDataCE = list(_OTMcloseStrikePricesCE)
    lstDataPE = list(_OTMcloseStrikePricesPE)

    for m in lstDataCE:
        allCE.append([m["CE"]["strikePrice"], m["CE"]["lastPrice"], m["CE"]["openInterest"] * multiple, m["CE"]["changeinOpenInterest"] * multiple])
    for m in lstDataPE:
        allPE.append([m["PE"]["strikePrice"], m["PE"]["lastPrice"], m["PE"]["openInterest"] * multiple, m["PE"]["changeinOpenInterest"] * multiple])

    allCE.append(["Total", "", sum(row[2] for row in allCE[1:]), sum(row[3] for row in allCE[1:])])
    allPE.append(["Total", "", sum(row[2] for row in allPE[1:]), sum(row[3] for row in allPE[1:])])

    pcr = sum(row[2] for row in allPE[1:]) / sum(row[2] for row in allCE[1:])
    
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)
    # lstCallPutData = []
    # lstCallPutData.append([current_time, sum(row[2] for row in allCE[1:-1]),  sum(row[2] for row in allPE[1:-1]), pcr])
    tableData.append([current_time, sum(row[2] for row in allCE[1:-1]),  sum(row[2] for row in allPE[1:-1]), pcr])
    
    dict = {"callData" : allCE, "putsData" : allPE}
    return dict


@app.route('/chain')
def chain():
    while True:
        option_chain_data = getChainAnalysis()
        return render_template('chain-analysis.html', callData=option_chain_data["callData"], putData=option_chain_data["putsData"], callPutData=tableData)


if __name__ == '__main__':
    app.run()