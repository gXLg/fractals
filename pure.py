class Pure:

  def __init__(self, a, b = 0, prec = 1000):
    if not a:
      b = 0

    while not a % 10 and b > 0:
      b -= 1
      a //= 10

    if b > prec:
      a //= 10 ** (b - prec)
      b = prec
      if not a:
        b = 0
    self.prec = prec

    self.a = a
    self.b = b

  def __add__(self, p):
    sa = self.a
    sb = self.b
    pa = p.a
    pb = p.b

    if sb > pb:
      ta, tb = pa, pb
      pa, pb = sa, sb
      sa, sb = ta, tb

    sa *= 10 ** (pb - sb)

    return Pure(sa + pa, pb)

  def __sub__(self, p):
    return self + Pure(- p.a, p.b)

  def __mul__(self, p):
    return Pure(self.a * p.a, self.b + p.b)

  def __truediv__(self, p):
    return self * p.inverse()

  def inverse(self):
    a = self.a
    c = 0

    d = 1
    r = 0

    for i in range(self.prec):
      if not d: break
      if d > a:
        f = d // a
        d -= f * a
        r += f
      r *= 10
      d *= 10
      c += 1

    return Pure(r, c - self.b)

  def __str__(self):
    if(self.a < 0):
      a = - self.a
      m = "-"
    else:
      a = self.a
      m = ""
    t = 10 ** self.b
    b = str(a % t)
    a = str(a // t)
    return m + a + "." + b.zfill(self.b)

  def __hash__(self):
    return hash((self.a, self.b))

  def __le__(self, p):
    sa = self.a
    sb = self.b
    pa = p.a
    pb = p.b

    if sb > pb:
      pa *= 10 ** (sb - pb)
    else:
      sa *= 10 ** (pb - sb)

    return sa <= pa
