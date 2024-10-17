import random, math

cl = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890"

def tetration(a, n):
    # Base case: if n is 1, return the base (a)
    if n == 1:
        return a
    # Recursive case: a raised to the power of tetration(a, n-1)
    return a ** tetration(a, n - 1)

def gen():
    o = ""
    for i in range(100):
        o += cl[random.randrange(0, len(cl) - 1)]
    return o

def permutate(coin: str, amount: int) -> str:
    s = ""
    for c in coin:
        # Get the new index, wrapping around using the modulo operator
        new_index = (cl.index(c) % amount) % len(cl)
        s += cl[new_index]
    return s
