###############################################################################
# ferre.py: module for interacting with Carlos Allende Prieto's FERRE code
###############################################################################
from functools import wraps
import os
import subprocess
import numpy
def paramArrayInputDecorator(func):
    """Decorator to parse spectral input parameters given as arrays,
    assumes the arguments are: something,teff,logg,metals,am,nm,cm,vmicro="""
    @wraps(func)
    def scalar_wrapper(*args,**kwargs):
         if numpy.array(args[1]).shape == ():
             scalarOut= True
             newargs= (args[0],)
             for ii in range(len(args)-1):
                 newargs= newargs+(numpy.array([args[ii+1]]),)
             args= newargs
             if not kwargs.get('vm',None) is None:
                 kwargs['vm']= numpy.array([kwargs['vm']])
         else:
             scalarOut= False
         result= func(*args,**kwargs)
         if result is None: return result
         if scalarOut:
             return result[0,:]
         else:
             return result
    return scalar_wrapper

def run_ferre(dir,verbose=False):
    """
    NAME:
       run_ferre
    PURPOSE:
       run an instance of FERRE
    INPUT:
       dir - directory to run the instance in (has to have an input.nml file)
       verbose= (False) if True, print the FERRE output
    OUTPUT:
       (none)
    HISTORY:
       2015-01-22 - Written - Bovy (IAS)
    """
    # Set up the subprocess to run FERRE
    if verbose:
        stdout= None
        stderr= None
    else:
        stdout= subprocess.PIPE
        stderr= subprocess.PIPE
    try:
        subprocess.check_call(['ferre'],cwd=dir,stdout=stdout,stderr=stderr)
    except subprocess.CalledProcessError:
        raise Exception("Running FERRE instance in directory %s failed ..." % dir)
    return None

def write_input_nml(dir,
                    pfile,
                    offile,
                    ndim=6,
                    nov=0,
                    synthfile=None,
                    inter=3,
                    f_format=1,
                    f_access=1):
    """
    NAME:
       write_input_nml
    PURPOSE:
       write a FERRE input.nml file
    INPUT:
       dir - directory where the input.nml file will be written to
       pfile - name of the input parameter file
       offile - name of the output best-fitting model file
       ndim= (6) number of dimensions/parameters
       nov= (0) number of parameters to search (0=interpolation)
       synthfile= (default ferreModelLibraryPath in apogee.tools.path) file name of the model grid's header
       inter= (3) order of the interpolation
       f_format= (1) file format (0=ascii, 1=unf)
       f_access= (1) 0: load whole library, 1: use direct access (for small numbers of interpolations)
    OUTPUT:
       (none; just writes the file)
    HISTORY:
       2015-01-22 - Written - Bovy (IAS)
    """
    if synthfile is None:
        import apogee.tools.path as appath
        synthfile= appath.ferreModelLibraryPath(header=True)
    with open(os.path.join(dir,'input.nml'),'w') as outfile:
        outfile.write('&LISTA\n')
        outfile.write('NDIM = %i\n' % ndim)
        outfile.write('NOV = %i\n' % nov)
        indvstr= 'INDV ='
        for ii in range(1,ndim+1):
            indvstr+= ' %i' % ii
        outfile.write(indvstr+'\n')
        outfile.write("SYNTHFILE(1) = '%s'\n" % synthfile)
        outfile.write("PFILE = '%s'\n" % pfile)
        outfile.write("OFFILE = '%s'\n" % offile)
        outfile.write('INTER = %i\n' % inter)
        outfile.write('F_FORMAT = %i\n' % f_format)
        outfile.write('F_ACCESS = %i\n' % f_access)
        outfile.write('/\n')
    return None

@paramArrayInputDecorator
def write_interpolate_ipf(dir,
                          teff,logg,metals,am,nm,cm,vm=None):
    """
    NAME:
       write_interpolate_ipf
    PURPOSE:
       write a FERRE input.ipf file for interpolation
    INPUT:
       dir - directory where the input.ipf file will be written to
       Parameters (can be 1D arrays):
          teff - Effective temperature (K)
          logg - log10 surface gravity / cm s^-2
          metals - overall metallicity
          am - [alpha/M]
          nm - [N/M]
          cm - [C/M]
          vm= if using the 7D library, also specify the microturbulence
    OUTPUT:
       (none; just writes the file)
    HISTORY:
       2015-01-23 - Written - Bovy (IAS)
    """
    with open(os.path.join(dir,'input.ipf'),'w') as outfile:
        for ii in range(len(teff)):
            outStr= 'dummy '
            if not vm is None:
                outStr+= '%.3f ' % numpy.log10(vm[ii])
            outStr+= '%.3f %.3f %.3f %.3f %.3f %.1f\n' \
                % (cm[ii],nm[ii],am[ii],
                   metals[ii],logg[ii],teff[ii])
            outfile.write(outStr)
    return None