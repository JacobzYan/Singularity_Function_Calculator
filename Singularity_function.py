## Jacob Yan
## 12/18/2023
## This Class enables the logic of singularity function

# from sympy import symbols as sym
import numpy as np
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
        
        # Unpack arguments or use defaults - DEPRICATE DEFAULTS
        try:
            # Unpack values
            self.coeff = kwargs['coeff']
            self.a = kwargs['a']
            self.pow = kwargs['pow']
            
            # Sanitize input
            self.state = 'CUSTOM'

        except:
            # Assign default values
            self.coeff = 100
            self.a = 250
            self.pow = -2
            self.state = 'DEFAULT'
    

    # Integrate singularity Function
    def integrate(self, n=1):

        for i in range(n):    
            # Update power
            self.pow += 1

            # Update Coefficent
            if self.pow > 0:
                self.coeff /= self.pow

        return self


    # Take the derivitave of the singularity function
    def derivitave(self):
        
        # Update Coefficent
        if self.pow > 0:
            self.coeff *= self.pow

        # Update power:
        self.pow -= 1


    # Returns value of the singularity function
    def value(self, x, direction='positive'):
        # Direction - Evaluate limit from negative or positive direction, changes behavior when x=a
        # Check if x is iterable
        iterable = True
        try:
            iter(x)
        except:
            iterable = False

        # Single x values
        if not iterable:
            sol = self.single_value(x, direction)
        
        # Iterable x values
        else:
            # Cast to Np array, reassign values in same shape as x
            x_np = np.array(x)
            sol = np.zeros(x_np.size)
            for i, xi in enumerate(x_np):
                sol[i] = self.single_value(xi, direction)
            
        return sol


# Returns polynomial value If power is positive or x >= a, used as a helper function for value
    def single_value(self, x, direction):
        if x - self.a < 0 or self.pow < 0:
            return 0
        
        result = self.coeff * (x - self.a) ** self.pow
        
        if x-self.a != 0:
            return result
        if direction[0].lower() == 'p':
            return result
        if direction[0].lower() == 'n':
            return 0
            

    # return string representation of singularity function
    def to_str_abs(self):
        return f'{abs(self.coeff)}<x-{self.a}>^({self.pow})'
    

    '''-----------------------------MAGIC METHODS-----------------------------'''

    
    def __str__(self):
        return f'{self.coeff} < x - {self.a}>^({self.pow})'


    # Objects equal if all parameters match
    def __eq__(self, other):
            return (self.coeff == other.coeff) and (self.a == other.a) and (self.pow == other.pow)


    # Compares a values, if the same, orders by lowest power
    def __lt__(self, other):
        if self.a == other.a:
            return self.pow > other.pow
        else:
            return self.a < other.a


    # Compares a values, if the same, orders by highest power
    def __gt__(self, other):
        if self.a == other.a:
            return self.pow < other.pow
        else:
            return self.a > other.a


    def __mul__(self, other):
        try:
            # Make sure is numeric
            assert(other*0 == 0)
            # Copy self
            temp = self.copy()
            
            # If nonprimative, copy other
            if hasattr(other, "copy") and callable(getattr(other, "copy")):
                other_processed = other.copy()
            else:
                other_processed = other
            temp.coeff *= other_processed
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


    def copy(self):
        self.coeff
        # If nonprimative coeff, copy coeff
        if hasattr(self.coeff, "copy") and callable(getattr(self.coeff, "copy")):
            return Singularity_function(coeff = self.coeff.copy(), a = self.a, pow = self.pow)
        else: 
            return Singularity_function(coeff = self.coeff, a = self.a, pow = self.pow)





# Test Functionality
if __name__  == '__main__':
    a = Singularity_function()
    print(f'Testing Integration:')
    for i in range(4):
        print(f'INTEGRATION #{i}')
        print(f'{a} = {a.value(300)} @ x = 300')
        print(f'At limit, {a.value(a.a)} @ x = {a}')
        a.integrate()
        print('\n')
    
    print(f'\nTesting iterable compatability')
    print(f'a: {a}')
    x = np.arange(249,253,1)
    print(f'np vector x: {a.value(x)}')

    print(f'\nTesting value:')
    b = Singularity_function(coeff=1, a=0, pow=0)
    print(f'{b} at x=0 -> {b.value(0)}')

    print(f'Testing edge cases:')
    print(f'Power of zero, x-a<0 (should be 0): {b.value(-1)}')
    print(f'Power of zero, x-a=0+ (should be 1): {b.value(0, direction='p')}')
    print(f'Power of zero, x-a=0- (should be 0): {b.value(0, direction='n')}')
    print(f'Power of zero, x-a > 0 (should be 1): {b.value(1)}')

    print(f'Testing integral and derivative preservation')
    c = Singularity_function(coeff=1, a=0, pow=0)
    for i in range(5):
        c.integrate()
        print(f'c: {c}')

    print('Testing Copy functionality')
    d = Singularity_function(coeff=1, a=0, pow=5)
    d2 = d.copy()
    for i in range(5):
        print(f'\tDerivative {i}: {d}')
        print(f'\tCopy: {d2}')
        d.derivitave()

