# Autonoumous System Information Checker

asnChecker is a tool to get information of the autonoumous system which you're interested. Such like Adj ASes, PoC, Prefixes, Public IXes and Private facs, etc. This tool will crawl the public information on Internet and return all of them using JSON format.

# Description

Running this tool will listen on 127.0.0.1 port 8080 and the only thing is to provide AS number to asn parameter to asnchecker and event. 
>Example: http://127.0.0.1:8080/asnchecker?asn=15169
>Example: http://127.0.0.1:8080/event?asn=15169

# Information Source

* https://peeringdb.com/
* https://bgp.potaroo.net/
* https://bgpstream.com/

# Installation

```sh
$ pip3 install -r requirements.txt
$ python3 asnChecker.py
$ * Serving Flask app "asnChecker" (lazy loading)
$ * Environment: production
$   WARNING: This is a development server. Do not use it in a production deployment.
$   Use a production WSGI server instead.
$ * Debug mode: on
$ * Running on http://127.0.0.1:8080/ (Press CTRL+C to quit)
$ * Restarting with stat
$ * Debugger is active!
$ * Debugger PIN: 328-083-063
```

# Docker

```sh
$ docker run -t -d -p8080:8080 jieliau/asnchecker
```

And connect to http://127.0.0.1:8080
