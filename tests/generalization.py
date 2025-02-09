OK_FORMAT = True

test = {   'name': 'generalization',
    'points': 4,
    'suites': [   {   'cases': [   {   'code': '>>> assert np.isclose(get_gripper_location(arm_longer)[0], 0.59, atol=0.1) or np.isclose(get_gripper_location(arm_longer_optimized)[0], '
                                               'target_longer[0], atol=0.01)\n',
                                       'hidden': False,
                                       'locked': False},
                                   {   'code': '>>> assert np.isclose(get_gripper_location(arm_longer)[0], 0.59, atol=0.1) or np.isclose(get_gripper_location(arm_longer_optimized)[0], '
                                               'target_longer[0], atol=0.01)\n',
                                       'hidden': False,
                                       'locked': False}],
                      'scored': True,
                      'setup': '',
                      'teardown': '',
                      'type': 'doctest'}]}
