from flask import Flask
import json
from flask import request

app = Flask(__name__)

@app.route("/", methods=["GET"])
def getCurrentQuote():
    with open('current_quote.json', 'r') as f:
        data = json.load(f)
    return {"status":"success","current_quote": data['current_quote']}

@app.route("/quotes", methods=["GET"])
def getQuotes():
    with open('quotes.json', 'r') as f:
        data = json.load(f)
    return {"status":"success","quotes": data['quotes']}

@app.route("/quotes", methods=["POST"])
def addQuote():
    if request.method == "POST":
        # Get form data
        quote = request.form.get("quote")
        source = request.form.get("source")
        author = request.form.get("author")
        
        try:
            # Read existing quotes
            with open('quotes.json', 'r') as f:
                data = json.load(f)
            
            # Add new quote to the quotes array
            data['quotes'].append({
                "quote": quote,
                "source": source,
                "author": author
            })
            
            # Write updated quotes back to file
            with open('quotes.json', 'w') as f:
                json.dump(data, f, indent=4)
            
            return {"status": "success", "message": "Quote added successfully"}, 200
        
        except Exception as e:
            return {"status": "error", "message": str(e)}, 500


if __name__ == "__main__":
    app.run()