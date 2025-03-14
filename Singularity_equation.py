# Packages multuple singularity functions into one equation
from Singularity_function import Singularity_function as sing
from matplotlib import pyplot as plot
import numpy as np
import numbers

'''
INPUT:
    sings
        Iterable of Singualrity_function objects
'''


class Singularity_equation:


    # Define own iterable of all singularity functions
    def __init__(self, sings):
        
        # Sanitize input
        try:
            for i in sings:
                assert(type(i) == sing)
        except:
            raise Exception('INVALID INPUT FOR SINGULARITY EQUATION')
        
        self.sings = list(sings)
        self.sort_sings()


    # Return value of all singularity functions
    def value(self, x, direction='positive'):
        # Check if x is iterable
        iterable = True
        try:
            iter(x)
        except:
            iterable = False

        # Single x values
        if not iterable:
            value = 0.0
        # Iterable x values
        else:
            value = np.zeros(x.size)
        
        # Assign Values
        for sing in self.sings:
                value += sing.value(x, direction=direction)
        return value


    # Integrate all singularity functions
    def integrate(self, *args):
        # Check if passed number of iterations
        try:
            iterations = args[0]
        except:
            iterations = 1
        # Integrate given number of times
        for j in range(iterations):
            # Integrate each singularity function
            for i in range(len(self.sings)):
                self.sings[i].integrate()
        return self


    # Take the derivitive of all singularity functions
    def derivative(self, *args):
        # Check if passed number of iterations
        try:
            iterations = args[1]
        except:
            iterations = 1
        # Integrate given number of times
        for j in range(iterations):
            # Integrate each singularity function
            for i in range(len(self.sings)):
                self.sings[i].derivitave()


    # Add singularity function
    def add_sing(self, sing:sing):
        self.sings.append(sing)
        self.sort_sings()


    # Remove singularity function
    def delete_sing(self, sing:sing):
        try:
            self.sings.remove(sing)
        except:
            raise(f'{sing} not found to delete')


    # Sort sings by a value
    def sort_sings(self):
        self.sings = sorted(self.sings)


    # Plot given a figure
    def plot(self, x, label=None, fig=None):
        """
        Plots the value of the singularity function an a given range with added c functions
        Inputs:
            x: Iterable of points to plot on -> make sure this behaves like np vector not a list
            fig: Matplotlib figure object to plot on
            c_function: A function that takes in an iterable and returns the corresponding values for c # REPHRASE THIS 
        """
        y = self.value(x)

        if not fig:
            fig = plot
        fig.plot(x, y, label=label)


    '''-----------------------------MAGIC METHODS-----------------------------'''


    # Add elements to singularity equation
    def __add__(self, new):
        # Check type of object to add
        if hasattr(new, '__iter__'): # Iterable
            if type(new[0]) == sing: # of sings
                self.sings += new
                self.sort_sings()
            else:
                raise Exception(f"CANNOT ADD {new} TO SING EQ OBJECT")
        elif isinstance(new, Singularity_equation): # Singularity Equation
            for sing in new.sings:
                self.add_sing(sing)
        elif isinstance(new, sing): # Single sing
                self.add_sing(new)
        else:
            raise Exception(f"CANNOT ADD {new} TO SING EQ OBJECT")
        return self


    # Add elements with negative - NOT IMPLEMENTED
    def __sub__(self, new):
        raise('SINGULARITY EQUATION SUBTRACTION NOT YET IMPLEMENTED')
        
        # # Check type of object to add
        # if hasattr(new, '__iter__'):
        #     if type(new[0]) == sing:
        #         for sing in new:
        #             sing.coeff = -sing.coeff
        #         self.sings += new
        #     else:
        #         raise Exception(f"CANNOT ADD {new} TO SING EQ OBJECT")
        # else:
        #     if type(new) == sing:
        #         new.coeff = -new.coeff
        #         self.sings.append(new)
        #     else:
        #         raise Exception(f"CANNOT ADD {new} TO SING EQ OBJECT")


    # Multiply coefficients
    def __mul__(self, coeff):
        if not isinstance(coeff, numbers.Number):
            raise Exception(f'MUST MULTIPLY SINGULARITY FUNCTION BY A NUMBER')
        for sing in self.sings:
            sing.coeff *= coeff
        return self


    # Divide coefficients
    def __truediv__(self, coeff):
        if not isinstance(coeff, numbers.Number):
            raise Exception(f'MUST DIVIDE SINGULARITY FUNCTION BY A NUMBER')
        for sing in self.sings:
            sing.coeff /= coeff
        return self

    
    # Return a copy of the singularity equation
    def copy(self):
        temp_sings = []
        for i in self.sings:
            i_mod = i.copy()
            temp_sings.append(i_mod)
        return Singularity_equation(temp_sings)


    # return string representation of the equation
    def __str__(self):

        output = '\n'

        # Add each sing function output to the full output
        for i in self.sings:     
            
            if i.coeff < 0:
                sign = '- '
            else:
                sign = '+ '

            output += sign + i.to_str_abs() + '\n'
        
        return output.strip('\n')
    

    def __len__(self):
        return len(self.sings)





