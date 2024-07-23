import asyncio
import sys

import websockets

import SimpleITK as sitk


def world_coordinate_to_stl(pos_input):
    def convert_ras_to_lps(ras_point):
        x, y, z = ras_point
        lps_point = [x, z, size[2] - y]
        return lps_point

    sphere_center = convert_ras_to_lps(pos_input)
    world_coordinate = dicom_image.TransformIndexToPhysicalPoint(
        (int(sphere_center[0]) - 25, int(sphere_center[1]) - 25, int(sphere_center[2]) - 25))
    return world_coordinate, spacing


async def process_and_forward(websocket):
    async for message in websocket:
        print(f"Server 8765 received: {message}")

        try:
            # terminate and send signal to frontend
            if message == 'terminate':
                await forward_to_frontend('terminate')
                sys.exit(0)

            x, y, z = map(int, message.split(','))

            origin, scale = world_coordinate_to_stl([x, y, z])
            processed_message = ', '.join(str(coord) for coord in origin)

            await forward_to_frontend(processed_message)

        except Exception as e:
            print(e)


async def forward_to_frontend(message):
    async with websockets.connect("ws://localhost:" + str(frontend_port)) as outbound:
        await outbound.send(message)
        response = await outbound.recv()
        print(f"echo from frontend: {response}")


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "dicomFolder"

    reader = sitk.ImageSeriesReader()
    dicom_series = reader.GetGDCMSeriesFileNames(arg)
    reader.SetFileNames(dicom_series)

    # read dicom tags
    dicom_image = reader.Execute()
    spacing = dicom_image.GetSpacing()
    size = dicom_image.GetSize()

    frontend_port = 8887
    navigation_port = 8765

    # connect to navigation program's websocket
    start_server_navigation = websockets.serve(process_and_forward, "localhost", navigation_port)

    asyncio.get_event_loop().run_until_complete(start_server_navigation)
    asyncio.get_event_loop().run_forever()
