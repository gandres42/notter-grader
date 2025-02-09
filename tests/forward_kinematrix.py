OK_FORMAT = True

test = {   'name': 'forward_kinematrix',
    'points': 5,
    'suites': [   {   'cases': [   {'code': ">>> assert np.all(np.isclose(arm_geometry_fk[0]['Matrix_pose'], mat_check_base, atol=0.01))\n", 'hidden': False, 'locked': False},
                                   {'code': ">>> assert np.all(np.isclose(arm_geometry_fk[1]['Matrix_pose'], mat_check_link_1, atol=0.01))\n", 'hidden': False, 'locked': False},
                                   {'code': ">>> assert np.all(np.isclose(arm_geometry_fk[2]['Matrix_pose'], mat_check_link_2, atol=0.01))\n", 'hidden': False, 'locked': False},
                                   {'code': ">>> assert np.all(np.isclose(arm_geometry_fk[3]['Matrix_pose'], mat_check_link_3, atol=0.01))\n", 'hidden': False, 'locked': False},
                                   {'code': ">>> assert np.all(np.isclose(arm_geometry_fk[-1][0]['Matrix_pose'], mat_check_wrist, atol=0.01))\n", 'hidden': False, 'locked': False}],
                      'scored': True,
                      'setup': '',
                      'teardown': '',
                      'type': 'doctest'}]}
