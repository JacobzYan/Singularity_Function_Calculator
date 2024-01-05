## Jacob Yan
## 12/18/2023
## This Class enables the calculations and interpretation of singularity functions

import numpy as np
from matplotlib import pyplot as plot
from Singularity_function import Singularity_function as sing
from Singularity_equation import Singularity_equation as sing_eq


class sing_calc():
    '''
    INPUT: 
        l:
            numerical
            length of beam
        MOI:
            numerical
            moment of interia (I) of the beam
        loading:
            iterable of Singularity_function objects
            all non reaction loads
        bc:
            name of boundary condition -> cant (cantelever), ff -> (fixed fixed), fp(fixed, pinned), pf(pinned, fixed), pp(pinned, pinned)
            boundary conditions for the beam ends
    ''' 
    # By default, create a 1000mm long cantilevered beam with a moment of inertia from default values
    def __init__(self, **kwargs):

        # Implement geometry, loading, and BC or take default values
        try:
            assert(type(kwargs['loading'] == sing_eq))

            self.l = kwargs['l']
            self.MOI = kwargs['MOI']            
            self.bc = kwargs['bc']
            self.loading = kwargs['loading']
            self.state = 'CUSTOM'
            
        except:
            self.l = 500 # Length of the beam in mm
            self.MOI = sing_calc.MOI() # Second moment of area
            self.loading = sing_eq(sing())
            self.bc = 'cant'
            self.state = 'DEFAULT'


        ## DEBUG
        print(f'self.l: {self.l}')
        print(f'self.MOI: {self.MOI}')
        print(f'self.loading: {self.loading}')
        print(f'self.bc: {self.bc}')
        print(f'self.state: {self.state}')


        # Set up bc
        # Sanitize bc
        if not(len(self.bc) == 2 or self.bc == 'cant'):
            self.bc = 'cant'
        
        # define end conditions
        if len(self.bc) != 2:
            self.ends = ['fixed', 'free']
        else:
            # Set default as ff
            self.ends = ['fixed', 'fixed']

            # If either end is pinned, update that end
            if self.bc[0] == 'p':
                self.ends[0] = 'pinned'
            if self.bc[1] == 'p':
                self.ends[1] = 'pinned'

        #  Define positions and slopes based on end condtions
            # '' -> undefined
            # NUMBER -> set to that number
        # Preallocate, assume all are free
        self.moment_bc = [0, 0]
        self.shear_bc = [0, 0]
        self.pos_bc = ['', '']
        self.slope_bc = ['', '']
        
        # Set BC for each end
        for i in [0, 1]:

            if self.ends[i] == 'fixed':
                self.slope_bc[i] = 0
                self.pos_bc[i] = 0

            if self.ends[i] == 'pinned':
                self.slope_bc[i] = ''
                self.pos_bc[i] = 0
            
            if self.ends[i] == 'free':
                self.slope_bc[i] = ''
                self.pos_bc[i] = ''
        
        ## Solve singularity function

        # Calculate Loading
        self.shear = self.loading.integrate()

        # Check RHS boundary condition
        if self.shear_bc[1] * 0 == 0:
            ## NOT YET IMPLEMENTED
            




        

        
        
    





    # Define beam moment of inertia
    def set_moment_of_inertia(self, **kwargs):
        self.MOI = sing_calc(kwargs)
    




     # Calculate Moment of intertia
    @staticmethod
    def MOI(**kwargs):

        # Unpack valid arguments
        try: 
            temp_shape = kwargs['shape']
            dimensions = kwargs['dims']
        except:
            temp_shape = 'rectangle'
            dimensions = [20, 20]
        
        # Calculate MOI
        if temp_shape == 'rectangle':
            MOI = (dimensions[0] * dimensions[1]**3) / 12
        elif temp_shape == 'circle':
            MOI = np.pi * (dimensions**4) / 4 * 2**-4
        
        return MOI





# Test Function
if __name__ == '__main__':
    
    m = sing_calc.MOI()
    print(f'DEFAULT MOI = {m}')

    print('\nDEFAULT CASES TEST -------------------------------------------------')
    a = sing_calc()
    print(f'a.shear_bc(): {a.shear_bc}')
    print(f'a.moment_bc(): {a.moment_bc}')
    print(f'a.slope_bc(): {a.slope_bc}')
    print(f'a.pos_bc(): {a.pos_bc}')


    print('\nCUSTOM CASE TEST -------------------------------------------------')
    b_load_1 = sing(coeff = 10, a = 100, pow = -2)
    b_load_2 = sing(coeff = 5, a = 200, pow = -1)
    b_loads = sing_eq(b_load_1, b_load_2)
    b = sing_calc(l = 300, MOI = sing_calc.MOI(), loading = b_loads, bc = 'pf')
    
    print(f'b.shear_bc(): {b.shear_bc}')
    print(f'b.moment_bc(): {b.moment_bc}')
    print(f'b.slope_bc(): {b.slope_bc}')
    print(f'b.pos_bc(): {b.pos_bc}')
