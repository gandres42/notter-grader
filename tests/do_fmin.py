OK_FORMAT = True

test = {   'name': 'do_fmin',
    'points': 0,
    'suites': [   {   'cases': [   {'code': '>>> assert np.isclose(get_gripper_location(arm_geometry_optimized)[0], target[0], atol=0.01)\n', 'hidden': False, 'locked': False},
                                   {'code': '>>> assert np.isclose(get_gripper_location(arm_geometry_optimized)[1], target[1], atol=0.01)\n', 'hidden': False, 'locked': False}],
                      'scored': True,
                      'setup': '',
                      'teardown': '',
                      'type': 'doctest'}]}
