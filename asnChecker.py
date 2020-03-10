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
    for i in range(len(aspfx)):
        if 'AS' in aspfx[i]:
            ases.append(aspfx[i])
    ases.remove("AS" + as_number)
    prefixes = [i.text.strip(" ") for i in soup.select('.black')]

    """ Get rich information from peeringdb.com """
    #r = requests.get("https://peeringdb.com/api/net")
    #netjson = r.json()
    with open("./net.json") as netjson_file:
        netdata = json.load(netjson_file)
        for i in range(len(netdata['data'])):
            if netdata['data'][i]['asn'] == int(as_number):
                name = netdata['data'][i]['name']
                website = netdata['data'][i]['website']
                supportIPv6 = netdata['data'][i]['info_ipv6']
                supportMulticast = netdata['data'][i]['info_multicast']
                net_id = netdata['data'][i]['id']
                org_id = netdata['data'][i]['org_id']
                break

    pocs = list()
    ixes = list()
    facs = list()
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

def main():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    
    @app.route("/", methods=['GET'])
    def root():
        return "<h1>Open browser and connect to http://127.0.0.1:8080/asnchecker?asn=[your as number]</h1>"
    
    @app.route("/asnchecker", methods=['GET'])
    def asn():
        asn = request.args.get('asn')
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

    app.run(host="127.0.0.1", port="8080")

if __name__ == '__main__':
    if os.path.isfile("./net.json") == False:
        r = requests.get("https://peeringdb.com/api/net")
        with open("./net.json", "w") as outfile:
            json.dump(r.json(), outfile)

    main()
