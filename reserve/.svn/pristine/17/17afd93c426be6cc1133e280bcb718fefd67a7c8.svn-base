# -*- coding: utf-8 -*-
"""
:created on: '12/5/14'

:copyright: NSN
:author: Bartłomiej Idzikowski
:contact: bartlomiej.idzikowski@nokia.com
"""

import logging
from ute_cloud_common_api.common import CloudCommonApi
from ute_cloud_common_api.exception import ApiParametersValidationFailException, ApiActionNotPermittedException
from ute_cloud_reservation_api.exception import ApiCloudReservationException, ApiMaxReservationCountExceededException, \
    ApiTooEarlyExtendAttemptException, ApiWrongReservationStatusFoundException, ApiDeactivatedTestlineFoundException, \
    ApiTestlineRestrictedAccessFoundException, ApiMaxExtendTimeExceededException


_logger = logging.getLogger(__name__)


class CloudReservationApi(CloudCommonApi):
    API_EXCEPTIONS = {
        100: ApiActionNotPermittedException,
        200: ApiParametersValidationFailException,
        300: ApiCloudReservationException,
        301: ApiMaxReservationCountExceededException,
        302: ApiTooEarlyExtendAttemptException,
        303: ApiWrongReservationStatusFoundException,
        304: ApiDeactivatedTestlineFoundException,
        305: ApiTestlineRestrictedAccessFoundException,
        306: ApiMaxExtendTimeExceededException,
    }

    def __request(self, resource, data, method='post'):
        return self._request(resource, data, CloudReservationApi.API_EXCEPTIONS, method)

    def create_reservation(self, testline_type=None, enb_build=None, ute_build=None, sysimage_build=None, test_repository_revision=None,
                           state=None, duration=None, tags=None, share_with=None):
        """Create reservation.

        :param string testline_type: Testline types eg. CLOUD_F. By default high-priority.
        :param string enb_build: eNB build name. By default latest active.
        :param string ute_build: Version of UTE package. By default latest active.
        :param sysimage_build: System image version. By default latest active.
        :param string test_repository_revision: Test repository revision. By default latest revision (HEAD).
        :param string state: eNB state which should be achieved eg. configured, commissioned. By default configured.
        :param integer duration: Testline reservation duration in minutes. Maximum is 420. By default 60.
        :param list tags: List of tags names. By default empty.
        :param list share_with: List of users who will be granted access to newly created reservation. By default empty.
        :type: share_with: list of str, each str is User`s username
        :rtype: integer
        :return: Reservation id.

        """
        resource = 'reservation/create'

        request_data = {
            "testline_type": testline_type,
            "enb_build": enb_build,
            "ute_build": ute_build,
            "sysimage_build": sysimage_build,
            "test_repository_revision": test_repository_revision,
            "state": state,
            "duration": duration,
            "tags": tags,
            "share_with": share_with,
        }
        return self.__request(resource, request_data)

    def extend_reservation(self, reservation_id, duration=None):
        """Extend ongoing reservation.

        :param reservation_id: Reservation id.
        :param duration: Duration in minutes between 1 and 180. Default: 60.
        """
        resource = 'reservation/extend'

        request_data = {
            "id": reservation_id,
            "duration": duration
        }
        return self.__request(resource, request_data)

    def share_reservation(self, reservation_id, users):
        """Share reservation with other users so that they can extend, release and see reservation details.

        :param reservation_id: Reservation id.
        :param users: Users who will be granted access to Reservation.
        :type: users: list of str, each str is User`s username
        """

        resource = 'reservation/add_sharing_users'

        request_data = {
            "id": reservation_id,
            "share_with": users
        }
        return self.__request(resource, request_data)

    def get_reservation_status(self, reservation_id):
        """Get reservation status as text.

        Status list:
          - 'Pending for testline'
          - 'Testline assigned'
          - 'Confirmed'
          - 'Finished'
          - 'Canceled'

        :param integer reservation_id: Reservation id.
        :rtype: string
        """
        resource = 'reservation/status'
        request_data = {"id": reservation_id}
        return self.__request(resource, request_data, method='get')

    def get_reservation_details(self, reservation_id):
        """Get reservation details.

        :param integer reservation_id: Reservation id.
        :rtype: dict
        :return:

        .. code-block:: python

            rs['id']                        # reservation id
            rs['user']                      # reservation requestor username
            rs['status']                    # reservation status
            rs['testline_type']             # reservation requested testline_type
            rs['enb_build']                 # eNB build name
            rs['ute_build']                 # ute linux package build version
            rs['sysimage_build']            # system image build name
            rs['test_repository_revision']  # test repository revision
            rs['add_date']                  # reservation add date
            rs['start_date']                # reservation start date
            rs['end_date']                  # reservation end date
            rs['testline']['name']          # reservation test line name
            rs['testline']['address']       # reservation test line address. If testline has more VM, master VM address will be provided.
            rs['testline']['site']          # reservation test line site
            rs['tags']                      # reservation tags

        """
        resource = 'reservation/details'
        request_data = {"id": reservation_id}
        return self.__request(resource, request_data, method='get')

    def release_reservation(self, reservation_id):
        """Release reservation. Reservation will be canceled/finished depends on reservation status.

        :param integer reservation_id: Reservation id.
        :rtype: integer
        :return: Reservation id.
        """
        resource = 'reservation/release'
        request_data = {"id": reservation_id}
        return self.__request(resource, request_data)

    def get_available_tl_count_group_by_type(self):
        """Get available test line count grouped by TL type.

        :rtype: dict
        :return: Dict where key is testline type and value is number of available test lines. eg. {"CLOUD_F": 10}
        """
        resource = 'metric/get_available_tl_count_group_by_type'
        request_data = {}
        return self.__request(resource, request_data, method='get')

    def get_available_tl_count(self):
        """Get available test line count.

        :rtype: int

        """
        resource = 'metric/get_available_tl_count'
        request_data = {}
        return self.__request(resource, request_data, method='get')

    def get_testline_type_details(self, name):
        """Get testline type details.

        :param string name: Testline type name.
        :rtype: dict
        :return:

        .. code-block:: python

            details['name']                     # testline type name
            details['agent']                    # testline type related agent name
            details['active']                   # whether if testline type is active
            details['compatibility_regex']      # regex that defines testline type compatible enbbuild
            details['states']                   # list of avialable testline type states
        """
        resource = 'testline_type/details'
        request_data = {"name": name}
        return self.__request(resource, request_data, method='get')

    def list_my_reservations(self, status=None, offset=0, limit=10, shared=False):
        """List all user reservation ids sorted by add date descending (newest on top).

        :param string status: Reservation status is optional parameter. Possible values are listed below. Default: None. List reservation ids
            regardless of its status.

            Status list:
              - 'Pending for testline'
              - 'Testline assigned'
              - 'Confirmed'
              - 'Finished'
              - 'Canceled'
        :param integer offset: Skip first offset ids. Default: 0.
        :param integer limit: No more than limit ids will be returned. Default: 10.
        :param boolean shared: If True include reservations shared with user. Default: False

        :Example:
            - list_my_reservations() - list first 10 user reservation ids regardless of its status.
            - list_my_reservations(status='Finished') - list first 10 user reservation ids that have 'Finished' status.
            - list_my_reservations(offset=5) - list 10 user reservation ids from 6 to 15.
            - list_my_reservations(offset=10, limit=5) - list 5 user reservation ids from 11 to 15.

        :rtype: list
        :return: List with user reservation ids.
        """
        resource = 'reservation/list'
        request_data = {
            'status': status,
            'offset': offset,
            'limit': limit,
            'shared': shared
        }
        return self.__request(resource, request_data, method='get')

    def get_available_testlines_by_types_for_user(self, user=None, testline_type=None):
        """
        Get testlines available for `user` and group them by types. If `testline_type` passed - get available testlines for `user` for this specific
        `testline_type` only.

        :param string user:          string representing username. Default: requestor.
        :param string testline_type: string representing `testline_type` name. Default: None.

        :Example:
            - get_available_testlines_by_types_for_user() - get all available `testlines` ids for requestor and group them by types.
            - get_available_testlines_by_types_for_user(testline_type='CLOUD_F') - get all available `testlines` ids for `CLOUD_F` type for requestor.
            - get_available_testlines_by_types_for_user(user='username') - get all available `testlines` ids for `user` and group them by types.
            - get_available_testlines_by_types_for_user(user='username', testline_type='CLOUD_F') - get all available `testlines` ids for `CLOUD_F`
                                                                                                    type for `user`.

        :rtype:     dict
        :return:    Return dictionary with `testline types` as a keys and values are ids of `testlines` which ara available for `user` OR ids of
                    available testlines for specific `testline_type` for `user`.
        """

        resource = 'metric/get_available_testlines_by_types_for_user'
        request_data = {"user": user, 'testline_type': testline_type}
        return self.__request(resource, request_data, method='get')

    def reserve_quick_reservation(self, reservation_id):
        """
        Reserve pre-prepared quick reservation
        :param reservation_id: Quick reservation id
        :return: Dictionary with reservation status
        """
        resource = 'reservation/quick/create'
        request_data = {"id": reservation_id}
        return self.__request(resource, request_data)

    def list_available_quick_reservations(self):
        """
        List prepared reservations which can be reserved.

        :return: Returns list of available reservations.
        One entry of returned reservation is a dictionary with fields:
        'ute_build',
        'testline': assigned testline name,
        'id': reservation id,
        'enb_build': enb_build:tag,
        'testline_type': 'CLOUD_R4P'
        """
        resource = 'reservation/quick/list_available_reservations'

        return self.__request(resource, {}, method='get')
