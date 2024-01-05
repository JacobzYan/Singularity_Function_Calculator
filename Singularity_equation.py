# Packages multuple singularity functions into one equation


from Singularity_function import Singularity_function as sing

'''
INPUT:
    *sings
        multiple Singualrity_function objects
        list of singularity functions to be included in the equation    
'''


class Singularity_equation:
    
    # Define own iterable of all singularity functions
    def __init__(self, *sings: sing):
        
        # Sanitize input
        try:
            for i in sings:
                assert(type(i) == sing)
        except:
            raise Exception('INVALID INPUT FOR SINGULARITY EQUATION')
        
        self.sings = list(sings)
        self.sort_sings()


    # Return value of all singularity functions
    def value(self, x):
        value = 0.0
        for i in self.sings:
            value += i.value(x)

        return value
    

    # Integrate all singularity functions
    def integrate(self):
        for i in range(len(self.sings)):
            self.sings[i].integrate()

    # Take the derivitive of all singularity functions
    def derivative(self):
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
            print(f'ERROR: {sing} not found')
    # Sort sings by a value
    def sort_sings(self):
        self.sings = sorted(self.sings)


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

    test = Singularity_equation(a, b, c, d)
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