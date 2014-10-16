from __future__ import division

class Test(object):

  def __init__(self):

    from dials.algorithms.integration.profile import XdsCircleSampler

    width = 1000
    height = 1000
    depth = 10
    nz = 1
    self.sampler = XdsCircleSampler((width, height, depth), nz)

    self.grid_size = (9, 9, 9)
    self.threshold = 0.02

  def run(self):

    self.tst_with_identical_non_negative_profiles()
    self.tst_with_systematically_offset_profiles()
    self.tst_with_single_profile()

  def tst_with_identical_non_negative_profiles(self):

    from dials.algorithms.integration.profile import XdsCircleReferenceLearner
    from scitbx.array_family import flex

    # Generate identical non-negative profiles
    reflections, profiles, profile = self.generate_identical_non_negative_profiles()

    # Create the reference learner
    learner = XdsCircleReferenceLearner(self.sampler,
        self.grid_size, self.threshold)

    # Learn from the reflections
    for i in range(len(reflections)):
      learner.add(profiles[i], reflections[i]['xyzcal.px'])
    learner.finalize()

    # Get the reference locator
    locate = learner.locate()

    # Normalize the profile
    profile = self.normalize_profile(profile)

    # Check that all the reference profiles are the same
    eps = 1e-10
    for index in range(locate.size()):
      reference = locate.profile(index)
      for k in range(self.grid_size[2]):
        for j in range(self.grid_size[1]):
          for i in range(self.grid_size[0]):
            assert(abs(reference[k,j,i] - profile[k,j,i]) <= eps)
      assert(abs(flex.sum(reference) - 1.0) <= eps)

    print 'OK'

  def tst_with_systematically_offset_profiles(self):
    from dials.algorithms.integration.profile import XdsCircleReferenceLearner
    from dials.algorithms.image.centroid import centroid_image
    from scitbx import matrix
    from scitbx.array_family import flex

    # Generate identical non-negative profiles
    reflections, profiles = self.generate_systematically_offset_profiles()

    # Create the reference learner
    learner = XdsCircleReferenceLearner(self.sampler,
        self.grid_size, self.threshold)

    # Learn from the reflections
    for i in range(len(reflections)):
      learner.add(profiles[i], reflections[i]['xyzcal.px'])
    learner.finalize()

    # Get the reference locator
    locate = learner.locate()

    # Check that all the reference profiles are the same
    eps = 1e-3
    x1 = []
    x2 = []
    for index in range(locate.size()):
      reference = locate.profile(index)
      coord = locate.coord(index)
      centroid = centroid_image(reference)
      x1.append(coord[0])
      x2.append(centroid.mean()[0])

      assert(abs(flex.sum(reference) - 1.0) < 1e-7)

    Y = matrix.col((
        sum(x2),
        sum([x * y for x, y in zip(x1, x2)])))
    X = matrix.sqr((
        len(x1),
        sum(x1),
        sum(x1),
        sum([x * x for x in x1])))

    b = X.inverse() * Y

    print 'OK'

  def tst_with_single_profile(self):

    from dials.algorithms.integration.profile import XdsCircleReferenceLearner
    from scitbx.array_family import flex

    # Generate identical non-negative profiles
    reflections, profiles, profile = self.generate_single_central_non_negative_profiles()

    # Create the reference learner
    learner = XdsCircleReferenceLearner(self.sampler,
        self.grid_size, self.threshold)

    # Learn from the reflections
    for i in range(len(reflections)):
      learner.add(profiles[i], reflections[i]['xyzcal.px'])
    learner.finalize()

    # Get the reference locator
    locate = learner.locate()

    # Normalize the profile
    profile = self.normalize_profile(profile)
    zero = flex.double(profile.accessor(), 0)

    assert(len(reflections) == 1)
    coord = reflections[0]['xyzcal.px']
    ind = locate.indices(coord)

    nind = set(range(locate.size())).difference(ind)
    assert(len(nind) == 0)

    for i in ind:
      assert(locate.profile(i).as_1d().all_approx_equal(profile.as_1d()))

    print 'OK'


  def normalize_profile(self, profile):
    from scitbx.array_family import flex
    max_profile = flex.max(profile)
    threshold = self.threshold * max_profile
    sum_profile = 0.0
    for i in range(len(profile)):
      if profile[i] > threshold:
        sum_profile += profile[i]
      else:
        profile[i] = 0.0

    result = flex.double(flex.grid(profile.all()))
    for i in range(len(profile)):
      result[i] = profile[i] / sum_profile

    return result


  def generate_single_central_non_negative_profiles(self):
    from dials.array_family import flex
    from tst_profile_helpers import gaussian
    rlist = flex.reflection_table(1)

    profile = gaussian(self.grid_size, 1000, (4, 4, 4), (1.5, 1.5, 1.5))

    x = 500
    y = 500
    z = 5
    xyz = flex.vec3_double(1)
    xyz[0] = (x, y, z)
    profiles = [ profile.deep_copy() ]
    rlist['xyzcal.px'] = xyz

    return rlist, profiles, profile


  def generate_identical_non_negative_profiles(self):
    from dials.array_family import flex
    from random import uniform
    from tst_profile_helpers import gaussian
    rlist = flex.reflection_table(1000)

    profile = gaussian(self.grid_size, 1000, (4, 4, 4), (1.5, 1.5, 1.5))

    xyz = flex.vec3_double(1000)
    profiles = []
    for i in range(1000):
      x = uniform(0, 1000)
      y = uniform(0, 1000)
      z = uniform(0, 10)
      xyz[i] = (x, y, z)
      profiles.append(profile.deep_copy())
    rlist['xyzcal.px'] = xyz

    return rlist, profiles, profile

  def generate_systematically_offset_profiles(self):
    from dials.array_family import flex
    from random import uniform
    from tst_profile_helpers import gaussian
    rlist = flex.reflection_table(1000)

    xyz = flex.vec3_double(1000)
    profiles = []
    for i in range(1000):
      x = uniform(0, 1000)
      y = uniform(0, 1000)
      z = uniform(0, 10)

      offset = -4.5  + 9 * x / 1000.0

      profile = gaussian(self.grid_size, 1000,
          (4 + offset, 4, 4), (1.5, 1.5, 1.5))
      xyz[i] = (x, y, z)
      profiles.append(profile)

    rlist['xyzcal.px'] = xyz
    return rlist, profiles

if __name__ == '__main__':
  from dials.test import cd_auto
  with cd_auto(__file__):
    test = Test()
    test.run()
