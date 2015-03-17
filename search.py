__author__ = 'gordon'
from flask import *
from contextlib import closing
import urllib2
from bs4 import BeautifulSoup
import re

DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)

# for United States Holocaust Memorial Museum
# input a string and return a dictionary
def parse1(inputs):
    # parse query and fetch html result
    query = "+".join(inputs.split())
    # TODO: advanced search support
    url = "http://www.errproject.org/jeudepaume/card_search.php?Query=" + query
    res = urllib2.urlopen(url)
    html = res.read()
    soup = BeautifulSoup(html)

    # Result number
    num = soup.find("div",class_="num")
    if num!= None:
        counts = num.contents[0]
        count = counts.split()[5]
    else:
        count = 0

    # pack the result
    result = {}
    result["url"] = url
    result["count"] = count

    return result


# for National Archives
# input a string and return a dictionary
def parse2(inputs):
    # parse query and fetch html result
    query = "+".join(inputs.split())
    # TODO: advanced search support
    url = "http://search.archives.gov/query.html?qt="+query+"&col=1arch&col=social&qc=1arch&qc=social"
    res = urllib2.urlopen(url)
    html = res.read()
    soup = BeautifulSoup(html)

    # Result number
    num = soup.find("div",class_="result-count")
    if num!= None:
        counts = num.contents[0]
        count = counts.split()[1]
    else:
        count = 0

    # pack the result
    result = {}
    result["url"] = url
    result["count"] = count

    return result

def parse3(inputs):
    with open("bel.txt") as f:
        text = f.read()
    pattern = re.compile(r"\b"+inputs+r"\b",flags=re.I)
    if re.search(pattern, text):
        return "has"
    else:
        return "doesn't have"

@app.route('/')
def render_index_page():
    return render_template('layout.html')

@app.route('/search', methods=['GET','POST'])
def search():
    inputs = request.form["search"]
    result1 = parse1(inputs)
    result2 = parse2(inputs)
    result3 = parse3(inputs)
    return render_template("search.html",museum = result1,arch = result2,bel=result3, query=inputs)

if __name__ == '__main__':
    app.run()