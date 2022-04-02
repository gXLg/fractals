import asyncio
import websockets
import cv2
import numpy
from pure import Pure

WIDTH = 50
HEIGHT = 50
MAX_ITER = 500
ZOOM = Pure(200)
X_ORIG = Pure(-129, 2)
Y_ORIG = Pure(699, 4)
COLORS = 2048
gradient = numpy.array([
  [0x74, 0xD4, 0x8E],
  [0x92, 0xF7, 0xEF],
  [0x94, 0xA2, 0xEB],
  [0x94, 0xA2, 0xEB],
  [0x34, 0x4A, 0xBA],
  [0x21, 0x2A, 0x59]
], numpy.int16)
gradient_map = [0, 0.3, 0.6, 0.9, 0.99, 1]
colors = []
for i in range(COLORS):
  index = 0
  while (i / COLORS) > gradient_map[index + 1]:
    index += 1

  start = gradient_map[index]
  end = gradient_map[index + 1]

  delta = end - start
  pos = i / COLORS - start
  diff = pos / delta

  start = gradient[index]
  end = gradient[index + 1]

  colors.append(start + (end - start) * diff)
colors = numpy.array(colors, numpy.uint8)


async def server(websocket, fin, todo, out, worker):
  async for message in websocket:
    message = str(message)
    command, *args = message.split(" ")
    if command == "free":
      if not todo:
        await websocket.send("chill")
      else:
        x, y = todo.pop(0)
        worker[0] += 1
        await websocket.send(f"do {x} {y}")
    elif command == "what":
      await websocket.send(f"todo {WIDTH} {HEIGHT} {MAX_ITER} {ZOOM.a} {ZOOM.b} {X_ORIG.a} {X_ORIG.b} {Y_ORIG.a} {Y_ORIG.b}")

    elif command == "ready":
      x = int(args[0])
      y = int(args[1])
      itera = int(args[2])
      out[y, x] = itera
      worker[0] -= 1

      if not todo:
        await websocket.send("done")
      else:
        await websocket.send("thanks")

      if not todo and not worker[0]:
        print("data ready, processing...")

        num_iter = numpy.zeros((MAX_ITER), numpy.uint16)
        for y in out:
          for x in y:
            num_iter[x] += 1

        total = 0
        for n in num_iter:
          total += n

        sums = []
        s = 0
        for i in range(MAX_ITER):
          s += num_iter[i] / total
          sums.append(s)

        hue = [
          [
            sums[x] for x in y
          ] for y in out
        ]

        print("rendering...")
        image = numpy.array([
          [
            colors[max(0, min(int(x * COLORS), COLORS - 1))] for x in y
          ] for y in hue
        ], numpy.uint8)

        cv2.imwrite(f"output.png", cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

        fin.set_result(0)

async def main():
  worker = [0]
  todo = [(x, y) for x in range(WIDTH) for y in range(HEIGHT)]
  out = numpy.zeros([WIDTH, HEIGHT], numpy.uint16)

  fin = asyncio.Future()
  async with websockets.serve(
    lambda ws: server(ws, fin, todo, out, worker), "localhost", 8765
  ):
    await fin

asyncio.run(main())
