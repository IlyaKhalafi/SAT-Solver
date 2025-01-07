# SAT-Solver
A self-contained implementation of Linear &amp; Cubic SAT Solvers from book of ``Logic in Computer Science: Modelling and reasoning about systems`` by Michael Huth and Mark Ryan.

Unfortunately, due to the shortage of time, I did not have enough time to make my code as efficient as possible, and it also has boilerplate code. However, it may be useful for anyone seeking the implementation of these two algorithms because I did not find any implementation for them anywhere else.

# Reserved Keywords

- **\"T\"**: True value

- **\"F\"**: False value

- **\"and\"**, **\"&\"**: AND operator's name and sign
  
- **\"or\"**, **\"|\"**: OR operator's name and sign

- **\"implies\"**, **\"->\"**: IMPLY operator's name and sign 

- **\"neg\"**, **\"~\"**: NEGATE operator's name and sign 

# Methods

1. Parsing an expression:
```python
expr = Expression('(p and q) -> r')
```
**Both the name and sign of operators are supported by the parser.**

2. Making a deepcopy of an expression object:
```python
expr.copy()
```
**Additionally, this method is available in any subformula of an expression.**

3. Calculating the horn clause of an expression.
```python
expr.horn()
```

4. Convert an expression to its string form to print it:
```python
print(expr)
str(expr)
```
**This method is available in any subformula of an expression.**

5. Estimating the truth value of an expression with a truth assignment function represented as a dictionary:
```python
expr.estimate({'p': True, 'q': False, 'r': True})
```
**This method is available in any subformula of an expression.**

6. SAT Solver that works in **linear time complexity** mentioned in the book:
```python
expr.linear_sat_solver()
```

7. SAT Solver that works in **cubic time complexity** mentioned in the book:
```python
expr.cubic_sat_solver()
```

A number of test cases are available in the `verification.py` file. You can run this code with the command below:
> python3 verification.py