# Test equation functionality
if __name__ == '__main__':
    # Def sing. functions
    a = sing()
    b = sing(a = 10, pow = -1, coeff = -10)
    c = sing(a = 10, pow = -2, coeff = 30)
    d = sing(a = 20, pow = 0, coeff = -20)
    e = sing(a = 30, pow = 0, coeff = 0.001)
    # Test look at sing. states:
    print(f'a:{a.state}\nb:{b.state}\nc:{c.state}\nd:{d.state}')

    test = Singularity_equation([a, b, c, d])
    print(f'\nORIGINAL-----------------------------------------------------------------------\nf(x) = \n{test}')
    for i in range(2):
        print(f'\nINTEGRATIONS:{i}-----------------------------------------------------------------------\nf(x) = \n{test}')
        print(f'\tVALUE AT 200: {test.value(200)}\n')
        test.integrate()
    
    print('ADDING SING')
    test.add_sing(e)
    print(test)

    for i in range(3):
        print(f'\nINTEGRATIONS:{i}-----------------------------------------------------------------------\nf(x) = \n{test}')
        print(f'\tVALUE AT 200: {test.value(200)}')
        test.integrate()

    test.derivative()
    print('REMOVING SING')
    f = sing(coeff = 15.0, a = 10, pow = 2)
    test.delete_sing(f)
    print(test)
    print(f'Value at 0: {test.value(0)}')
    print(f'Value at L: {test.value(200)}')

    print(f'\nPLOTTING:-----------------------------------------------------------------------\n')
    l = 0.0508
    l = 0.019
    # l = 0.0762
    L = l+.09385
    EI = 2822.7


    p1 = sing(a=0, pow=-1, coeff=-8634.08/EI) # Fs1
    p2 = sing(a=l, pow=-1, coeff=11257.56/EI) # Fs2
    p3 = sing(a=L, pow=-1, coeff=-2623.48/EI) # Fl
    p4 = sing(a=L, pow=-2, coeff=192.39/EI)   # Ml
    p = Singularity_equation([p1, p2, p3, p4])
    p = p.integrate(4)
    def c(x):
        return -x**3*p1.coeff * p2.a**3

    x_plot = np.arange(0, L*1.1, 0.0001) # RANGE OF VALUEs, resolution
    print(f'p: \n{p}')
    print(f'x_plot(Sing eq):\n{x_plot}')
    print(f'c slope: {c(1)}')
    p.plot(x=x_plot, c_function=c, fig=None)
    # plot.show()

    print('Testing Copy functionality')
    da = sing(a=0, pow=5, coeff=2)
    db = sing(a=l, pow=-1, coeff=1)
    d = Singularity_equation([da, db])
    d2 = d.copy()
    for i in range(3):
        print(f'\tDerivative {i}: {d}')
        print(f'\tCopy: {d2}')
        d.derivative()