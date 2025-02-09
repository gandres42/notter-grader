OK_FORMAT = True

test = {   'name': 'optimization_dist_func',
    'points': 0,
    'suites': [   {   'cases': [   {'code': '>>> assert np.isclose(dist, 0.0, atol=0.01)\n', 'hidden': False, 'locked': False},
                                   {'code': '>>> assert dist_far_away > 0.0\n', 'hidden': False, 'locked': False}],
                      'scored': True,
                      'setup': '',
                      'teardown': '',
                      'type': 'doctest'}]}
