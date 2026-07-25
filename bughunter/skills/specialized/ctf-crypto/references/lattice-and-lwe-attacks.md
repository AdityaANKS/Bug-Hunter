# grid attack and LWE

## basic concepts

```
grid (Lattice): Z^n Discrete additive subgroups in
Geki (Basis): Generate a lattice of linearly independent vectors
LLL algorithm: Find the approximate shortest vector of the lattice basis (SVP approximate)
CVP (Closest Vector Problem): Find the nearest vector
SVP (Shortest Vector Problem): Find the shortest vector
```

## LLL algorithm

```python
# SageMath accomplish
"""
A = matrix(ZZ, [[...], [...], ...])  # lattice basis matrix
B = A.LLL()  # LLL stipulation base
# B The column vector of is the closest lattice vector
```

## Hidden Number Problem (HNP)

```python
"""
known: (d_i, (t_i * a + k_i * d_i) mod p) Partial bit
recover: a (private key)
use Coppersmith find out k_i
"""
# SageMath
def hnp_attack(d, t, bits, p):
    F.<x> = PolynomialRing(Zmod(p))
    # construct polynomials...
```

## Coppersmith Related

```python
"""
Coppersmith Find the small root of a polynomial:
f(x) = 0 mod n, |x| < n^(1/d)
in d is the polynomial degree
"""

# SageMath
def coppersmith_small_root(f, n, d, m):
    """f(x) = 0 mod n, Looking for small roots x, |x| < n^(1/(d*omega))"""
    # construct lattice union LLL
```

## LWE (Learning With Errors)

```python
"""
LWE question:
known: (A, b = As + e) mod q
recover: s (private key)
in e is the small error vector

Common attacks:
1. Enumeration small error (e Very young)
2. BKW algorithm
3. reduced to SVP/CVP
"""
```

## HNP Attack template

```python
# SageMath: Restore from partial private key RSA private key
"""
DCP (Diffie-Hellman Claw Problem) variant
Use lattice reduction to solve
"""

# Basic Template
"""
F = GF(p)
P.<x> = PolynomialRing(F)

# Construct basis matrix
# Application LLL
# Extract private key from the specification base
"""
```

## General Template for Attack Formats

```python
# Consider Format attacks when encountering the following scenarios:
# 1. Multiple equations with unknowns and "Minor errors"
# 2. Partial private key/Partial plaintext recovery
# 3. Reduce to the nearest vector problem in a grid

# Steps:
# 1. Modeling the problem in the grid CVP/SVP
# 2. Construct basis matrix
# 3. Use LLL/BKZ Protocol
# 4. Extracting solutions from specifications
```
