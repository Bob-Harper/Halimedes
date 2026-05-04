from aiohttp import web

async def handle_hardware(request):
    data = await request.json()
    components = data.get("components", [])

    # HAL's hardware manager already exists
    snapshot = request.app["hardware_manager"].snapshot()

    result = {c: snapshot.get(c) for c in components}
    return web.json_response(result)

def create_hal_api(hardware_manager):
    app = web.Application()
    print("Starting Onboard API")
    app["hardware_manager"] = hardware_manager
    app.router.add_post("/api/hardware", handle_hardware)

    return app
