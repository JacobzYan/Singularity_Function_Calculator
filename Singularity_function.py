## Jacob Yan
## 12/18/2023
## This Class enables the logic of singularity function
import numpy as np
from sympy import symbols as sym

'''
Arguments
    coeff
        numerical or sym
        coefficent of singularity function
    a
        numerical or sym
        starting position of loading
    pow
        numerical
        defined by type of loading/stress
'''

class Singularity_function:


    # Initialize singularity function
    def __init__(self, **kwargs):
        
        # Unpack arguments or use defaults
        try:
            # Unpack values
            self.coeff = kwargs['coeff']
            self.a = kwargs['a']
            self.pow = kwargs['pow']
            
            # Sanitize input
            # TBI
            self.state = 'CUSTOM'

        except:
            # Assign default values
            self.coeff = 100
            self.a = 250
            self.pow = -2
            self.state = 'DEFAULT'
    

    # Integrate singularity Function
    def integrate(self):
        
        # Update power
        self.pow += 1

        # Update Coefficent
        if self.pow > 0:
            self.coeff /= self.pow


    # Take the derivitave of the singularity function
    def derivitave(self):
        
        # Update Coefficent
        if self.pow > 0:
            self.coeff *= self.pow

        # Update power:
        self.pow -= 1


    # Returns value of the singularity function
    def value(self, x):

        # Returns polynomial value If power is positive or x >= a
        if (self.pow < 0) or (x - self.a < 0):
            return 0.0
        else:
            return self.coeff * ((x - self.a) ** self.pow)


    def copy(self):
        return Singularity_function(coeff = self.coeff, a = self.a, pow = self.pow)


    # return string representation of singularity function
    def to_str_abs(self):
        return f'{abs(self.coeff)}< x - {self.a} >^({self.pow})'
    

    '''-----------------------------MAGIC METHODS-----------------------------'''

    
    def __str__(self):
        return f'{self.coeff}< x - {self.a} >^({self.pow})'
    

    # Objects equal if all parameters match
    def __eq__(self, other):
            return (self.coeff == other.coeff) and (self.a == other.a) and (self.pow == other.pow)
    

    # Compares a values, if the same, orders by lowest power
    def __lt__(self, other):
        if self.a == other.a:
            return self.pow > other.pow
        else:
            return self.a < other.a
    

    def __gt__(self, other):
        if self.a == other.a:
            return self.pow < other.pow
        else:
            return self.a > other.a


    def __mul__(self, other):
        try:
            assert(other*0 == 0)
            temp = self.copy()
            temp.coeff *= other
            return temp
        except:
            raise Exception(f'ERROR: CANNOT MULTIPLY SING BY {other}')
    

    def __truediv__(self, other):
        try:
            assert(other*0 == 0)
            temp = self.copy()
            temp.coeff /= other
            return temp
        except:
            raise Exception(f'ERROR: CANNOT DIVIDE SING BY {other}')





# Test Functionality
if __name__  == '__main__':
    a = Singularity_function()
    
    for i in range(4):
        print(f'INTEGRATION #{i}')
        print(f'{a} = {a.value(300)} @ x = 300')
        a.integrate()
        print('\n')