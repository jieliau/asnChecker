import requests, json, os
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup

def asNumberChecker(as_number):
    """ Get Adjancy ASes and Prefixes information from bgp.potaroo.com """
    r = requests.get("https://bgp.potaroo.net/cgi-bin/as-report?as=AS" + str(as_number))
    html_str = r.text
    soup = BeautifulSoup(html_str, features="html.parser")
    aspfx = [i.text for i in soup.select('pre a')]
    ases = list()
    prefixes = list()
    if aspfx == []:
        ases = []
        prefixes = []
    else:    
        for i in range(len(aspfx)):
            if 'AS' in aspfx[i]:
                ases.append(aspfx[i])
        ases.remove("AS" + as_number)
        prefixes = [i.text.strip(" ") for i in soup.select('.black')]

    """ Get rich information from peeringdb.com """
    #r = requests.get("https://peeringdb.com/api/net")
    #netjson = r.json()
    isNet = False
    pocs = list()
    ixes = list()
    facs = list()
    with open("./net.json") as netjson_file:
        netdata = json.load(netjson_file)
        for i in range(len(netdata['data'])):
            if netdata['data'][i]['asn'] == int(as_number):
                isNet = True
                name = netdata['data'][i]['name']
                website = netdata['data'][i]['website']
                supportIPv6 = netdata['data'][i]['info_ipv6']
                supportMulticast = netdata['data'][i]['info_multicast']
                net_id = netdata['data'][i]['id']
                org_id = netdata['data'][i]['org_id']
                break
        if isNet == False:
            name = 'N/A'
            website = 'N/A'
            supportIPv6 = 'N/A'
            supportMulticast = 'N/A'
            pocs = []
            ixes = []
            facs = []
            country = 'N/A'
        else:
            r = requests.get("https://peeringdb.com/api/net/" + str(net_id))
            netjson = r.json()
            for i in range(len(netjson['data'][0]['poc_set'])):
                poc = {
                    "Name": netjson['data'][0]['poc_set'][i]['name'],
                    "Role": netjson['data'][0]['poc_set'][i]['role'],
                    "E-Mail": netjson['data'][0]['poc_set'][i]['email']
                }
                pocs.append(poc)

            for i in range(len(netjson['data'][0]['netixlan_set'])):
                ix = {
                    "Name": netjson['data'][0]['netixlan_set'][i]['name'],
                    "AS Number": netjson['data'][0]['netixlan_set'][i]['asn'],
                    "IPv4": netjson['data'][0]['netixlan_set'][i]['ipaddr4'],
                    "IPv6": netjson['data'][0]['netixlan_set'][i]['ipaddr6']
                }
                ixes.append(ix)

            for i in range(len(netjson['data'][0]['netfac_set'])):
                fac = {
                    "Name": netjson['data'][0]['netfac_set'][i]['name'],
                    "Country": netjson['data'][0]['netfac_set'][i]['country'],
                    "City": netjson['data'][0]['netfac_set'][i]['city']
                }
                facs.append(fac)

            r = requests.get("https://peeringdb.com/api/org/" + str(org_id))
            orgjson = r.json()
            country = orgjson['data'][0]['country']

    return name, website, country, supportIPv6, supportMulticast, pocs, ixes, facs, ases, prefixes

def check_event(as_number):
    r = requests.get("https://bgpstream.com/")
    html_str = r.text
    soup = BeautifulSoup(html_str, features="html.parser")
    events = [i.text.strip(' ') for i in soup.select(".event_type")]
    asn = [i.text.strip().replace("\n", '.') for i in soup.select(".asn")]
    bgphijacks = list()
    bgpleaks = list()
    outages = list()
    for i in range(len(events)):
        if events[i] == 'Possible Hijack':
            if 'AS ' + str(as_number) in asn[i]:
                bgphijacks.append(asn[i])
        if events[i] == 'Outage':
            if 'AS ' + str(as_number) in asn[i]:
                outages.append(asn[i])
        if events[i] == 'BGP Leak':
            if 'AS ' + str(as_number) in asn[i]:
                bgpleaks.append(asn[i])
    return bgphijacks, bgpleaks, outages

def main():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    
    @app.route("/", methods=['GET'])
    def root():
        return ''' <h1>Check Autonomous System Information<br> 
        Connect to http://127.0.0.1:8080/asnchecker?asn=[your AS number]
        <br><br>
        Check if you AS is under event<br>
        Connect to http://127.0.0.1:8080/event?asn=[you AS number]</h1> '''
    
    @app.route("/asnchecker", methods=['GET'])
    def asn():
        if 'asn' in request.args:
            asn = request.args.get('asn')
            try:
                int(asn)
                name, website, country, supportIPv6, supportMulticast, pocs, ixes, facs, ases, prefixes = asNumberChecker(asn)
                results = {
                    "Name": name,
                    "Website": website,
                    "Country": country,
                    "Support IPv6": supportIPv6,
                    "Support Multicast": supportMulticast,
                    "Point Of Contacts": pocs,
                    "Public Peering Exchanges Points": ixes,
                    "Private Peering Facilities": facs,
                    "Adjancy ASes": ases,
                    "Prefixes": prefixes
                }
                return jsonify(results)
            except ValueError:
                return "<h1>You use the wrong AS number format. Integer</h1>"
        else:
            return "<h1>You have to provide AS number. http://127.0.0.1:8080/asnchecker?asn=[your AS number]</h1>"

    @app.route("/event", methods=['GET'])
    def event():
        if 'asn' in request.args:
            asn = request.args.get('asn')
            try:
                int(asn)
                bgphijacks, bgpleaks, outages = check_event(asn)
                results = {
                    "AS Number": asn,
                    "Possible BGP Hijack": bgphijacks,
                    "BGP Leak": bgpleaks,
                    "Outage": outages
                }
                return jsonify(results)
            except ValueError:
                return "<h1>You use the wrong AS number format. Integer</h1>"
        else:
            return "<h1>You have to provide AS number. http://127.0.0.1:8080/event?asn=[your AS number]</h1>"

    app.run(host="127.0.0.1", port="8080")

if __name__ == '__main__':
    if os.path.isfile("./net.json") == False:
        print("Downloading...")
        r = requests.get("https://peeringdb.com/api/net")
        with open("./net.json", "w") as outfile:
            json.dump(r.json(), outfile)

    main()
