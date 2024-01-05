import asyncio

from researcher.core.agent import Researcher

async def main():

    
    r = Researcher('taylor swifts concert in 2023. How was it?')

    response = await r.run()

    print(response)


asyncio.run(main())

