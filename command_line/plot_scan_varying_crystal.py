#!/usr/bin/env python
#
# plot_scan_varying_crystal.py
#
#  Copyright (C) (2014) STFC Rutherford Appleton Laboratory, UK.
#
#  Author: David G. Waterman
#
#  This code is distributed under the BSD license, a copy of which is
#  included in the root directory of this package.

from __future__ import division

import matplotlib
matplotlib.use('Agg')

class Script(object):
  '''Class to run script.'''

  def __init__(self):
    '''Setup the script.'''
    from dials.util.options import OptionParser

    self.parser = OptionParser(
      read_experiments=True,
      check_format=False)

  def run(self):
    '''Run the script.'''
    from dials.util.options import flatten_experiments

    params, options = self.parser.parse_args()
    if len(params.input.experiments) == 0:
      self.parser.print_help()
    experiments = flatten_experiments(params.input.experiments)
    crystals = experiments.crystals()

    for icrystal, crystal in enumerate(crystals):

      if crystal.num_scan_points == 0:
        print "Ignoring scan-static crystal"
        continue

      scan_pts = range(crystal.num_scan_points)
      cells = [crystal.get_unit_cell_at_scan_point(t) \
               for t in scan_pts]
      dat = [(t,) + e.parameters() + (e.volume(),) \
             for (t, e) in zip(scan_pts, cells)]
      seq = icrystal if len(crystals) > 1 else None
      self.plot(dat, seq=seq)

      print "Image\ta\tb\tc\talpha\tbeta\tgamma\tVolume"
      msg = "\t".join(["%.3f"] * 8)
      for line in dat:
        print msg % line

    print "TODO: misset angles around user-supplied axes"

  def plot(self, dat, seq):
    try:
      import matplotlib.pyplot as plt
      import matplotlib.gridspec as gridspec
    except ImportError as e:
      print "matplotlib modules not available", e
      return None

    from math import floor, ceil
    image, a, b, c, alpha, beta, gamma, volume = zip(*dat)
    fig = plt.figure(figsize=(13, 10))
    gs = gridspec.GridSpec(4, 2, wspace=0.4, hspace=0.6)

    ax = plt.subplot(gs[0, 0])
    ax.ticklabel_format(useOffset=False)
    plt.plot(image, a)
    plt.xlabel('Image')
    plt.ylabel(r'length $\left(\AA\right)$')
    plt.title('a')

    ax = plt.subplot(gs[0, 1])
    ax.ticklabel_format(useOffset=False)
    plt.plot(image, alpha)
    plt.axis(ymin=floor(min(alpha)), ymax=ceil(max(alpha)))
    plt.xlabel('Image')
    plt.ylabel(r'angle $\left(^\circ\right)$')
    plt.title(r'$\alpha$')

    ax = plt.subplot(gs[1, 0])
    ax.ticklabel_format(useOffset=False)
    plt.plot(image, b)
    plt.xlabel('Image')
    plt.ylabel(r'length $\left(\AA\right)$')
    plt.title('b')

    ax = plt.subplot(gs[1, 1])
    ax.ticklabel_format(useOffset=False)
    plt.plot(image, beta)
    plt.axis(ymin=floor(min(beta)), ymax=ceil(max(beta)))
    plt.xlabel('Image')
    plt.ylabel(r'angle $\left(^\circ\right)$')
    plt.title(r'$\beta$')

    ax = plt.subplot(gs[2, 0])
    ax.ticklabel_format(useOffset=False)
    plt.plot(image, c)
    plt.xlabel('Image')
    plt.ylabel(r'length $\left(\AA\right)$')
    plt.title('c')

    ax = plt.subplot(gs[2, 1])
    ax.ticklabel_format(useOffset=False)
    plt.plot(image, gamma)
    plt.axis(ymin=floor(min(gamma)), ymax=ceil(max(gamma)))
    plt.xlabel('Image')
    plt.ylabel(r'angle $\left(^\circ\right)$')
    plt.title(r'$\gamma$')

    ax = plt.subplot2grid((4,2), (3, 0), colspan=2)
    ax.ticklabel_format(useOffset=False)
    plt.plot(image, volume)
    plt.xlabel('Image')
    plt.ylabel(r'volume $\left(\AA^3\right)$')
    plt.title('Cell volume')

    basename = "sv_crystal"
    if seq is not None: basename += "_{0}".format(seq)
    plt.savefig(basename + ".pdf")

if __name__ == '__main__':
  from dials.util import halraiser
  try:
    script = Script()
    script.run()
  except Exception as e:
    halraiser(e)
