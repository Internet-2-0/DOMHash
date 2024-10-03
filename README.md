<p align="center">
  <img src=".github/domhash_logo.png" width="860" height="852"/>
</p>

# What is DOMHash?

DOMHash is a completely self sustainable program that requires no thirdparty libraries and works "out of the box". 

It is a way to determine similarities in DOM content by generating a fuzzy hash from the content and comparing the hashes together

# How do I use it?

DOMHash can be used as a standalone tool or implemented as a library. To use it as a standalone tool:
```bash
chmod 777 domhash.py
cp domhash.py /whatever/path/you/want

$ /whatever/path/you/want/domhash.py -h
usage: domhash.py [-h] [-h1 HASHONE] [-h2 HASHTWO] [domcontent]

optional arguments:
  -h, --help            show this help message and exit

Positional Arguments:
  domcontent            Pass the dom content to build the hash from

Misc Arguments:
  -h1 HASHONE, --hash1 HASHONE
                        Pass a built hash to compare to another hash (requires -h2 to be passed)
  -h2 HASHTWO, --hash2 HASHTWO
                        Pass another built hash to compare to first hash (requires -h1 to be passed)
$ ./domhash.py "`curl -s https://google.com`"
DnHlIfDnlumG12o1TIfd8DeJhYQFPDOcWw2zH2zpk3c=
$ ./domhash.py -h1 "`curl -s https://google.com`" -h2 "`curl -s https://duckduckgo.com`"
2.28
```

To use DOMHash as a library, simply copy the `domhash.py` file over to your location and import it:

```python
import requests

from domhash import DomHash

url1 = "http://106.54.193.152:8888/supershell/login/"
url2 = "http://185.196.8.189"

req1 = requests.get(url1, verify=False).content
req2 = requests.get(url2, verify=False).content

domhash = DomHash(None)
domhash.update_dom(req1)
hash1 = domhash.generate_fuzzy_hash()
print(hash1)
domhash.update_dom(req2)
hash2 = domhash.generate_fuzzy_hash()
print(hash2)
results = domhash.compare_hashes(hash1, hash2)
print(results)

# $ python test.py
# 8ipnY4uYlcP_36t9lwOepyXVnEF1GVmclsfyuIpmoug=
# GLgOEM_NeKHS-9HkkzOfOnxUbVTTQzhRbri5F04n7mg=
# 6.82
```

You also have the option to install DOMHash as a library and run it that way by running the `setup.py` file like so:

```python3
python setup.py install
```

This will install the program and provide you with the ability to use it as a library. 

# Supported languages

| Language   | Support Versions | Is Released? |
|------------|------------------|--------------|
| Python     | >3.8.x           | Yes          |
| Rust       | --               | No           |
| C          | --               | No           |
| Javascript | --               | No           |