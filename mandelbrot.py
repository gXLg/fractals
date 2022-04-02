import cv2
import numpy
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
import math

from pure import Pure

interpolate = lambda a, b, p: a + (b - a) * p

WIDTH = 1000
HEIGHT = 1000
MAX_ITER = 500
#ZOOM = 200
ZOOM = Pure(20_000)
X_ORIG = Pure(-129, 2)
Y_ORIG = Pure(699, 4)
#X_ORIG = -1.29
#Y_ORIG = 0.0699

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

#for Z in range(1000):
if True:

  def point(x, y):
    x = (Pure(x) - Pure(WIDTH // 2)) / ZOOM + X_ORIG
    y = (Pure(HEIGHT // 2) - Pure(y)) / ZOOM + Y_ORIG
    #x = (x - WIDTH // 2) / ZOOM + X_ORIG
    #y = (HEIGHT // 2 - y) / ZOOM + Y_ORIG

    # cardioid check
    qua = Pure(25, 2)
    #qua = 0.25
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
    #za = 0
    #zb = 0
    #a2 = 0
    #b2 = 0

    s = set()
    itera = 0
    while itera < MAX_ITER:

      #print(iter, za, zb)
      s.add((za, zb))

      zb = Pure(2) * za * zb + y
      za = a2 - b2 + x
      a2 = za * za
      b2 = zb * zb

      if (za, zb) in s:
        return MAX_ITER - 1 #colors[-1]
      elif Pure(65536) <= a2 + b2:
        #return iter #colors[COLORS * iter // MAX_ITER]
        #nu = math.log(math.log(a2 + b2)) / math.log(2)
        #return int(itera + 1 - nu)

        # how much is it outside?
        return itera

      itera += 1
    return MAX_ITER - 1 #colors[-1]

  def lines(y):
    print(y)
    innerPool = ThreadPool()
    def line(x):
      return point(x, y)

    out = innerPool.map(line, range(WIDTH))
    innerPool.close()
    return out

  pool = Pool()
  out = pool.map(lines, range(HEIGHT))
  pool.close()
  print("data ready, generating...")

  """
  image = numpy.array([
    [
      interpolate(colors[int(x) - 1], colors[int(x)], x % 1) for x in y
    ] for y in out
  ], numpy.uint8)

  """

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
  #"""

  #cv2.imwrite(f"zoom/output{Z}.png", cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
  cv2.imwrite(f"output.png", cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

  #ZOOM *= 1.2
  #print("Ready", Z)
