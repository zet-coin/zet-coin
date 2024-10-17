import sys, coingen
import random


if len(sys.argv) > 1:
    cmd = sys.argv[1:len(sys.argv)]
else:
    sCmd = input("zet coin cmd -> ")
    cmd = []
    for token in sCmd.split(" "):
        cmd.append(token)


with open("coins.mint", "r") as f:
    coins: list[list[str, int]] = eval(f.read())

def writeCoins():
    with open("coins.mint", "w") as f:
        f.write(str(coins))

if cmd[0] == "mint":
    for i in range(int(cmd[1])):
        coins.append([coingen.gen(), random.randrange(-100000000, 100000000)])
    writeCoins()

if cmd[0] == "perm":
    print(coingen.permutate(cmd[1], int(cmd[2])))

if cmd[0] == "verify":
    for coin in coins:
        if cmd[1] == coingen.permutate(coin[0], coin[1]):
            print("valid")
            exit()
    print("invalid")

if cmd[0] == "exchange":
    for i, coin in enumerate(coins):
        if cmd[1] == coingen.permutate(coin[0], coin[1]):
            per = random.randrange(-100000000, 100000000)
            coins[i][1] = per
            print(coingen.permutate(coin[0], per))
            writeCoins()
            exit()
    print("ERR coin not found")