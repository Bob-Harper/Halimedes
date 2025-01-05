import asyncio
import readchar

async def main():
    print("Press ESC to quit...")

    while True:
        key = readchar.readkey()  # Read a single key press

        print(f"Key pressed: {key}")  # Debugging line to see key value

        if key == readchar.key.ESC:
            print("\nQuitting")
            await asyncio.sleep(2)
            print("\033[H\033[J", end='')  # Clear terminal window
            break

if __name__ == "__main__":
    asyncio.run(main())
