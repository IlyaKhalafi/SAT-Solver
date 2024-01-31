from sat_solvers import *

if __name__ == '__main__':
    expr1 = Expression('~(p | q) & ~r')
    print('Expression 1: ', expr1)
    print('Expression 1 Horn Clause: ', expr1.horn())
    print('Linear Solver Response: ', expr1.horn().linear_sat_solver())
    
    print('-' * 30)
    
    expr2 = Expression('~(p & q)')
    print('Expression 2: ', expr2)
    print('Expression 2 Horn Clause: ', expr2.horn())
    print('Linear Solver Response: ', expr2.horn().linear_sat_solver())
    print('Cubic Solver Response: ', expr2.horn().cubic_sat_solver())