# ECC Attack cheat sheet

## Elliptic Curve Basics

```python
# elliptic curve: y² = x³ + ax + b (mod p)
# Point arithmetic: P + Q, k*P
# ECDLP: known P, Q=k*P,beg k
```

## Attack options

| condition | Attack method | Applicable scenarios |
|------|---------|---------|
| level n is a smooth number | Pohlig-Hellman | n The factors are all small |
| Abnormal curve (p=n) | Smart attack | abnormal curve |
| Subgroup order is small | Kid group attack | order has large prime factors |
| Curve parameters are suspicious | Invalid Curve attack | non-standard curve |
| ECDSA nonce Reuse | deterministic attack | same k Sign twice |
| The order is very small | Violence/Baby-step Giant-step | n < 2^40 |

## Pohlig-Hellman attack

```python
# Sage accomplish
# When the group level n When the factors of are all small

P = EllipticCurve(GF(p), [a, b])
G = P(P_x, P_y)  # base point
Q = P(Q_x, Q_y)  # target point

n = P.order()  # Group level
factors = factor(n)

# Pohlig-Hellman
k = discrete_log(Q, G, operation='+')
# or specify method
k = Q.discrete_log(G)
```

## Smart attack (abnormal curve)

```python
# When the order of the curve is equal to the characteristic p (abnormal curve)
# E.lift_x() May fail but can be exploited p-adic promote

# Sage accomplish
def smart_attack(P, Q, p, a, b):
    """Smart attack, applicable to #E = p abnormal curve"""
    E = EllipticCurve(Qp(p), [a, b])
    P_lift = E.lift_x(ZZ(P.xy()[0]))
    Q_lift = E.lift_x(ZZ(Q.xy()[0]))
    
    pP = p * P_lift
    pQ = p * Q_lift
    
    x1 = pP.xy()[0] / pP.xy()[1]
    x2 = pQ.xy()[0] / pQ.xy()[1]
    
    k = ZZ(x2) / ZZ(x1) % p
    return k
```

## Invalid Curve attack

```python
# When the server does not verify that the point is on the curve
# It is possible to send a point that is not on a curve and may be on another curve
# If the order of that curve is smooth, you can use Pohlig-Hellman

# Construct: Select a' make y² = x³ + a'*x + b There are smooth steps
```

## ECDSA Nonce reuse attack

```python
"""
if ECDSA in the same nonce k Used for two signatures:
s1 = k^(-1) * (h1 + r*d) mod n
s2 = k^(-1) * (h2 + r*d) mod n

s1 - s2 = k^(-1) * (h1 - h2) mod n
k = (h1 - h2) * (s1 - s2)^(-1) mod n
d = (s1 * k - h1) * r^(-1) mod n  (private key)
"""

def ecdsa_nonce_reuse(r1, s1, h1, r2, s2, h2, n):
    """ECDSA nonce Reuse recovery private key"""
    from gmpy2 import invert
    # Confirm r Same
    assert r1 == r2
    k = ((h1 - h2) * invert(s1 - s2, n)) % n
    d = ((s1 * k - h1) * invert(r1, n)) % n
    return int(d)
```

## Common ECC CTF Question type

| Question type | Features | Attack |
|------|------|------|
| Standard curve + Small Order | n < 2^40 | Brute force |
| Standard curve + Smooth step | n There are minor factors | Pohlig-Hellman |
| Anomaly curve | #E = p | Smart Attack |
| Custom curve | a, b Suspicious | Invalid Curve / Decomposition degree |
| ECDSA Signature | Multiple sets of signatures | Nonce Reuse |
| Twisted Edwards | x² + a*y² = 1 + d*x²*y² | Convert to Weierstrass |
