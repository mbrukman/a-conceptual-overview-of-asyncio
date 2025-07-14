import asyncio

class Blah:
    def __await__(self):
        print("You are now entering __await__.")
        

async def func():
    b = Blah()
    await b

b = Blah()
b.__await__()