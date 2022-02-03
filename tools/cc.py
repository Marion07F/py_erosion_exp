# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 09:17:49 2021

@author: Paul Leroy
"""

import configparser, logging, os, shutil, struct

import numpy as np

import tools.common_ple as ple
import tools.ccConfig as ccConfig
import tools.m3c2 as m3c2_tools

logger = logging.getLogger(__name__)

cc_dgm = ccConfig.cc_dgm
cc_dgm = ccConfig.cc_dgm

subMethods = {0: None, 1: 'RANDOM', 2: 'SPATIAL', 3: 'OCTREE'}

EXIT_FAILURE = 1
EXIT_SUCCESS = 0

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class CloudCompareError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self):
        pass

def format_name(in_, name_):
    # generating a cloud_file full name for the subproces call can be tricky
    # especially when the path contains whitespaces...
    # handling all these whitespaces is really tricky...
    # sigh... (read CC command line help, option -FILE)
    normpath = os.path.normpath(os.path.join(in_, name_))
    list_ = [f'"{item}"' if ' ' in item else item for item in normpath.split('\\')]
    if ':' in list_[0]:
        new_name = '/'.join(list_) # beurk
    else:
        new_name = os.path.join(*list_)
    return new_name

def cloud_exists(cloud, verbose=False):
    head, tail = os.path.split(cloud)
    if os.path.exists(cloud):
        if verbose is True: 
            logger.info(f'cloud {tail} exists')
        return True
    else:
        logger.error(f'cloud {tail} does not exist')
        raise Error(f'cloud {tail} does not exist')

def copy_cloud(cloud, out):
    # copy the cloud file to out
    # /!\ with sbf files, one shall copy .sbf and .sbf.data
    head, tail = os.path.split(cloud)
    root, ext = os.path.splitext(cloud)
    logger.info(f'copy {tail} to output directory')
    dst = shutil.copy(cloud, out)
    if ext == '.sbf':
        src = cloud + '.data'
        if os.path.exists(src):
            logger.info('copy .sbf.data to output directory')
            shutil.copy(src, out)
    return dst

def move_cloud(cloud, odir):
    # move the cloud to out
    # /!\ with sbf files, one shall copy .sbf and .sbf.data
    head, tail = os.path.split(cloud)
    root, ext = os.path.splitext(cloud)
    logger.info(f'move {tail} to output directory')
    if os.path.isdir(odir):
        out = os.path.join(odir, tail)
    else:
        out = odir
    dst = shutil.move(cloud, out)
    if ext == '.sbf':
        src = cloud + '.data'
        if os.path.exists(src):
            logger.info('move .sbf.data to output directory')
            shutil.move(src, out + '.data')
    return dst

#########
## 3DMASC
#########
def q3dmasc(pc, training_file, shift, core=None, silent=True, debug=False):
    x, y, z = shift
    args = ''
    if silent is True:
        args += ' -SILENT -NO_TIMESTAMP'
    else:
        args += ' -NO_TIMESTAMP'
    args += ' -C_EXPORT_FMT SBF'
    root, ext = os.path.splitext(pc)
    args += f' -o -GLOBAL_SHIFT {x} {y} {z} {pc}'
    if core is not  None:
            args +=f' -o -GLOBAL_SHIFT {x} {y} {z} {core}'
    if core is not None:
        args += f' -3DMASC_CLASSIFY -ONLY_FEATURES {training_file} "PC1=1 PCX=2"'
    else:
        args += f' -3DMASC_CLASSIFY -ONLY_FEATURES {training_file} "PC1=1"'
    print(f'cc {args}')
    ple.exe(cc_dgm + args, debug=debug)
    return root + '_WITH_FEATURES.sbf'

def density(pc, shift, radius, densityType, silent=True, debug=False):
    x, y, z = shift
    args = ''
    if silent is True:
        args += ' -SILENT'
    args += ' -NO_TIMESTAMP'
    args += ' -C_EXPORT_FMT SBF -SAVE_CLOUDS'
    root, ext = os.path.splitext(pc)
    args += f' -o -GLOBAL_SHIFT {x} {y} {z} {pc} -REMOVE_ALL_SFS'
    # densityType can be KNN SURFACE VOLUME
    args += f' -DENSITY {radius} -TYPE {densityType}'
    print(f'cc {args}')
    ple.exe(cc_dgm + args, debug=debug)
    return root + '_DENSITY.sbf'

################
# Best Fit Plane
################

def best_fit_plane(cloud, debug=False):
    
    cloud_exists(cloud)
    
    args = ''
    args += ' -SILENT -NO_TIMESTAMP'
    args += ' -o ' + cloud
    args += ' -BEST_FIT_PLANE '
    
    ple.exe(cc_dgm + args, debug=debug)
    
    outputs = (os.path.splitext(cloud)[0] + '_BEST_FIT_PLANE.bin',
               os.path.splitext(cloud)[0] + '_BEST_FIT_PLANE_INFO.txt')
    
    return outputs

def get_orientation_matrix(filename):
    with open(filename) as f:
        matrix = np.genfromtxt(f, delimiter=' ', skip_header=5)
    return matrix

#######
## M3C2
#######

def m3c2(pc1, pc2, params, core=None, silent=True, fmt='ASC', debug=False):
    cloud_exists(pc1, verbose=False)
    cloud_exists(pc2, verbose=False)
    args = ''
    if silent is True:
        args += ' -SILENT -NO_TIMESTAMP'
    else:
        args += ' -NO_TIMESTAMP'
    args += f' -C_EXPORT_FMT {fmt}'
    args += ' -o -GLOBAL_SHIFT FIRST ' + pc1
    args += ' -o -GLOBAL_SHIFT FIRST ' + pc2
    if core is not None:
        args += ' -o -GLOBAL_SHIFT FIRST ' + core
    args += ' -M3C2 ' + params
    cmd = cc_dgm + args
    if debug is True:
        logging.info(cmd)
    ret = ple.exe(cmd, debug=debug)
    if ret == EXIT_FAILURE:
        raise CloudCompareError
    # extracting rootname of the fixed point cloud Q
    if fmt == 'SBF':
        ext ='sbf'
    elif fmt == 'BIN':
        ext = 'bin'
    elif fmt == 'ASC':
        ext ='asc'
    head1, tail1 = os.path.split(pc1)
    root1, ext1 = os.path.splitext(tail1)
    results = os.path.join(head1, root1 + f'_M3C2.{ext}')
    return results

def drop_global_shift(cloud, silent=True):
    args = ''
    if silent is True:
        args +=' -SILENT -NO_TIMESTAMP'
    else:
        args +=' -NO_TIMESTAMP'
    args +=' -o ' + cloud
    args +=' -DROP_GLOBAL_SHIFT -SAVE_CLOUDS'
    ret = ple.exe(cc_dgm + args)
    if ret == EXIT_FAILURE:
        raise CloudCompareError
    return ret

def remove_scalar_fields(cloud, silent=True):
    args = ''
    if silent is True:
        args +=' -SILENT -NO_TIMESTAMP'
    else:
        args +=' -NO_TIMESTAMP'
    args +=' -o ' + cloud
    args +=' -REMOVE_ALL_SFS -SAVE_CLOUDS'
    ple.exe(cc_dgm + args)

def rasterize(cloud, spacing, ext='_RASTER', debug=False, proj='AVG'):
    cloud_exists(cloud)
    
    args = ''
    args += ' -SILENT -NO_TIMESTAMP'
    args += ' -o ' + cloud
    args += ' -RASTERIZE -GRID_STEP ' + str(spacing)
    args += ' -PROJ ' + proj
    ple.exe(cc_dgm + args, debug=debug)
    
    return os.path.splitext(cloud)[0] + ext + '.bin'
    
def build_core(conf):
    #-1- build raster from cloud 1
    raster = rasterize(conf.Q, conf.coreSpacing)
    
    #####################
    # NORMALS SUBSAMPLING
    if conf.normalsSubMethod != 0:
        # 2.1) M3C2
        results = m3c2(conf.Q, conf.P, conf.m3c2_core, core=raster, fmt='SBF')
        configRes = read_sbf_header(results)
        coreOnQ, normQ, nQ, stdQ = m3c2_tools.load_pc_n1_std1_norm(results)
        logger.warning(f'number of core points before normals subsampling {nQ.size}')
        # save normals
        sbfNormQ = os.path.join(conf.out, 'sbfNormQ.sbf')
        write_sbf(sbfNormQ, normQ.T, addIndex=True)
        # subsampling
        algorithm = subMethods[conf.normalsSubMethod]
        parameter = conf.normalsSubParameter
        if algorithm == 'RANDOM' or algorithm == 'SPATIAL':
            parameter = 2 * np.sin(parameter / 2 * np.pi / 180)
        logger.warning(f'subampling parameter {parameter:.6f}')
        sbfSubSampled = ss(sbfNormQ, algorithm=algorithm, parameter=parameter)
        # read subsamples
        array, shift, config = read_sbf(sbfSubSampled)
        index = array[:, 3].astype(int)
        logger.warning(f'number of core points after normals subsampling {index.size}')
        # we need to relaunch M3C2 with the reduced set of core points
        coreWithoutNormals = os.path.join(conf.out, 'core_SUBSAMPLED.sbf')
        globalShift = eval(configRes['SBF']['GlobalShift'])
        coreOnQ -= np.array(globalShift).reshape(-1, 1)
        write_sbf(coreWithoutNormals, coreOnQ[:, index].T, GlobalShift=globalShift)
        # 2.2) M3C2
        core = m3c2(conf.Q, conf.P, conf.m3c2_core, core=coreWithoutNormals, fmt='BIN')
        logger.info(f'normals subsampling applied, core rebuilt: {os.path.split(core)[-1]}')
    else:
        # 2) compute M3C2 values, projection depends on the parameters file
        core = m3c2(conf.Q, conf.P, conf.m3c2_core, core=raster, fmt='BIN')
        
    # 3) remove scalar fields
    remove_scalar_fields(core)
    
    # 4) copy core points to destination
    src = core
    root, ext = os.path.splitext(core)
    dst = root + '_core.bin'
    
    if os.path.exists(dst):
        os.remove(dst)
    os.rename(src, dst)
    
    return dst

#################
## TO BIN, TO SBF
#################

def to_sbf(fullname, debug=False):
    root, ext = os.path.splitext(fullname)
    if ext == '.sbf':
        # nothing to do, simply return the name
        return fullname
    if os.path.exists(fullname):
        args = ''
        args += ' -SILENT -NO_TIMESTAMP'
        args += ' -C_EXPORT_FMT SBF'
        args += ' -o ' + fullname
        args += ' -SAVE_CLOUDS'
        ple.exe(cc_dgm + args, debug=debug)
        return os.path.splitext(fullname)[0] + '.sbf'
    else:
        print(f'error, {fullname} does not exist')
        return -1

def to_bin(fullname, debug=False, shift=None, cc=cc_dgm):
    root, ext = os.path.splitext(fullname)
    if os.path.exists(fullname):
        args = ''
        if debug==False:
            args += ' -SILENT -NO_TIMESTAMP'
        else:
            args += ' -NO_TIMESTAMP'
        args += ' -C_EXPORT_FMT BIN'
        if shift is not None:
            x, y, z = shift
            args += f' -o -GLOBAL_SHIFT {x} {y} {z} ' + fullname
        else:
            args += ' -o ' + fullname
        args += ' -SAVE_CLOUDS'
        print(f'cc {args}')
        ret = ple.exe(cc + args, debug=debug)
        return ret
    else:
        print(f'error, {fullname} does not exist')
        return -1
    
def all_to_bin(dir_, shift, debug=False):
    list_ = os.listdir(dir_)
    for name in list_:
        path = os.path.join(dir_, name)
        if os.path.isfile(path):
            if os.path.splitext(path)[-1] == '.laz':
                to_bin(path, debug=debug, shift=shift)

##############
## SUBSAMPLING
##############

def ss(fullname, cc=cc_dgm, algorithm='OCTREE', parameter=8, debug=False, odir=None, fmt='SBF'):
    root, ext = os.path.splitext(fullname)
    
    if fmt == 'SBF':
        ext = 'sbf'
    elif fmt == 'BIN':
        ext = 'bin'

    if algorithm == 'OCTREE':
        out = root + f'_OCTREE_LEVEL_{parameter}_SUBSAMPLED.{ext}'
    elif algorithm == 'SPATIAL':
        out = root + f'_SPATIAL_SUBSAMPLED.{ext}'
    elif algorithm == 'RANDOM':
        out = root + f'_RANDOM_SUBSAMPLED.{ext}'

    if os.path.exists(fullname):
        args = ''
        if debug==False:
            args += ' -SILENT -NO_TIMESTAMP'
        else:
            args += ' -NO_TIMESTAMP'
        # algorithm RANDOM SPATIAL OCTREE 
        # parameter number of points / distance between points / subdivision level
        args += ' -o ' + fullname
        args += f' -C_EXPORT_FMT {fmt} -SS {algorithm} {parameter}'
        ret = ple.exe(cc + args, debug=debug)
        if odir is not None:
            head, tail = os.path.split(out)
            dst = os.path.join(odir, tail)
            shutil.move(out, dst)
            if fmt == 'SBF':
                dstData = os.path.join(odir, tail + '.data')
                shutil.move(out + '.data', dstData)
            out = dst
        return out
    else:
        print(f'error, {fullname} does not exist')
        return -1

#######################
## CLOUD TRANSFORMATION
#######################

def get_inverse_transformation(transformation):
    R = transformation[:3, :3]
    T = transformation[:3:, 3]
    inv = np.zeros((4, 4))
    inv[3, 3] = 1
    inv[:3, :3] = R.T
    inv[:3:, 3] = -R.T @ T
    return inv

def save_trans(transfile, R, T):
    transformation = np.zeros((4, 4))
    transformation[:3, :3] = R
    transformation[:3, 3, None] = T
    transformation[3, 3] = 1
    np.savetxt(transfile, transformation, fmt='%.8f')
    logger.debug(f'{transfile} saved')

def apply_trans_alt(cloudfile, transfile):
    args = ''
    args += ' -SILENT -NO_TIMESTAMP'
    args += ' -o ' + cloudfile
    args += ' -APPLY_TRANS ' + transfile
    ret = ple.exe(cc_dgm + args)
    if ret == EXIT_FAILURE:
        raise CloudCompareError
    root, ext = os.path.splitext(cloudfile)
    return root + '_TRANSFORMED.bin'

def apply_trans(cloudfile, transfile, outfile=None, silent=True, debug=False, shift=(0, 0, 0)):
    root, ext = os.path.splitext(cloudfile)
    level = logger.getEffectiveLevel()
    if debug is True:
        logger.setLevel(logging.DEBUG)
    # Transform a point cloud using CloudCompare
    logger.debug(f'IN___ {os.path.split(cloudfile)[-1]}')
    logger.debug(f'TRANS {os.path.split(transfile)[-1]}')
    if outfile is None:
        head, tail = os.path.split(cloudfile)[0]
        name = os.path.splitext(tail)[0] + '_rotated.bin'
        outfile = os.path.join(head,  name)
    else:
        name = os.path.split(outfile)[-1]
    logger.debug(f'OUT__ {name}')
    args = ''
    if silent is True:
        args += ' -SILENT'
    args += ' -NO_TIMESTAMP'
    if ext == '.bin':
        args += ' -C_EXPORT_FMT BIN -AUTO_SAVE OFF'
        args += ' -o ' + cloudfile
    elif ext == '.sbf':
        x, y, z = shift
        args += ' -C_EXPORT_FMT SBF -AUTO_SAVE OFF'
        args += f' -o -GLOBAL_SHIFT {x} {y} {z} ' + cloudfile
    args += ' -APPLY_TRANS ' + transfile
    args += ' -SAVE_CLOUDS FILE ' + outfile
    if debug is True:
        print(f'cc {args}')
    ret = ple.exe(cc_dgm + args)
    if ret == EXIT_FAILURE:
        raise CloudCompareError
    logger.setLevel(level)
    
def transform_cloud(cloud, R, T, shift=None, silent=True, debug=False):
    cloud_exists(cloud)
    head, tail = os.path.split(cloud)
    cloud_trans = cloud # the transformation will overwrite the cloud
    transformation = os.path.join(head, 'transformation.txt')
    # Create the matrix file to be used by CloudCompare to transform the cloud
    save_trans(transformation, R, T)
    # Transform the cloud
    logger.info(f'[CC] transformation of {tail}')
    apply_trans(cloud, transformation, cloud_trans, silent=silent, debug=debug, shift=shift)

###################
## BIN READ / WRITE
###################

def get_from_bin(bin_):
    with open(bin_, 'rb') as f:
        bytes_ = f.read(4)
        # 'I' unsigned int / integer / 4
        for k in range(3):
            print(chr(bytes_[k]))

#################
## SBF READ/WRITE
#################

def shift_array(array, shift, config=None, debug=False):
    newArray = array.astype(float)
    # apply the shift read in the SBF file
    newArray += np.array(shift).reshape(1, -1)
    # apply GlobalShift if any
    if config is not None:
        try:
            globalShift = eval(config['SBF']['GlobalShift'])
            logger.debug(f'use GlobalShift {globalShift}')
            newArray += np.array(globalShift).reshape(1, -1)
        except:
            pass
    return newArray

def read_sbf_header(sbf, verbose=False):
    config = configparser.ConfigParser() 
    config.optionxform = str
    with open(sbf) as f:
        config.read_file(f)
        if 'SBF' not in config:
            print('sbf badly formatted, no [SBF] section')
        else:
            return config

def read_sbf(sbf, verbose=False):
    
    ###########
    # READ .sbf
    config = read_sbf_header(sbf, verbose=verbose)
    
    ################
    # READ .sbf.data
    # carefull, sys.byteorder is probably 'little' (different from Cloud Compare)
    sbf_data = sbf + '.data'
    with open(sbf_data, 'rb') as f:
        bytes_ = f.read(64)
        # 0-1 SBF header flag
        flag = bytes_[0:2]
        # 2-9 Point count (Np)
        Np = struct.unpack('>Q', bytes_[2:10])[0]
        # 10-11 ScalarField count (Ns)
        Ns = struct.unpack('>H', bytes_[10:12])[0]
        if verbose is True:
            print(f'flag {flag}, Np {Np}, Ns {Ns}')
        # 12-19 X coordinate shift
        xShift = struct.unpack('>d', bytes_[12:20])[0]
        # 20-27 Y coordinate shift
        yShift = struct.unpack('>d', bytes_[20:28])[0]
        # 28-35 Z coordinate shift
        zShift = struct.unpack('>d', bytes_[28:36])[0]
        # 36-63 Reserved for later
        if verbose is True:
            print(f'shift ({xShift, yShift, zShift})')
            print(bytes_[37:])
            print(len(bytes_[37:]))
        array = np.fromfile(f, dtype='>f').reshape(Np, Ns+3)
        shift = np.array((xShift, yShift, zShift)).reshape(1, 3)
        
    # shift point cloud
    pc = shift_array(array[:, :3], shift, config)
    
    # get scalar fields if any
    if Ns != 0:
        sf = array[:, 3:]
    else:
        sf = None
        
    return pc, sf, config

def write_sbf(sbf, pc, sf, config=None, addIndex=False, normals=None):
    head, tail = os.path.split(sbf)
    path_to_sbf = sbf
    path_to_sbf_data = sbf + '.data'
    if sf is not None:
        SFCount = sf.shape[1]
    else:
        SFCount = 0
    
    # write .sbf
    Points = pc.shape[0] 
    if config is None:
        dict_SF = {f'SF{k+1}':f'{k+1}' for k in range(SFCount)}
        config = configparser.ConfigParser()
        config.optionxform = str
        config['SBF'] = {'Points': str(Points),
                         'SFCount': str(SFCount),
                         'GlobalShift': '0., 0., 0.',
                         **dict_SF}
    else:
        # enforce the coherence of the number of points
        config['SBF']['Points'] = str(Points)
        config['SBF']['SFCount'] = str(SFCount)

    if addIndex is True:
        if 'SFCount' in config['SBF']:
            SFCount += 1
        else:
            SFCount = 1
        config['SBF']['SFcount'] = str(SFCount)
        config['SBF'][f'SF{SFCount}'] = 'index'
    if normals is not None:
        if 'SFCount' in config['SBF']:
            SFCount += 3
        else:
            SFCount = 3
        config['SBF']['SFcount'] = str(SFCount)
        config['SBF'][f'SF{SFCount+1}'] = 'Nx'
        config['SBF'][f'SF{SFCount+2}'] = 'Ny'
        config['SBF'][f'SF{SFCount+3}'] = 'Nz'
    
    # write .sbf configuration file
    with open(path_to_sbf, 'w') as sbf:
        config.write(sbf)
    
    # remove GlobalShift
    globalShift = eval(config['SBF']['GlobalShift'])
    pcOrig = pc - np.array(globalShift).reshape(1, -1)
    # compute sbf internal shift
    shift = np.mean(pcOrig, axis=0).astype(float)
    # build the array that will effectively be stored (32 bits float)
    a = np.zeros((Points, SFCount + 3)).astype('>f')
    a[:, :3] = (pcOrig - shift).astype('>f')
    if SFCount != 0:
        a[:, 3:] = sf.astype('>f')

    if addIndex is True:
        b = np.zeros((Points, SFCount + 1)).astype('>f')
        b[:, :-1] = a
        b[:, -1] = np.arange(Points).astype('>f')
        a = b
    
    # write .sbf.data
    with open(path_to_sbf_data, 'wb') as sbf_data:
        # 0-1 SBF header flag
        flag = bytearray([42, 42])
        sbf_data.write(flag)
        # 2-9 Point count (Np)
        sbf_data.write(struct.pack('>Q', Points))
        # 10-11 ScalarField count (Ns)
        sbf_data.write(struct.pack('>H', SFCount))
        # 12-19 X coordinate shift
        sbf_data.write(struct.pack('>d', shift[0]))
        # 20-27 Y coordinate shift
        sbf_data.write(struct.pack('>d', shift[1]))
        # 28-35 Z coordinate shift
        sbf_data.write(struct.pack('>d', shift[2]))
        # 36-63 Reserved for later
        sbf_data.write(bytes(63-36+1))
        sbf_data.write(a)
        
###########
## C2C_DIST
###########

def c2c_dist(compared, reference, maxDist, odir=None, silent=True, debug=False):
    # cloud to cloud distance + filtering using the distance maxDist
    args = ''
    if silent is True:
        args += ' -SILENT -NO_TIMESTAMP'
    else:
        args += ' -NO_TIMESTAMP'
    args += ' -C_EXPORT_FMT SBF'
    args += f' -o {compared}'
    args += f' -o {reference}'
    args += ' -c2c_dist'
    args += f' -FILTER_SF 0. {maxDist:.3f}'

    ple.exe(cc_dgm + args, debug=debug)

    root, ext = os.path.splitext(compared)
    output = root + '_C2C_DIST.sbf'
    head, tail =  os.path.split(output)
    if os.path.exists(odir):
        overlap = os.path.join(odir, tail)
        shutil.move(output, overlap)
        shutil.move(output + '.data', overlap + '.data')
        output = overlap
    
    return output

def closest_point_set(compared, reference, silent=True, debug = False):
    compRoot, compExt = os.path.splitext(compared)
    compHead, compTail = os.path.split(compared)
    refRoot, refExt = os.path.splitext(reference)
    args = ''
    if silent is True:
        args += ' -SILENT -NO_TIMESTAMP'
    else:
        args += ' -NO_TIMESTAMP'
    args += ' -C_EXPORT_FMT SBF'
    if compExt == '.sbf':
        args += f' -o -GLOBAL_SHIFT FIRST {compared}'
    else:
        args += f' -o {compared}'
    if refExt == '.sbf':
        args += f' -o -GLOBAL_SHIFT FIRST {reference}'
    else:
        args += f' -o {reference}'
    args += ' -CLOSEST_POINT_SET'

    compBase = os.path.splitext(os.path.split(compared)[1])[0]
    refBase = os.path.splitext(os.path.split(reference)[1])[0]

    ple.exe(cc_dgm + args, debug=debug)
    
    return os.path.join(compHead, f'[{refBase}]_CPSet({compBase}).sbf')

######
## ICP
######

def icp(compared, reference,
        overlap=None,
        random_sampling_limit=None, 
        farthest_removal=False,
        iter_=None,
        silent=True, debug=False):
    compRoot, compExt = os.path.splitext(compared)
    refRoot, refExt = os.path.splitext(reference)
    args = ''
    if silent is True:
        args += ' -SILENT -NO_TIMESTAMP'
    else:
        args += ' -NO_TIMESTAMP'
    args += ' -C_EXPORT_FMT SBF'
    if compExt == '.sbf':
        args += f' -o -GLOBAL_SHIFT FIRST {compared}'
    else:
        args += f' -o {compared}'
    if refExt == '.sbf':
        args += f' -o -GLOBAL_SHIFT FIRST {reference}'
    else:
        args += f' -o {reference}'
    args += ' -ICP'
    if overlap is not None:
        args += f' -OVERLAP {overlap}'
    if random_sampling_limit is not None:
        args += f' -RANDOM_SAMPLING_LIMIT {random_sampling_limit}'
    if farthest_removal is True:
        args += ' -FARTHEST_REMOVAL'
    if iter_ is not None:
        args += f' -ITER {iter_}'

    print(f'cc {args}')
    ple.exe(cc_dgm + args, debug=debug)
    
    out = os.path.join(os.getcwd(), 'registration_trace_log.csv')
    return out

if __name__ == '__main__':
    laz10b = 'C:/DATA/ZoneB/nz10b.laz'
    laz14b = 'C:/DATA/ZoneB/nz14b.laz'
    bin_ = 'C:/DATA/ZoneB/test_bin/nz10b_0000002_M3C2_core.bin'
    
    ss1 = 'C:/DATA/test_cloud_subsampling/nz10b_0000002_RANDOM_SUBSAMPLED_1.bin'
    ss2 = 'C:/DATA/test_cloud_subsampling/nz10b_0000002_RANDOM_SUBSAMPLED_2.bin'

    #to_bin(fullname, debug=True, shift=nz14_nztm)
    #to_bin('E:/PaulLeroy/ZoneA/nz14/nz14.laz', shift=nz14_utm59south, debug=True)
    
    
    