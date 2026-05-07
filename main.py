import asyncio
from hal_runtime import Hal

debug_reasoning = True

async def _main():
    hal = Hal(debug_reasoning=debug_reasoning)
    await hal.run()


async def _shutdown(hal: Hal | None):
    if hal is not None:
        await hal.shutdown()


if __name__ == "__main__":
    hal_instance = None
    try:
        hal_instance = Hal(debug_reasoning=debug_reasoning)
        asyncio.run(hal_instance.run())

    except KeyboardInterrupt:
        print("[Shutdown] KeyboardInterrupt received.")
        asyncio.run(_shutdown(hal_instance))

    except Exception as e:
        print(f"[Shutdown] Fatal error: {e}")
        asyncio.run(_shutdown(hal_instance))
        raise
