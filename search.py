__author__ = 'gordon'
from flask import *
from contextlib import closing
import urllib2
from bs4 import BeautifulSoup
import re
from lxml import etree
import json

DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

# util
# deal with str(None)
def xstr(s):
    if s is None:
        return ''
    return str(s)


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
        print counts
        length = len(counts.split(",")[0].split())
        if length == 4:
            count = counts.split()[1]
        else:
            count = counts.split()[0]
    else:
        count = 0

    # pack the result
    result = {}
    result["url"] = url
    result["count"] = count

    return result

# belgium
def getresult(nodes):
    result = {}
    results = []
    for node in nodes:
        result["id"] = node.get("number")
        result["type"] = node.get("type")
        result["quantity"] = node.get("quantity")
        result["date_range1"] = node.get("date_range1")
        result["date_range2"] = node.get("date_range2")
        result["date"] = xstr(result["date_range1"]) + " " + xstr(result["date_range2"])
        result["detail"] = " ".join(node.text.strip().replace("\n","").split()[1:])
        series = []
        lnote = node.xpath("../note")
        if len(lnote)>0:
             result["lnote"] = " ".join( lnote[0].text.strip().replace("\n","").split()[1:])
        for p in node.iterancestors("series"):
            series.append(p.get("title"))
        result["series"] = " -> ".join(series[::-1])
        for p in node.iterancestors("collection"):
            title = p.get("title")
            result["collection"] = title
            note = p.find(".//note")
            if note!=None:
                result["cnote"] = note.text.strip().replace("\n","")
        results.append(result)
        result={}
    nresults = sorted(results, key=lambda k: int(k['id']))
    return nresults

def ftitle(inventory,title):
    results = set()
    nodes = inventory.find(".//collection[@title='" + title + "']")
    for node in nodes.iter("item"):
        results.add(node)
    return results

def fseries(inventory,title):
    results = set()
    nodes = inventory.find(".//series[@title='" + title + "']")
    for node in nodes.iter("item"):
        results.add(node)
    return results

def fdate(inventory,date):
    results = set()
    date = int(date)
    for node in inventory.iter("item"):
        date1 = node.get("date_range1")
        date2 = node.get("date_range1")
        if date1 != None:
            lower = int(date1.split("-")[0])
            upper = int(date1.split("-")[1])
            if date<=upper and date >=lower:
                results.add(node)
                continue

        if date2 != None:
            lower = int(date2.split("-")[0])
            upper = int(date2.split("-")[1])
            if date<=upper and date >=lower:
                results.add(node)
                continue

    return results

def ftype(inventory,type):
    results = set()
    for node in inventory.iter("item"):
        if type == "other":
            if node.get("type") in ["part","object","report","printed", "printed parts"]:
                results.add(node)
        elif node.get("type") == type:
            results.add(node)
    return results

def ftext(inventory,text):
    results = set()
    for node in inventory.iter("item"):
        if re.match(r'.*'+text+'.*',node.text.replace('\n',' '),re.I):
            results.add(node)
    return results

def fname(inventory,name):
    results = set()
    for node in inventory.iter("item"):
        if node.get("name") != None:
            if name.lower() in node.get("name").lower():
                results.add(node)
    return results

def parse3(inputs):
    result = {}
    tree = etree.parse("bel.xml")
    inventory = tree.getroot()
    nodes = ftext(inventory,inputs)
    print nodes
    result["count"] = len(nodes)
    return result

# The Getty Research Institute
# input a string and return a dictionary
def parse4(inputs):
    # parse query and fetch html result
    query = "+".join(inputs.split())
    # TODO: advanced search support
    url = "http://www.getty.edu/Search/SearchServlet?qt="+query
    res = urllib2.urlopen(url)
    html = res.read()
    soup = BeautifulSoup(html)

    # Result number
    table = soup.find_all("table")[2]
    num = table.find("td").contents[0].strip().split()
    count = num[1]

    result = {}
    result["url"] = url
    if (count.isdigit()):
         result["count"] = count
    else:
         result["count"] = 0

    return result



@app.route('/')
def render_index_page():
    return render_template('layout.html')

@app.route('/search', methods=['GET','POST'])
def search():
    inputs = request.form["search"]
    session["inputs"] = inputs
    result1 = parse1(inputs)
    result2 = parse2(inputs)
    result3 = parse3(inputs)
    result4 = parse4(inputs)
    return render_template("search.html",museum = result1,arch = result2,bel=result3,getty=result4, query=inputs)

@app.route('/adsearch', methods=['GET','POST'])
def adsearch():
    if "inputs" in session:
        inputs = session["inputs"]
        tree = etree.parse("bel.xml")
        inventory = tree.getroot()
        result = getresult(ftext(inventory,inputs))
        return render_template('adsearch.html',results=result)
    else:
        return render_template('adsearch.html')

@app.route('/advsearch', methods=['GET','POST'])
def advsearch():
    tree = etree.parse("bel.xml")
    inventory = tree.getroot()
    session.clear()
    # initial
    result = set(inventory.iter())
    title = request.form.get("title")
    if title != "":
        title_r = ftitle(inventory,title)
        result = result & title_r

    date = request.form["date"]
    if date != "":
        date_r = fdate(inventory,date)
        result = result & date_r

    type = request.form["type"]
    if type != "":
        type_r = ftype(inventory,type)
        result = result & type_r

    series = request.form["series"]
    if series != "":
        series_r = fseries(inventory,series)
        result = result & series_r

    text = request.form["text"]
    if text != "":
        text_r = ftext(inventory,text)
        result = result & text_r

    name = request.form["name"]
    if name != "":
        name_r = fname(inventory,name)
        result = result & name_r


    ls = getresult(result)
    print ls
    return render_template('adsearch.html',results=ls)

@app.route('/detail', methods=['GET','POST'])
def detail():
    result = request.args.get("detail")
    return render_template('detail.html',results = result)


if __name__ == '__main__':
    app.run()