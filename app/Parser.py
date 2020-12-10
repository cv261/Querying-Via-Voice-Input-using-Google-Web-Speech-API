import re


queryAbstract = {
    "where is": "select aisle from products as p inner join aisles as a on p.aisle_id = a.aisle_id where product_name = 'X';",
    "find location": "select aisle from products as p inner join aisles as a on p.aisle_id = a.aisle_id where product_name = 'X';",
    "in which": "select Y from products as p inner join Ys as a on p.Y_id = a.Y_id where product_name = 'X';",
    "most popular product": "select product_name from order_products as op inner join products as p on op.product_id = p.product_id Q group by p.product_id order by count(p.product_id) desc limit L;",
    "popular product": "select product_name from order_products as op inner join products as p on op.product_id = p.product_id Q group by p.product_id order by count(p.product_id) desc limit L;",
    "least popular product": "select product_name from order_products as op inner join products as p on op.product_id = p.product_id Q group by p.product_id order by count(p.product_id) asc limit L;",
    "most product": "select Y from products as p inner join Ys as a on p.Y_id = a.Y_id group by p.Y_id order by count(p.Y_id) desc limit L;",
    "least product": "select Y from products as p inner join Ys as a on p.Y_id = a.Y_id group by p.Y_id order by count(p.Y_id) asc limit L;",
    "product starting": "select product_name from products where product_name like 'X%'",
    "product starting": "select product_name from products where product_name like 'X%'",
    "all product from": "select product_name from products as p inner join aisles as a on p.aisle_id = a.aisle_id where aisle = 'X'",
    "in": "inner join Xs as a on p.X_id = a.X_id where X = 'Y'"
}

regex = {
    "most popular product": {
        "L": "(?<=top).*(?=most popular product)",
        "Q": "(?<=most popular product).*"
    },
    "popular product": {
        "L": "(?<=top).*(?=popular product)",
        "Q": "(?<=popular product).*"
    },
    "least popular product": {
        "L": "(?<=top).*(?=least popular product)",
        "Q": "(?<=least popular product).*"
    },
    "product starting": {
        "X": "(?<=product starting).*"
    },
    "product that starts": {
        "X": "(?<=product that starts).*"
    },
    "in": {
        "X": "(?<=in).*\s+(?=of )",
        "Y": "(?<=of).*"
    },
    "where is": {
        "X": "(?<=where is).*"
    },
    "find location": {
        "X": "(?<=find location of).*"
    },
    "in which": {
        "X": "(?<=is)\s+.*",
        "Y": "(?<=in which).*(?=is)"
    },
    "most product": {
        "L": "(?<=get|top)\s+[0-9]+(?=.*?most product)",
        "Y": "[\w]+\s+(?=most product)"
    },
    "least product": {
        "L": "(?<=get|top)\s+[0-9]+(?=.*?least product)",
        "Y": "[\w]+\s+(?=least product)"
    },
    "all product from": {
        "X": "(?<=all product from).*"
    }
}
# print(re.search("(?<=where is)\s+\w+", "where is coke").group(0))

# print(re.search(".*?(?=most popular product).*?", "most popular product in snacks").findall())


def extractVars(query):
    print("extracting vars for: ", query)
    parsed_item = {}
    for q in queryAbstract.keys():
        if q in query:
            for part in regex[q]:
                result = re.search(regex[q][part], query)
                if result:
                    parsed_item[part] = result.group(0).strip()
            return parsed_item, q



def cleanQuery(query):
    stopwords = set(["the", "with", "a", "an"])
    pluraltosingular = {"aisles" : "aisle", "products" : "product", "departments" : "department", "orders" : "order"}
    query = " ".join(map(lambda x: pluraltosingular[x] if x in pluraltosingular else x, query.split(" ")))
    print("Singular Plural to : ", query)

    return ' '.join(filter(lambda x: x not in stopwords, query.strip().split(" ")))


def buildQuery(query):
    vars, q = extractVars(query)
    print("vars for ", query, "vars:", vars)
    if 'Q' in vars and vars['Q']:
        vars['Q'] = buildQuery(vars['Q'])
    else:
        vars['Q'] = ''
    for key in regex[q]:
        if key not in vars:
            if key == 'L':
                vars[key] = '1'
            else:
                vars[key] = ''
        
    print("final vars for ", query, "vars: ", vars)
    return buildQueryUsingAbstractQueries(vars, q)


def buildQueryUsingAbstractQueries(vars, q):
    finalQuery = queryAbstract[q]
    print("in buildQuery")
    print("got the vars: ", vars)
    for v in vars:
        finalQuery = finalQuery.replace(v, vars[v])
        #elif v == 'L':
        #    finalQuery = finalQuery.replace(v, '1')
    print("Final Query : ", finalQuery)
    return finalQuery



def getQuery(query):
    query = cleanQuery(query)
    print("Cleaned query:", query)
    return buildQuery(query)
    

 



# Look for TOP Keyword to find Limit L




# query = "get all products from missing"


'''
List of working queries:
    get all products starting with chocolate
    find the most popular product
    find the most popular product in the department of deli
    find the most popular product in the aisle of butter
    where is coke
    find the location of turkey
    in which department is turkey


'''

# print(cleanQuery(query))
# print(getQuery("find the top 10 departments with least products in the aisle of soft drinks"))
# inner join Xs as a on p.X_id = a.X_id where X = 'Y' 
