from flask import Flask
import json
from flask import request
import os
QUOTES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'quotes.json')
CURRENT_QUOTE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'current_quote.json')

app = Flask(__name__)

@app.route("/", methods=["GET"])
def api_help():
    return {
        "endpoints": {
            "GET /quote": "Get the current quote",
            "POST /quote": "Add a new quote to the quotes list in form of JSON with keys: quotation, source, author",
            "GET /quotes": "Get all quotes",
            "POST /quotes": "Replace all quotes with new list of quotes in form of JSON with key: quotes (array of quote objects with keys: quotation, source, author)"
        }
    }
    

@app.route("/quote", methods=["GET"]) 
def getCurrentQuote():
    with open(CURRENT_QUOTE_FILE, 'r') as f:
        data = json.load(f)
    return {"status":"success","quote": data}

@app.route("/quote", methods=["POST"])
def addQuote():

    payload = request.get_json()
    quotation = payload.get("quotation")
    source = payload.get("source")
    author = payload.get("author")
    try:
        # Read existing quotes
        with open(QUOTES_FILE, 'r') as f:
            data = json.load(f)
        
        # Add new quote to the quotes array
        data.append({
            "quotation": quotation,
            "source": source,
            "author": author
        })
        
        # Write updated quotes back to file
        with open(QUOTES_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        
        return {"status": "success", "message": "Quote added successfully"}, 200
    
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@app.route("/quotes", methods=["GET"])
def getQuotes():
    with open(QUOTES_FILE, 'r') as f:
        data = json.load(f)
    return {"status":"success","quotes": data}



@app.route("/quotes", methods=["POST"])
def setQuotes():
    try:
       
        payload = request.get_json()
        quotes = payload.get("quotes")
    
        # Write updated quotes back to file
        with open(QUOTES_FILE, 'w') as f:
            json.dump(quotes,f)
        return {"status": "success", "message": "Quotes replaced successfully"}, 200

    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

if __name__ == "__main__":
    app.run()