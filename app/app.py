from flask import Flask, request, render_template
from dbconnection import executeQuery
from QueryParser import QueryParser
from Parser import getQuery


app = Flask(__name__)

@app.route("/")
def mainPage():
    return render_template("index.html")

@app.route("/execute", methods=["POST", "GET"])
def execute():
    print((request.form["dbType"], request.form["query"]))
    query = request.form["query"].strip().strip('\n').strip('\r').strip('\r\n')
    # parser = QueryParser.getInstance()
    try:
        if 'on' in request.form.getlist("free_speech_switch"):
            print("running free speech")
            query = getQuery(query)
        else:
            print("running parser")
            parser = QueryParser.getInstance()
            query = parser.handle(query)
        
        print("Got query: ", query)
        tableHeaders, results, timeElapsed = executeQuery(query, request.form["dbType"], request.form["dbName"])
    except:
        message = "Server faced with unexpected error! Make sure you use the right swtich!!"
        return render_template("index.html", message=message)
    print(tableHeaders, results)
    return render_template("index.html", tableHeaders=tableHeaders, results=results, timeElapsed=timeElapsed)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)