import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
import subprocess

api = Flask(__name__)
CORS(api)

@api.route('/api/verify', methods=['GET'])
def verify():
    coin = request.args.get('coin')  # Extract the coin from the query parameter
    if not coin:
        return jsonify({"error": "coin parameter is missing"}), 400  # Return error if coin is missing

    # Use f-string to include the 'coin' variable in the command
    command = f"python zetcoin.py verify {coin}"

    # Run the subprocess and capture the output
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)

    # Return the result as JSON
    return jsonify({"res": result.stdout.replace("\n", "")})

@api.route('/api/exchange', methods=['GET'])
def exchange():
    coin = request.args.get('coin')  # Extract the coin from the query parameter
    if not coin:
        return jsonify({"error": "coin parameter is missing"}), 400  # Return error if coin is missing

    # Use f-string to include the 'coin' variable in the command
    command = f"python zetcoin.py exchange {coin}"

    # Run the subprocess and capture the output
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)

    # Return the result as JSON
    return jsonify({"res": result.stdout.replace("\n", "")})

# Safely read the price value
with open("price", "r") as f:
    price = float(f.read())  # Avoid eval

def savePrice():
    with open("price", "w") as f:
        f.write(str(price))

class Buyer:
    def __init__(self, token: str, rise: float, name: str):
        self.token = token
        self.rise = rise
        self.seller: Seller | None = None
        self.coin = None
        self.confirmed = False
        self.name = name

    def __repr__(self):
        return f"Token: {self.token} Rise: {self.rise} Coin: {self.coin}"

class Seller:
    def __init__(self, token: str, slippage: float, coin: str, name: str):
        self.token = token
        self.coin = coin
        self.slippage = slippage
        self.buyer: Buyer | None = None
        self.name = name
        self.price = 0

    def __repr__(self):
        return f"Token: {self.token} Slippage: {self.slippage} Coin: {self.coin}"

# List to store buyers and sellers
buyers: list[Buyer] = []
sellers: list[Seller] = []

# Matching logic
def match():
    global sellers, buyers, price

    for seller in sellers:
        if seller.buyer is None:
            buyers.sort(key=lambda b: -b.rise)  # Sort buyers by rise
            print("Buyers:", buyers)
            print("Sellers:", sellers)
            for buyer in buyers:
                if buyer.seller is not None:
                    continue
                if buyer.rise >= seller.slippage:
                    buyer.seller = seller
                    seller.buyer = buyer
                    buyer.coin = eval(requests.get(
                        f"http://localhost:5000/api/exchange?coin={seller.coin}"
                    ).text)['res']
                    seller.price = price + buyer.rise
                    print("Matched buyer to seller:", buyer.seller, "Price:", price + buyer.rise)
                    price += buyer.rise
                    savePrice()
                    break

# Sell API route
@api.route('/api/sell', methods=['GET'])
def sellApi():
    global sellers
    coin = request.args.get('coin')
    slippage = request.args.get('slippage')
    token = request.args.get('token')
    name = request.args.get('name')

    # Check for missing parameters
    if not all([coin, slippage, token, name]):
        return jsonify({"error": "parameters missing"}), 400

    try:
        slippage = float(slippage)
    except ValueError:
        return jsonify({"error": "Invalid slippage value, must be a float"})

    if eval(verify().data)['res'] != "valid":
        return jsonify({"error": "Invalid token"}), 400

    sellers.append(Seller(token, slippage, coin, name))
    match()
    return jsonify({"res": "sell req accepted"})

# Buy API route
@api.route('/api/buy', methods=['GET'])
def buyApi():
    global buyers
    rise = request.args.get('rise')
    token = request.args.get('token')
    name = request.args.get('name')

    # Check for missing parameters
    if not all([rise, token, name]):
        return jsonify({"error": "parameters missing"}), 400

    try:
        rise = float(rise)
    except ValueError:
        return jsonify({"error": "Invalid rise value, must be a float"}), 400

    buyers.append(Buyer(token, rise, name))
    match()
    return jsonify({"res": "buy req accepted"})

# Price API route
@api.route('/api/price', methods=['GET'])
def priceApi():
    return jsonify({"price": price})
@api.route('/api/info', methods=['GET'])
def infoApi():
    return jsonify({"sellers": len(sellers), "buyers": len(buyers), "price": price})

# Status API route
@api.route('/api/status', methods=['GET'])
def statusApi():
    global buyers, sellers
    token = request.args.get('token')
    fBuyer = None
    fSeller = None

    for buyer in buyers:
        if buyer.token == token:
            fBuyer = buyer
    for seller in sellers:
        if seller.token == token:
            fSeller = seller

    if fBuyer:
        if fBuyer.confirmed:
            buyers.remove(fBuyer)
            return jsonify({"res": f"Exchange completed! Your coin: {fBuyer.coin} - save it, you cannot view it again."})
        elif fBuyer.seller:
            return jsonify({"res": f"Exchange pending for seller to confirm your purchase... Seller: {fBuyer.seller.name}. Price: {fBuyer.seller.price}zł."})
        else:
            return jsonify({"res": "Exchange pending..."})
    elif fSeller:
        if fSeller.buyer:
            return jsonify({"res": f"Found buyer! Buyer: {fSeller.buyer.name}. Confirm this transaction after the exchange of goods. Price: {fSeller.price}zł."})
        else:
            return jsonify({"res": "Exchange pending..."})

    return jsonify({"res": "Invalid token!"})

@api.route('/api/confirm', methods=['GET'])
def confirmApi():
    token = request.args.get('token')
    for seller in sellers:
        if seller.token == token:
            if seller.buyer is not None:
                seller.buyer.confirmed = True
                sellers.remove(seller)
                return jsonify({"res": "Sell completed!"})
            else:
                return jsonify({"res": "No buyer found yet!"})
    return jsonify({"res": "Invalid token!"})

@api.route('/api/deny', methods=['GET'])
def denyApi():
    token = request.args.get('token')
    for seller in sellers:
        if seller.token == token:
            if seller.buyer is not None:
                return jsonify({"res": f"Sell denied! Coin return: {seller.buyer.coin}"})
            else:
                return jsonify({"res": "No buyer found yet!"})
    return jsonify({"res": "Invalid token!"})


if __name__ == '__main__':
    api.run(debug=True)
