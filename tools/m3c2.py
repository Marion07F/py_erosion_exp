# -*- coding: utf-8 -*-
"""
Created on Tue Jan  5 16:09:33 2021

@author: Dimitri Lague, Paul Leroy
"""

import logging, os

import numpy as np

import tools.cc as cc

logger = logging.getLogger(__name__)

def compute_metrics(dist, uncer, percentile):
    n =  dist.size
    # filter out valid data among distances and uncertainties
    dist_isvalid = (np.isnan(dist) == False)
    uncer_isvalid = (np.isnan(uncer) == False)
    # compute the uncertainty level based on the percentile parameter
    uL = np.percentile(uncer[uncer_isvalid], percentile)
    print(f'percentile {percentile} => ul < {uL:.3f}')
    ind = dist_isvalid & uncer_isvalid & (uncer < uL)
    dist = dist[ind]
    uncer = uncer[ind]
    nValid = dist.size
    mean_dist = np.mean(dist)
    std_dist = np.std(dist)
    return mean_dist, std_dist, n, nValid, ind

def load_res(filename):
    root, ext = os.path.splitext(filename)
    head, tail = os.path.split(filename)
    logger.info(f'load {tail}')
    if ext == '.sbf':
        pc, sf, config = cc.read_sbf(filename)
        pc = pc.T
    else:
        array = np.loadtxt(filename)
        pc = array[:, 0:3].T
    n1 = sf[:, 0].T
    n2 = sf[:, 1].T
    std1 = sf[:, 2].T
    std2 = sf[:, 3].T
    change = sf[:, 4].T
    uncer = sf[:, 5].T
    dist = sf[:, 6].T
    norm = sf[:, 7:10].T
    
    return pc, n1, n2, std1, std2, change, uncer, dist, norm

def load_pc_change_uncer_dist_norm(filename):
    pc, n1, n2, std1, std2, change, uncer, dist, norm = load_res(filename)
    return pc, change, uncer, dist, norm

def load_pc_n1_std1_norm(filename):
    pc, n1, n2, std1, std2, change, uncer, dist, norm = load_res(filename)
    return pc, n1, std1, norm

def load_uncer_dist(filename):
    pc, n1, n2, std1, std2, change, uncer, dist, norm = load_res(filename)
    return uncer, dist

def call_init(conf, silent=True, debug=False):

    head, tail  = os.path.split(conf.P)
    P = os.path.join(conf.out, tail)

    ###########################################################
    # COMPUTE M3C2 DISTANCES AND PROJECT CORE POINTS ON CLOUD 1
    logger.info('[M3C2] calculations + projection of core points on Q')
    # launch M3C2
    results = \
        cc.m3c2(conf.Q, P, conf.m3c2_1, core=conf.core, fmt='SBF', silent=silent, debug=debug)
    # load M3C2 results
    coreOnQ, nQ, stdQ, normQ = load_pc_n1_std1_norm(results)

    ###########################################################
    # COMPUTE M3C2 DISTANCES AND PROJECT CORE POINTS ON CLOUD 2
    logger.info('[M3C2] calculations + projection of core points on P')
    # launch M3C2
    results = \
        cc.m3c2(conf.Q, P, conf.m3c2_2, core=conf.core, fmt='SBF', silent=silent, debug=debug)
    # load M3C2 results
    coreOnP, change, uncer, dist, normP = load_pc_change_uncer_dist_norm(results)

    return coreOnQ, normQ, nQ, stdQ, coreOnP, change, uncer, dist, normP

def call(conf, silent=True, debug=False):
    
    head, tail  = os.path.split(conf.P)
    P = os.path.join(conf.out, tail)

    ###########################################################
    # COMPUTE M3C2 DISTANCES AND PROJECT CORE POINTS ON CLOUD 2
    logger.info('[M3C2] calculations + projection of core points on P')
    # launch M3C2
    results = \
        cc.m3c2(conf.Q, P, conf.m3c2_2, core=conf.core, fmt='SBF', silent=silent, debug=debug)
    # load M3C2 results
    coreOnP, change, uncer, dist, normP = load_pc_change_uncer_dist_norm(results)

    return coreOnP, change, uncer, dist, normP
