import asyncio
from classes.picrawler import Picrawler  # Assuming Picrawler imports Robot correctly

# Initialize Picrawler instance
picrawler = Picrawler()

# Test tap action
async def test_tap():
    print("Testing front-right leg tap at 50 dps...")
    await picrawler.tap_front_right_async(dps=50)
    await asyncio.sleep(5)
    print("Testing front-right leg tap at 100 dps...")
    await picrawler.tap_front_right_async(dps=100)
    await asyncio.sleep(5)
    print("Testing front-right leg tap at 200 dps...")
    await picrawler.tap_front_right_async(dps=200)
    await asyncio.sleep(5)
    print("Testing front-right leg tap at 300 dps...")
    await picrawler.tap_front_right_async(dps=300)
    await asyncio.sleep(5)
    print("Testing front-right leg tap at 400 dps...")
    await picrawler.tap_front_right_async(dps=400)
    await asyncio.sleep(5)
    print("Testing front-right leg tap at 500 dps...")
    await picrawler.tap_front_right_async(dps=500)

if __name__ == "__main__":
    asyncio.run(test_tap())
