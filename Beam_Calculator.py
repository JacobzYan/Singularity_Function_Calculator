## Jacob Yan
## 12/18/2023
## This Class enables the calculations and interpretation of singularity functions

import numpy as np
from matplotlib import pyplot as plot
from Singularity_function import Singularity_function as sing
from Singularity_equation import Singularity_equation as sing_eq


class sing_calc():


    # By default, create a 1000mm long cantilevered beam with a moment of inertia from default values - DEPRICATE DEFAULT CASE LATER
    def __init__(self, verbose=False, **kwargs):
        '''
        INPUT: 
            l:
                numerical
                length of beam
            I:
                numerical
                2nd moment of area (I) of the beam [m^4]
            E:
                numerical
                Young's Modulous [Pa]
            loading:
                iterable of Singularity_function objects
                all non reaction loads [N], [N/m], [Nm], ect.
            bc:
                iterable of dictionaries with the location and type of support
                    loc: x position from left
                    type: type of support (f/fixed, p/pinned)
        ''' 

        # Bool to print out debug info
        self.verbose = verbose
        # Unpack geometry, loading, and BC or take default values - DEPRICATE DEFAULT CASE LATER
        try:
            assert(type(kwargs['loading'] == sing_eq))
            self.l = kwargs['l']
            self.I = kwargs['I']
            self.E = kwargs['E']        
            self.bc = kwargs['bc']
            self.loading = kwargs['loading']
            self.state = 'CUSTOM'
            
        except: # DEPRICATE DEFAULT CASE LATER
            self.l = .5 # Length of the beam in m
            self.I = sing_calc.I() # Second moment of area
            self.E = 2.35 * 69**9 # Young's Modulous [Pa] typical for Al
            self.loading = sing_eq([sing(coeff=100, a=self.l/2, pow=-1)])
            self.bc = [{'loc': 0, 'type': 'pinned'}, {'loc': self.l, 'type': 'pinned'}]
            self.state = 'DEFAULT'

        # Solve Reactions
        self.solve_reactions()


    # Solves for the reaction forces form each support and returns singularity equations
    def solve_reactions(self, print_results=True):
        # Preallocate reaction info
        supp_sings = [] # List of singularity functions corresponding to an equation
        supp_labels = [] # List of names of each reaction in B and columns of A in order
        n_fixed = 0 # Number of fixed supports
        x_fixed = [] # List of locations of fixed supports
        
        # Unpack more general information
        x_supp = [i['loc'] for i in self.bc] # x values of all supports

        # Process reaction info, for each support:
        #   - Sanitize support type
        #   - Classify support type
        #   - Add singularity function to a list that corresponds to the proportion of the reaction force/moment used for each equation row
        #   - Add reaction force/moment labels to a list of labels to decode later
        #   - Add list of points to evaluate equations at (0 and L for v and m, at each fixed support for y', at each support for y)
        # Build list of singularity functions to populate matrix, list of labels for columns, list of points to build equations at
        for i, supp in enumerate(self.bc):
            
            # Sanitize Support dict arguments
            try:
                # Ensure dict arguments exist
                supp['loc']
                supp['type']
            except: # dict arguments not found
                raise Exception(f'INVALID FORMAT FOR SUPPORT\nSupport must be a dictionary with key pairs:\n\t\"loc\" corresponding to the x value of the support from the left\n\t\"type\" corresponding to the type of support(f/p for fixed/pinned)')
            
            # Make sure support is the correct type
            if supp['type'].lower()[0] == 'p': # Pinned
                
                supp['type'] = 'p' # Standardize name
                
                # Add to list for equations, label list
                supp_sings.append(sing(coeff=1, a=supp['loc'], pow=-1))
                supp_labels.append(f'Fr{i}')
            elif supp['type'].lower()[0] == 'f': # Fixed
                
                supp['type'] = 'f' # Standardize name
                
                # Keep track of fixed supports for y' equations
                n_fixed = n_fixed + 1
                x_fixed.append(supp['loc'])

                # Add to list for equations, label list
                supp_sings.append(sing(coeff=1, a=supp['loc'], pow=-1))
                supp_sings.append(sing(coeff=1, a=supp['loc'], pow=-2))
                supp_labels.append(f'Fr{i}')
                supp_labels.append(f'Mr{i}')
            else: # Not pinned or fixed
                raise Exception('INVALID FORMAT FOR SUPPORT TYPE\nSupport type must be either p/pinned or f/fixed')
            
        supp_labels += ['C_shear', 'C_moment', 'C_y_slope', 'C_y']

        # Build singularity equation for loads
        if not(type(self.loading) == sing_eq or hasattr(self.loading, '__iter__')):
            raise Exception(f'INVALID FORMAT FOR LOADING\nLoading should be a Singularity_equation object or an iterable of Singularity_functions')
        if hasattr(self.loading, '__iter__'):
            loading_sing = sing_eq(self.loading)
        else:
            loading_sing = self.loading

        # List of lists of x values to evaluate for each integration
        # v, m  -> Evaluated at start and end
        # y' -> Evaluated at fixed suppports
        # y -> Evaluated at all supports
        x_eval = 2*[[0, self.l]]+ [x_fixed] + [x_supp]

        # Count total number of equations that need to be evaluated
        n_equations = sum([len(i) for i in x_eval])
        
        # Preallocate A, B
        # A matrix to store reaction forces.
        #   Cols: F1, M1, F2, M2, ... Fn, Mn, Cv, Cm, Cyp, Cy -> Mi only if pinned, see labels vector
        #   Rows: V(x1)...V(xn), M(x1)...V(xn), y'(x1)...y'(xn), y(x1)...y(xn)
        A = np.zeros([n_equations, n_equations])
        B = np.zeros([n_equations, 1])

        # For each integral:
        #   - Evaluate list of support singularity functions at each x position and fill in A matrix row
        #   - Evaluate load singularity function  at each x position and fill in B value
        #   - Add C value
        #   - Integrate support and load singularity functions
        working_row = 0
        divide_factors = [1,1,self.E*self.I, self.E*self.I]
        integral_names = ['shear', 'moment', 'slope', 'deflection']
        for i, integral_locs in enumerate(x_eval):

            # Integrate functions to current row
            for s in supp_sings:
                s.integrate()
            loading_sing.integrate()

            # Add C for the integration
            A[len(supp_sings)+i, i] = 1

            # For each x position per integral
            #   - Evaluate supp_sings and populate the corresponding row of the A matrix
            #   - Evaluate loading_sing and populate the corresponding element of the B matrix
            for x in integral_locs:
                if x == 0:
                    limit_direction = 'negative'
                else:
                    limit_direction = 'positive'
                
                reaction_sing_value_list = [s.value(x, direction=limit_direction)/divide_factors[i] for s in supp_sings]

                # Add fixture singularity functions, integration constant, and Loading singularit function equations to the matrices
                A[working_row, :len(supp_sings)] = reaction_sing_value_list
                A[working_row, i+3] = 1
                B[working_row] = loading_sing.value(x, direction=limit_direction)
                working_row += 1
        
        # Solve Reactions
        sols = np.linalg.solve(A, B)
        
        # Build list for c singularity functions
        C_sing_list = [sing(coeff=1, a=0, pow=i) for i in range(4)]
        
        # Combine coefficients with sing equations and add loading sing equation for the full deflection sing equation
        deflection_sing_eq = sing_eq([i[0].copy()*i[1].copy() for i in zip(supp_sings + C_sing_list, sols)]) + loading_sing

        # Remove sing functions that have coefficients of zero, 2 loops to prevent issues in incorrect orders
        to_remove = []
        for sing_i in deflection_sing_eq.sings:
            try:
                coeff = sing_i.coeff[0]
            except:
                coeff = sing_i.coeff
            self.vprint(f'Coeff: {coeff}')
            if coeff == 0:
                self.vprint(f'\tREMOVING')
                to_remove.append(sing_i)
        for sing_i in to_remove:
            deflection_sing_eq.delete_sing(sing_i)

        # Save full singularity equations
        integral_names.reverse() # Start with deflection, reverse to derivitave back to shear
        divide_factors.reverse()
        self.profiles = {}
        for i, name in enumerate(integral_names):
            self.profiles[name] = deflection_sing_eq.copy() / divide_factors[i]
            deflection_sing_eq.derivative()

        # Debug Info
        debug_str = ('States Read in:\n'
                    f'self.l: {self.l}\n'
                    f'self.I:{self.I}\n'
                    f'self.loading: {self.loading}\n'
                    f'self.bc: {self.bc}\n'
                    f'self.state: {self.state}\n'
                    f'n_eq: {n_equations}\n'
                    f'x_eval: {x_eval}\n'
                    f'A: \n{A}\n'
                    f'B: \n{B}\n'
                    f'Load Equation: {loading_sing}\n'
                    )
        self.vprint(debug_str)

        # Print Output
        if print_results:
            print(f'Reactions')
            for i, label in enumerate(supp_labels):
                print(f'\t{label}: {sols[i]}')
            print(f'Profiles:')
            for profile in self.profiles.keys():
                print(f'\n{profile}: \n{self.profiles[profile]}')


    # Plots out value
    def plot(self, profile, x=None, fig=None):
        
        try: # Check profile name
            eq = self.profiles[profile]
        except:
            raise('INVALID PROFILE NAME FOR PLOTTING, VALID NAMES ARE: \n\tshear\n\tmoment\n\tslope\n\tdeflection')
        
        if not x:
            x = np.linspace(0, self.l, 1000)
        
        eq.plot(x=x, fig=fig)


    # Debug print statement, only prints when verbose set to true
    def vprint(self, string):
        if self.verbose:
            print(string)

    @staticmethod
    def I(**kwargs):

        # Unpack valid arguments
        temp_shape = kwargs.get('shape', 'rectangle')
        dimensions = kwargs.get('dims', [20, 20])
        
        # Calculate I
        if temp_shape == 'rectangle':
            I = (dimensions[0] * dimensions[1]**3) / 12
        elif temp_shape == 'circle':
            I = np.pi * (dimensions**4) / 4 * 2**-4
        
        return I





# Test Function
if __name__ == '__main__':
    
    # Functional test Ex 1 in notebook
    l = 3 #[m]
    I = 1000 #[m^4]
    E = 10 #[N/m^2]
    loading = sing_eq([sing(coeff=-2, a=3, pow=-1)])
    bc = [{'loc':0, 'type': 'f'},
          {'loc':2, 'type': 'p'}]
    
    a = sing_calc(l=l, I=I, E=E, loading=loading, bc=bc, verbose=False)
    a.plot('deflection')
    plot.show()

