import re
import requests

class QueryParser():
    
    _instance = None


    @staticmethod
    def getInstance():
        if not QueryParser._instance:
            QueryParser()
        return QueryParser._instance 
    

    def __init__(self):
        if QueryParser._instance:
            raise("Query Parser is a Singleton class. Use QueryParser.getInstance() method to get the object")
        else:
            QueryParser._instance = self

    def handleConnectingCharacters(self, columns, specialCharaters):
          
        temp = []
        cleanedCols = []
        for col in range(len(columns)):
            if columns[col] in specialCharaters:
                temp.append(specialCharaters[columns[col]])
            else:
                temp.append(columns[col])
                if col < len(columns)-1 and columns[col+1] not in specialCharaters:
                    cleanedCols.append(''.join(temp))
                    temp = []
        if temp:
            cleanedCols.append(''.join(temp))
        print("Connecting chars cleaned: ", cleanedCols)
        return cleanedCols
      
      
    def handleSpecialCharacters(self, columns, specialCharacters): 
        
        cleanedCols = []
        column = 0
        while column < len(columns):
            if columns[column] in specialCharacters:
                cleanedCols.append(specialCharacters[columns[column]])
                if (columns[column] == "greater" or columns[column] == "less") and columns[column+1] == "than":
                    column += 1
            else:
                cleanedCols.append(columns[column])
            column += 1
        print("handle special characters: ", cleanedCols)
        return cleanedCols

    
    def isInteger(self, value):
        
        try:
            int(value)
            return True
        except:
            return False


    def handleStringValues(self, cleanedItem):
        
        operators = set(["!", "=", ">", "<", "like"])
        item = 0

        while item < len(cleanedItem):
            if cleanedItem[item] in operators: 
                while cleanedItem[item] in operators:
                    item += 1
                if not self.isInteger(cleanedItem[item]) and '.' not in cleanedItem[item]:
                    cleanedItem[item] = "'" + cleanedItem[item] + "'"
            item += 1
        print("String cleaned item: ", cleanedItem)
        return cleanedItem
    
    def handleFunctions(self, columns):

        functions = self.getMappings("functions")
        
        tempCleanedCols = []
        cleanedCols = []
        column = 0

        while column < len(columns):
            if columns[column] in functions:
                n = column+2 if columns[column+1] == "of" else column+1
                columns[n] = functions[columns[column]]+"("+columns[n]+")"
                column = n
            tempCleanedCols.append(columns[column])
            column += 1


        column = 0
        while column < len(tempCleanedCols)-2:
            if tempCleanedCols[column+1] == "as":
                tempCleanedCols[column+2] = tempCleanedCols[column] + " as " + tempCleanedCols[column+2]
                column = column+2
            cleanedCols.append(tempCleanedCols[column])
            column += 1
        if column < len(tempCleanedCols):
            cleanedCols = cleanedCols + tempCleanedCols[-2:]
        print("Function Handler: ", cleanedCols) 
        return cleanedCols


    def getMappings(self, mapping):
        
        mappings = {
                "columnSpecialCharacters": {
                    "all": "*",
                    "star": "*",
                    "ascending": "",
                    "descending": ""
                },

                "connectingCharacters": {
                    "underscore": "_",
                    "dot": "."
                },
        
                "conditionSpecialCharacters": {
                    "equals": "=",
                    "and": "AND",
                    "not": "!",
                    "or": "OR",
                    "greater": ">",
                    "less": "<",
                    "percentile": "%",
                    "like": "like"
                },

                "spaceMappings": {
                     "! =": "!=",
                     "> =": ">=",
                     "< =": "<="
                },

                "regex": {
                    "select": ["(?<=select).*?(?=from)"],
                    "from": ["(?<=from).*?(?=(\s+where|\s+order by|\s+group by|\s+having|\s*$))"],
                    "where": ["(?<=where).*?(?=(group by|order by|having|$))", "(?<=where)\s+[\w\. ]+(?=(\s*$))"],
                    "group by": ["(?<=group by).*?(?=(order by|having|$))", "(?<=group by)\s+[\w\. ]+(?=(\s*$))"],
                    "order by": ["(?<=order by).*?(?=(having|$))", "(?<=order by)\s+[\w\. ]+(?=(\s*$))"],
                    "having": ["(?<=having)\s+[\w\. ]+(?=(\s*$))"]
                },

                "functions": {
                    "sum": "SUM",
                    "minimum": "MIN",
                    "min": "MIN",
                    "max": "MAX",
                    "maximum": "MAX",
                    "average": "AVG",
                    "count": "COUNT"
                },
                "stripChars": set(["'", '"', ",", ";", " "])

        }

        return mappings[mapping]

      
    def makeRequest(self, host_url, data, request_type):
        
        if request_type == "post":
            resp = requests.post(host_url, json=data)
            return resp.json()
   

    def cleanRawItems(self, parsed_items):

        columnType = set(["select", "group by", "order by"])
        
        for item in parsed_items:
            cleanedItem = parsed_items[item].strip().split(" ")
            stripChars = self.getMappings("stripChars")
            for char in stripChars:
                cleanedItem = list(map(lambda x: x.strip(char), cleanedItem))
            cleanedItem = list(filter(lambda x: x != '', cleanedItem))
            cleanedItem = self.handleConnectingCharacters(cleanedItem, self.getMappings("connectingCharacters"))
            
            if item in columnType:
                extra = ""
                if item == "order by":
                    if "ascending" in cleanedItem:
                        extra = "ASC"
                    elif "descending" in cleanedItem:
                        extra = "DESC"

                cleanedItem = self.handleSpecialCharacters(cleanedItem, self.getMappings("columnSpecialCharacters"))
                cleanedItem = self.handleFunctions(cleanedItem)
                cleanedItem = list(filter(lambda x: x != '', cleanedItem))
                parsed_items[item] = ','.join(cleanedItem) + " " + extra
                parsed_items[item] = parsed_items[item].strip()
            
            else:
                cleanedItem = self.handleSpecialCharacters(cleanedItem, self.getMappings("conditionSpecialCharacters"))
                cleanedItem = self.handleStringValues(cleanedItem)
                cleanedItem = self.handleFunctions(cleanedItem)
                parsed_items[item] =' '.join(cleanedItem)
                spaceMappings = self.getMappings("spaceMappings")
                for spaceMap in spaceMappings:
                    parsed_items[item] = parsed_items[item].replace(spaceMap, spaceMappings[spaceMap])
        

        return parsed_items


    def generateQuery(self, parsed_items):
        
        parsed_items = self.cleanRawItems(parsed_items)   
         
        keywords = ["select", "from", "where", "group by", "order by", "having"]
        query = []

        for keyword in keywords:
            if keyword in parsed_items:
                query.append(keyword)
                query.append(parsed_items[keyword])
        
        query.append("LIMIT 100;")

        print(parsed_items)
        query = ' '.join(query)
        return query


    def parseQuery(self, query):
        
        regex = self.getMappings("regex")
        parsed_items = {}

        for key in regex:
            item = None
            exp = 0
            while not item and exp < len(regex[key]):
                item = re.search(regex[key][exp], query)
                exp += 1
            if item:
                parsed_items[key] = item.group(0).strip()
            
        return parsed_items


    def handle(self, query):
         
        # type: (HandlerInput) -> Response
        ###
        ### Getting variables from Alexa Model
        ###
        # slots = handler_input.request_envelope.request.intent.slots
        # slots = handler_input["slots"]
        # query = slots["query"].replace(". ", ".")
        # database = slots["database"]
        # table = slots["table"].value
        # columns = slots["columns"].value
        # database = slots["database"].value
        # stop_words = set(["star", "all"])


        parsed_items = self.parseQuery(query) 
        print(parsed_items) 
        
        query = self.generateQuery(parsed_items)
        print(query)
        return query
        # resp = self.makeRequest(
        #                     host_url="http://34.227.108.56/updateQuery", 
        #                     data={"database": database, "query": query},
        #                     request_type="post"
        #                 )
        
        
        # speak_output = resp["message"]
        # 
        # return (
        #     handler_input.response_builder
        #         .speak(speak_output)
        #         # .ask("add a reprompt if you want to keep the session open for the user to respond")
        #         .response
        # )



# parser = QueryParser.getInstance()
# query = input("enter the query: ")
# database = input("enter the database: ")
# slots = {"query": query.lower().strip(), "database": database.lower().strip()}
# handler_input = {"slots": slots}
# parser.handle(query)



