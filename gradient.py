import numpy
import cv2

# number of steps to generate
COLORS = 256

# colors used in the gradient
# int16 is used, because the difference between two colors may be negative
gradient = numpy.array([
  [0x8B, 0xC3, 0x4A],
  [0xFF, 0x57, 0x22],
  [0x00, 0x96, 0x88],
  [0xE9, 0x1E, 0x63],
  [0x67, 0x3A, 0xB7]
], numpy.int16)

# the color points given as relative to the whole palette
# the first must be 0, the last must be 1
gradient_map = [0, 0.2, 0.5, 0.8, 1]

colors = []

for i in range(COLORS):

  # find the color points interval
  index = 0
  while (i / COLORS) > gradient_map[index + 1]:
    index += 1

  # get the bounds of the interval
  start = gradient_map[index]
  end = gradient_map[index + 1]

  # get the relative difference
  delta = end - start
  pos = i / COLORS - start
  diff = pos / delta

  # get bound colors
  start = gradient[index]
  end = gradient[index + 1]

  # add the new color
  colors.append(start + (end - start) * diff)

# converting to numpy array
colors = numpy.array(colors, numpy.uint8)

# generate output with COLORS x 10 pixels
image = numpy.array([colors for _ in range(COLORS)], numpy.uint8)
cv2.imwrite("output.jpeg", cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
