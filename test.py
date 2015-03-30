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
    for line in text:
        # find I cat
        for cat in cat1:
            if re.match(r".*"+cat,line):
                inv["cat1"] = cat
                flag = False
                break

        # find A cat
        if re.match(r"[A-D]\.",line):
            inv["cat2"] = line
            flag = False

        # find docid
        if re.match(str(i) + '\.',line):
            inv["id"] = i-1
            invs.append(inv)
            inv={}
            inv["content"]=""
            i+=1
            flag = True

        if flag:
            inv["content"]+=line+" "
    return invs[1:]


# def parse3(inputs):
#     with open("bel.txt") as f:
#         text = f.readlines()
#     print text[:10]
    # pattern = re.compile(r"\b"+inputs+r"\b",flags=re.I)
    # if re.search(pattern, text):
    #     print "Yes"
    # else:
    #     print "No"


a = json.dumps(clean())
with open("test.json",'w') as f:
    f.write(a)