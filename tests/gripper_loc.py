OK_FORMAT = True

test = {   'name': 'gripper_loc',
    'points': 2,
    'suites': [   {   'cases': [{'code': '>>> assert np.isclose(grasp_loc[0], -0.8106, atol=0.01) and np.isclose(grasp_loc[1], 0.92437, atol=0.01)\n', 'hidden': False, 'locked': False}],
                      'scored': True,
                      'setup': '',
                      'teardown': '',
                      'type': 'doctest'}]}
