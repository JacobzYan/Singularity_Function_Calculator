from Beam_Calculator import *



# Functional test Ex 1 in notebook
l1=0.02375
l2=0.0314
l3=0.028

l = l1+l2+l3 #[m]
d = .03 # [m]
E = 71.7 *10**9 #[Pa]
I = sing_calc.I(shape='circle', dims=d)

# loading = sing_eq([sing(coeff=2, a=1, pow=-1)])
loading = [
    sing(coeff=3396.24, a=l1+l2, pow=-1), # Force
    sing(coeff=274, a=l1+l2, pow=-2), # Moment
    ]
bc = [
        {'loc':l1+l2+l3, 'type': 'p'}
        ,{'loc':l1, 'type': 'p'}
        ,{'loc':0, 'type': 'f'}
        ,{'loc':l2, 'type': 'p'}
    ]

a = sing_calc(l=l, I=I, E=E, loading=loading, bc=bc, verbose=False)

fig = plot.figure()
m_plot = fig.add_subplot(1,2,1)
d_plot = fig.add_subplot(1,2,2)


a.plot('deflection',fig=d_plot)
# a.plot('slope')
a.plot('moment',fig=m_plot)
# a.plot('shear')
plot.show()