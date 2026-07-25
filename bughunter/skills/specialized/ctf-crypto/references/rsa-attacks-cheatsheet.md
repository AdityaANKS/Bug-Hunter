# RSA Attack cheat sheet

## Attack selection decision tree

```
known n, e, c
├── e very small (e=3)?
│   ├── Encrypting the same plaintext multiple times (multiple groupsc)? → Håstad broadcast attack
│   └── only one group? → Small exponential root attack (low probability)
├── multiple groups (n, e, c)?
│   ├── n same? → common mode attack
│   ├── e same? → Håstad broadcast attack
│   └── p or q Have common factors? → GCD break down
├── e very big (>65537)?
│   └── d may be small → Wiener attack
├── n decomposable?
│   ├── Fermat break down (p≈q)
│   ├── Pollard p-1 (p-1 Factor is small)
│   ├── Williams p+1 (p+1 Factor is small)
│   └── Online inquiry (factordb)
└── Partially known information?
    ├── Partial plain text → Coppersmith
    ├── partp → Coppersmith
    └── partd → Direct construction
```

## small exponential attack (e=3)

### Low index broadcast attack (Håstad)
```python
from gmpy2 import iroot
from functools import reduce

def hastard_broadcast(cs, ns, e=3):
    """When the same plaintext is e different groups n When encrypting"""
    # CRT Solve
    N = reduce(lambda a, b: a * b, ns)
    x = 0
    for i in range(e):
        Mi = N // ns[i]
        yi = pow(Mi, -1, ns[i])
        x += cs[i] * Mi * yi
    x %= N
    m = iroot(x, e)
    if m[1]:
        return int(m[0])
    return None
```

## common mode attack

```python
from gmpy2 import gcd

def common_modulus_attack(c1, c2, e1, e2, n):
    """same plaintext、samen、differenteencryption"""
    g, s1, s2 = extended_gcd(e1, e2)
    if s1 < 0:
        c1 = pow(c1, -1, n)
        s1 = -s1
    if s2 < 0:
        c2 = pow(c2, -1, n)
        s2 = -s2
    m = (pow(c1, s1, n) * pow(c2, s2, n)) % n
    return m

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    g, x, y = extended_gcd(b % a, a)
    return g, y - (b // a) * x, x
```

## Wiener attack (e very big, d very small)

```python
def wiener_attack(e, n):
    """when d < n^(1/4) valid when"""
    cf = continued_fraction(e, n)
    convergents = get_convergents(cf)
    for k, d in convergents:
        if k == 0:
            continue
        phi = (e * d - 1) // k
        # Check if it is valid phi
        x = n - phi + 1
        disc = x * x - 4 * n
        if disc >= 0:
            s = int(disc ** 0.5)
            if s * s == disc:
                return d
    return None
```

## Fermat break down (p ≈ q)

```python
from gmpy2 import is_square, iroot

def fermat_factor(n):
    """when p and q Effective when very close"""
    a = iroot(n, 2)[0] + 1
    b2 = a * a - n
    while not is_square(b2):
        a += 1
        b2 = a * a - n
    p = a + iroot(b2, 2)[0]
    q = a - iroot(b2, 2)[0]
    return int(p), int(q)
```

## Pollard p-1 attack

```python
from math import gcd

def pollard_p1(n, B=100000):
    """when p-1 factors are all smaller than B valid when"""
    a = 2
    for j in range(2, B):
        a = pow(a, j, n)
        d = gcd(a - 1, n)
        if 1 < d < n:
            return d, n // d
    return None
```

## Coppersmith attack (known partial plaintext)

```python
# use SageMath
# When the high or low bits of the plaintext are known
# m = known_part + unknown_part
# unknown_part < n^(1/e)

# Sage accomplish:
P.<x> = PolynomialRing(Zmod(n))
f = (known_prefix + x)^e - c
f = f.monic()
roots = f.small_roots()
if roots:
    m = known_prefix + roots[0]
```

## Online decomposition tool

- https://factordb.com — query decomposed n
- http://sagecell.sagemath.org — online Sage calculate
