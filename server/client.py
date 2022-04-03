import asyncio
import websockets
from pure import Pure
from sys import argv
from multiprocessing.pool import ThreadPool

settings = {}

def point(x, y):

  WIDTH = settings["WIDTH"]
  HEIGHT = settings["HEIGHT"]
  MAX_ITER = settings["MAX_ITER"]
  ZOOM = settings["ZOOM"]
  X_ORIG = settings["X_ORIG"]
  Y_ORIG = settings["Y_ORIG"]

  x = (Pure(x) - Pure(WIDTH // 2)) / ZOOM + X_ORIG
  y = (Pure(HEIGHT // 2) - Pure(y)) / ZOOM + Y_ORIG

  # cardioid check
  qua = Pure(25, 2)
  p = x - qua
  q = p * p + y * y
  if q * (q + x - qua) <= qua * y * y:
    return MAX_ITER - 1 #colors[-1]

  # bulb check
  p = x + Pure(1)
  if p * p + y * y <= qua * qua:
    return MAX_ITER - 1 #colors[-1]

  za = Pure(0)
  zb = Pure(0)
  a2 = Pure(0)
  b2 = Pure(0)

  s = set()
  itera = 0
  while itera < MAX_ITER:

    s.add((za, zb))

    zb = Pure(2) * za * zb + y
    za = a2 - b2 + x
    a2 = za * za
    b2 = zb * zb

    if (za, zb) in s:
      return MAX_ITER - 1 #colors[-1]
    elif Pure(65536) <= a2 + b2:
      return itera

    itera += 1
  return MAX_ITER - 1 #colors[-1]

async def client():
  async with websockets.connect("ws://" + argv[1]) as websocket:
    await websocket.send("what")
    command, *args = (await websocket.recv()).split(" ")

    settings["WIDTH"] = int(args[0])
    settings["HEIGHT"] = int(args[1])
    settings["MAX_ITER"] = int(args[2])
    settings["ZOOM"] = Pure(int(args[3]), int(args[4]))
    settings["X_ORIG"] = Pure(int(args[5]), int(args[6]))
    settings["Y_ORIG"] = Pure(int(args[7]), int(args[8]))

    while True:
      try:
        await websocket.send("free")
        command, *args = (await websocket.recv()).split(" ")
        if command == "chill":
          break
        threads = int(args[0])
        pool = ThreadPool()
        itera = pool.map(
          lambda a: point(*a),
          [(int(args[2 * i + 1]), int(args[2 * i + 2])) for i in range(threads)]
        )
        out = " ".join([f"{args[2 * i + 1]} {args[2 * i + 2]} {itera[i]}"
                 for i in range(threads)])
        await websocket.send(f"ready {threads} {out}")
        print(args, itera)
        command = await websocket.recv()
        if command == "done":
          break
      except KeyboardInterrupt:
        break

asyncio.run(client())