import coingen
import requests

with open("coins.mint", "r") as f:
    coins: list[list[str, int]] = eval(f.read())

tokens: list[str] = []

x = int(input("Amount to sell -> "))

for i in range(x - 1):
    coin = coingen.permutate(coins[i][0], coins[i][1])
    print(requests.get(f"http://localhost:5001/api/sell?coin={coin}&token=ar{i}&slippage=0&name=Adam+Ryan").text)
    tokens.append(f"ar{i}")

print(tokens)