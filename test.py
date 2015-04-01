__author__ = 'gordon'
import re
import json

def clean():
    cat1 = ["ADMINISTRATIVE SERVICES","MANAGEMENT BOARD","DIRECTORATE RECOVERY","DIRECTORATE REPARATIONS",
            "DIRECTORATE GOVERNMENT OPERATIONS","ARCHIVES MANAGEMENT AT THE COMMERCIAL","ARCHIVAL DOCUMENTS WITH"]

    with open("bel.txt") as f:
        text = f.readlines()
    i=1
    flag = True
    inv={}
    inv["content"]=""
    invs=[]
    
    # category
    cate1 = ""
    cate2 = ""
    for line in text:
        # find I cat
        if len(cat1)>0:
			if re.match(r".*"+cat1[0],line):
				cate1 = cat1.pop(0)
				flag = False
		
        # find A cat
        if re.match(r"[A-D]\.",line):
            cate2 = line
            flag = False
		
        # find docid
        if re.match(str(i) + '\.',line):
            inv["id"] = i-1
            inv["cate1"] =cate1
            inv["cate2"] = cate2
            invs.append(inv)
            inv = {}
            inv["content"]=""
            inv["cate1"] =cate1
            inv["cate2"] = cate2
            i+=1
            flag = True

        if flag:
            inv["content"]+=line+" "
    return invs[1:]


def parse3(inputs):
    dics = clean()
    pattern = re.compile(r"\b"+inputs+r"\b",flags=re.I)
    ids = []
    for dic in dics:
		text = dic["content"]
		if re.search(pattern, text):
			ids.append(dic["id"])
	
    if len(ids)>0:
		print len(ids)
		for id in ids:
			print dics[id-1]


parse3("belgian")
