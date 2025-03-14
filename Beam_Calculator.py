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
            l: numerical - length of beam
            I: numerical - 2nd moment of area (I) of the beam [m^4]
            E: numerical - Young's Modulous [Pa]
            loading: iterable of Singularity_function objects - all non reaction loads [N], [N/m], [Nm], ect.
            bc: iterable of dictionaries with the location and type of support
                loc: x position from left
                type: type of support (f/fixed, p/pinned)
            verbose: bool - whether to dump all calculation info to the console
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
            
        except:
            raise AttributeError('NOT ALL REQUIRED ARGUMENTS PASSED:'
                                 '\n\tl: number - length of beam'
                                 '\n\tI: number - 2nd moment of area'
                                 '\n\tE: number - Young\'s Modulous'
                                 '\n\tbc: list of dictionaries with fields:\n\t\tloc: number - location of support\nt\ttype: string - f for fixed support, p for pinned support'
                                 '\n\tloading: sing_eq - Singularity equation for the loading')

        ## Clean error types
        # Check number variables
        self.check_is_number(self.l, 'l')
        self.check_is_number(self.I, 'I')
        self.check_is_number(self.E, 'E')
        
        # Check boundary conditions
        for i in range(len(self.bc)):
            if self.bc[i]['type'].lower()[0] == 'p': # Pinned
                    self.bc[i]['type'] = 'p' # Standardize name
            elif self.bc[i]['type'].lower()[0] == 'f': # Fixed
                self.bc[i]['type'] = 'f' # Standardize name
            else: # Not pinned or fixed
                raise AttributeError(f'INVALID FORMAT FOR SUPPORT {self.bc[i]}\nSupport type must be either p/pinned or f/fixed')

            self.check_is_number(self.bc[i]['loc'], f'Boundary condition {self.bc[i]} location')     
        
        ## Check loading
        # If passed lis of sing functions, package into sing_eq
        if not(type(self.loading) == sing_eq or hasattr(self.loading, '__iter__')):
            raise AttributeError(f'INVALID FORMAT FOR LOADING\nLoading should be a Singularity_equation object or an iterable of Singularity_functions')
        if hasattr(self.loading, '__iter__'):
            self.loading = sing_eq(self.loading)
        # Check each sing function
        for i in range(len(self.loading.sings)):
            self.check_is_number(self.loading.sings[i].coeff, f'Loading sing funct {self.loading.sings[i]} coeff')
            self.check_is_number(self.loading.sings[i].a, f'Loading sing funct {self.loading.sings[i]} a value')

        ## Solve Reactions
        self.solve_reactions()


    # Checks if a variable is numeric
    def check_is_number(self, var, name):
        '''
        INPUT:
            var: any - The variable to test
            name: string - How to refer to the variable if an error is raised
        '''
        try:
            float(var)
        except:
            raise AttributeError(f'{name} must be a number')


    # Solves for the reaction forces form each support and returns singularity equations
    def solve_reactions(self, print_results=True):
        '''
        INPUTS:
            print_results: bool - Whether to dump solutions to the console
        '''
        # Preallocate reaction info
        supp_sings = [] # List of singularity functions corresponding to a support or an integration constant
        supp_labels = [] # List of names of each reaction in B and columns of A in order
        n_fixed = 0 # Number of fixed supports
        x_fixed = [] # List of locations of fixed supports
        
        ## Unpack general information
        # x values of all supports
        x_supp = [i['loc'] for i in self.bc]

        # Process reaction info, for each support:
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
                raise AttributeError(f'INVALID FORMAT FOR SUPPORT\nSupport must be a dictionary with key pairs:\n\t\"loc\" corresponding to the x value of the support from the left\n\t\"type\" corresponding to the type of support(f/p for fixed/pinned)')
            
            # Make sure support is the correct type
            if supp['type'] == 'p':
                
                # Add to list for equations, label list
                supp_sings.append(sing(coeff=1, a=supp['loc'], pow=-1))
                supp_labels.append(f'Fr{i}')
            
            elif supp[type] == 'f':
                
                # Keep track of fixed supports for y' equations
                n_fixed = n_fixed + 1
                x_fixed.append(supp['loc'])

                # Add to list for equations, label list
                supp_sings.append(sing(coeff=1, a=supp['loc'], pow=-1))
                supp_sings.append(sing(coeff=1, a=supp['loc'], pow=-2))
                supp_labels.append(f'Fr{i}')
                supp_labels.append(f'Mr{i}')
            
        # Add integration constant info to supp lists
        supp_sings += [sing(coeff=1, a=0, pow=-1-i  , eval_all_a=True) for i in range(4)]
        supp_labels += ['C_shear', 'C_moment', 'C_y_slope', 'C_y']

        ## Build singularity equation for loads
        loading_sing = self.loading.copy()

        # List of lists of x values to evaluate for each integration
        # v, m  -> Evaluated at beam start and end
        # y' -> Evaluated at fixed suppports
        # y -> Evaluated at all supports
        x_eval = 2*[[0, self.l]]+ [x_fixed] + [x_supp]

        # Count total number of equations that need to be evaluated
        n_equations = sum([len(i) for i in x_eval])
        
        # Preallocate A, B
        # A matrix to store reaction forces.
        #   Cols: F1, M1, F2, M2, ... Fn, Mn, Cv, Cm, Cyp, Cy -> Mi only if pinned, see labels vector
        #   Rows: V(x1)...V(xn), M(x1)...V(xn), y'(x1)...y'(xn), y(x1)...y(xn)
        # B matrix to store loading forces for the relation: Ax + B = 0
        A = np.zeros([n_equations, n_equations])
        B = np.zeros([n_equations, 1])


        # For each integral:
        #   - Evaluate list of support singularity functions (includes Cs) at each x position and fill in A matrix row
        #   - Evaluate load singularity function  at each x position and fill in B value
        #   - Integrate support and load singularity functions
        working_row = 0
        divide_factors = [1,1,self.E*self.I, self.E*self.I]
        integral_names = ['shear', 'moment', 'slope', 'deflection']
        for i, integral_locs in enumerate(x_eval):
            
            # Integrate functions to current row
            for s in supp_sings:
                s.integrate()
            loading_sing.integrate()

            # For each x position per integral
            #   - Check if the location to evaluate is 0 (limit approaching from the left)
            #   - Evaluate supp_sings and populate the corresponding row of the A matrix
            #   - Evaluate loading_sing and populate the corresponding element of the B matrix
            for x in integral_locs:
                if x == 0:
                    limit_direction = 'negative'
                else:
                    limit_direction = 'positive'
                
                reaction_sing_value_list = [s.value(x, direction=limit_direction)/divide_factors[i] for s in supp_sings]

                # Add fixture singularity functions, integration constant, and Loading singularity function equations to the matrices
                A[working_row, :] = reaction_sing_value_list
                B[working_row] = loading_sing.value(x, direction=limit_direction)/divide_factors[i]
                working_row += 1

        # Solve Reactions
        sols = np.linalg.solve(A, -B)
        
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
        '''
        INPUTS:
            profile: string - the name of the profile to plot. Valid profile names are 
                shear
                moment
                slope
                deflection
            x: optional numpy array - the x values to plot the profiles on
            fig: optional pyplot figure - the pyplot figure to plot on
        '''
        try: # Check profile name
            eq = self.profiles[profile]
        except:
            raise AttributeError('INVALID PROFILE NAME FOR PLOTTING, VALID NAMES ARE: \n\tshear\n\tmoment\n\tslope\n\tdeflection')
        
        # Check and assign missing optionals
        if not x:
            x = np.linspace(0, self.l, 1000)
        if not fig:
            fig = plot

        # Plot profile, and centerline
        eq.plot(x=x, fig=fig, label=str.title(profile))
        fig.plot([0,self.l], [0,0], linestyle='--', lw='0.5', color='k')

        # Plot pinned supports hollow and fixed supports filled in
        pinned_list = []
        fixed_list = []
        for bc in self.bc:
            if bc['type'] == 'p':
                pinned_list.append(bc['loc'])
            elif bc['type'] == 'f':
                fixed_list.append(bc['loc'])
            else:
                raise AttributeError(f'BC type error, {bc[type]} is an invalid type')
            
        fig.scatter(pinned_list, np.zeros(len(pinned_list)), marker='o', facecolors='None', edgecolors='k', label='Pinned Supports')
        fig.scatter(fixed_list, np.zeros(len(fixed_list)), marker='o', facecolors='k', edgecolors='k', label='Fixed Supports')
        fig.legend()
        fig.xlabel('x[m]')
        fig.ylabel('y[m]')


    # Debug print statement, only prints when verbose set to true
    def vprint(self, string):
        if self.verbose:
            print(string)


    @staticmethod
    def I(**kwargs):
        '''
        INPUTS:
            kwargs: kwargs for the following fields
                shape: string - Cross sectional shape of the beam, the following are valid
                    rectangle
                    circle
                dims: iterable/numeric - cross sectional dimensions of the beam. Structure based on shape argument
                    shape = rectangle: [width, height]
                    shape = circle: diameter

        OUTPUTS:
            I: numeric - The 2nd moment of area
        '''
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
    # loading = sing_eq([sing(coeff=2, a=1, pow=-1)])
    loading = [sing(coeff=2, a=1, pow=-1), sing(coeff=2, a=3, pow=-1)]
    bc = [
            {'loc':0, 'type': 'p'}
            ,{'loc':0.5, 'type': 'p'}
            ,{'loc':1.5, 'type': 'p'}
            ,{'loc':2, 'type': 'p'}
         ]
    
    a = sing_calc(l=l, I=I, E=E, loading=loading, bc=bc, verbose=False)
    # a.plot('deflection')
    # a.plot('slope')
    # a.plot('moment')
    a.plot('shear')
    plot.show()

