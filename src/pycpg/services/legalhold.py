from pycpg import settings
from pycpg.exceptions import PycpgBadRequestError
from pycpg.exceptions import PycpgError
from pycpg.exceptions import PycpgForbiddenError
from pycpg.exceptions import PycpgLegalHoldAlreadyActiveError
from pycpg.exceptions import PycpgLegalHoldAlreadyDeactivatedError
from pycpg.exceptions import PycpgLegalHoldCriteriaMissingError
from pycpg.exceptions import PycpgLegalHoldNotFoundOrPermissionDeniedError
from pycpg.exceptions import PycpgUserAlreadyAddedError
from pycpg.services import BaseService
from pycpg.services.util import get_all_pages
from pycpg.util import parse_timestamp_to_milliseconds_precision


def _active_state_map(active):
    _map = {True: "ACTIVE", False: "INACTIVE", None: "ALL"}
    try:
        return _map[active]
    except KeyError:
        raise PycpgError(
            f"Invalid argument: '{active}'. active must be True, False, or None"
        )


class LegalHoldService(BaseService):
    """A service for interacting with CrashPlan Legal Hold APIs.

    The LegalHoldService provides the ability to manage CrashPlan Legal Hold Policies and Matters.
    It can:
    - Create, view, and list all existing Policies.
    - Create, view, deactivate, reactivate, and list all existing Matters.
    - Add/remove Custodians from a Matter.
    """

    _uri_prefix = "/api/v38"

    # object strings to pass to specify error messages
    _membership_string = "membership"
    _policy_string = "policy"
    _matter_string = "matter"

    def create_policy(self, name):
        """Creates a new Legal Hold Preservation Policy.

        Args:
            name (str): The name of the new Policy.

        Returns:
            :class:`pycpg.response.PycpgResponse`
        """
        uri = f"{self._uri_prefix}/legal-hold-policy/create"
        data = {"name": name}
        return self._connection.post(uri, json=data)

    def create_matter(
        self,
        name,
        legal_hold_policy_uid,
        description=None,
        notes=None,
        externalReference=None,
    ):
        """Creates a new, active Legal Hold Matter.

        Args:
            name (str): The name of the new Legal Hold Matter.
            legal_hold_policy_uid (str): The identifier of the Preservation Policy that will apply to this
                Matter.
            description (str, optional): An optional description of the Matter. Defaults to None.
            notes (str, optional): Optional notes information. Defaults to None.
            externalReference (str, optional): Optional external reference information. Defaults to None.

        Returns:
            :class:`pycpg.response.PycpgResponse`
        """
        uri = f"{self._uri_prefix}/legal-hold-matter/create"
        data = {
            "policyId": legal_hold_policy_uid,
            "name": name,
            "description": description,
            "notes": notes,
            "externalReference": externalReference,
        }
        return self._connection.post(uri, json=data)

    def get_policy_by_uid(self, legal_hold_policy_uid):
        """Gets a single Preservation Policy.

        Args:
            legal_hold_policy_uid (str): The unique identifier of the Preservation Policy.

        Returns:
            :class:`pycpg.response.PycpgResponse`: A response containing the Policy.
        """
        uri = f"{self._uri_prefix}/legal-hold-policy/view"
        params = {"legalHoldPolicyUid": legal_hold_policy_uid}
        try:
            return self._connection.get(uri, params=params)
        except PycpgForbiddenError as err:
            raise PycpgLegalHoldNotFoundOrPermissionDeniedError(
                err, legal_hold_policy_uid, self._policy_string
            )

    def get_policy_list(self):
        """Gets a list of existing Preservation Policies.

        Returns:
            :class:`pycpg.response.PycpgResponse`: A response containing the list of Policies.
        """
        uri = f"{self._uri_prefix}/legal-hold-policy/list"
        return self._connection.get(uri)

    def get_matter_by_uid(self, legal_hold_matter_uid):
        """Gets a single Legal Hold Matter.

        Args:
            legal_hold_matter_uid (str): The unique identifier of the Legal Hold Matter.

        Returns:
            :class:`pycpg.response.PycpgResponse`: A response containing the Matter.
        """
        uri = f"{self._uri_prefix}/legal-hold-matter/view"
        params = {
            "legalHoldUid": legal_hold_matter_uid,
        }
        try:
            return self._connection.get(uri, params=params)
        except PycpgForbiddenError as err:
            raise PycpgLegalHoldNotFoundOrPermissionDeniedError(
                err, legal_hold_matter_uid
            )

    def get_matters_page(
        self,
        page_num,
        creator_user_uid=None,
        active=True,
        name=None,
        externalReference=None,
        page_size=None,
    ):
        """Gets a page of existing Legal Hold Matters.

        Args:
            page_num (int): The page number to request.
            creator_user_uid (str, optional): Find Matters by the identifier of the user who created
                them. Defaults to None.
            active (bool or None, optional): Find Matters by their active state. True returns
                active Matters, False returns inactive Matters, None returns all Matters regardless
                of state. Defaults to True.
            name (str, optional): Find Matters with a 'name' that either equals or contains
                this value. Defaults to None.
            externalReference (str, optional): Find Matters having a matching external reference field.
                Defaults to None.
            page_size (int, optional): The number of legal hold items to return per page.
                Defaults to `pycpg.settings.items_per_page`.


        Returns:
            :class:`pycpg.response.PycpgResponse`:
        """

        page_size = page_size or settings.items_per_page
        uri = f"{self._uri_prefix}/legal-hold-matter/list"
        params = {
            "creatorPrincipalId": creator_user_uid,
            "active": str(active).lower(),
            "name": name,
            "externalReference": externalReference,
            "page": page_num,
            "pageSize": page_size,
        }
        return self._connection.get(uri, params=params)

    def get_all_matters(
        self, creator_user_uid=None, active=True, name=None, externalReference=None
    ):
        """Gets all existing Legal Hold Matters.

        Args:
            creator_user_uid (str, optional): Find Matters by the identifier of the user who created
                them. Defaults to None.
            active (bool or None, optional): Find Matters by their active state. True returns
                active Matters, False returns inactive Matters, None returns all Matters regardless
                of state. Defaults to True.
            name (str, optional): Find Matters with a 'name' that either equals or contains
                this value. Defaults to None.
            externalReference (str, optional): Find Matters having a matching external reference field.
                Defaults to None.

        Returns:
            generator: An object that iterates over :class:`pycpg.response.PycpgResponse` objects
            that each contain a page of Legal Hold Matters.
        """
        return get_all_pages(
            self.get_matters_page,
            None,
            creator_user_uid=creator_user_uid,
            active=active,
            name=name,
            externalReference=externalReference,
        )

    def get_custodians_page(
        self,
        page_num,
        legal_hold_matter_uid=None,
        user_uid=None,
        user=None,
        active=True,
        page_size=None,
    ):
        """Gets an individual page of Legal Hold memberships. One of the following
        optional args is required to determine which custodians to retrieve:

        `legal_hold_uid`, `user_uid`, `user`


        Args:
            page_num (int): The page number to request.
            legal_hold_matter_uid (str, optional): Find LegalHoldMemberships for the Legal Hold Matter
                with this unique identifier. Defaults to None.
            user_uid (str, optional): Find LegalHoldMemberships for the user with this identifier.
                Defaults to None.
            user (str, optional): Find LegalHoldMemberships by flexibly searching on username,
                email, extUserRef, or last name. Will find partial matches. Defaults to None.
            active (bool or None, optional): Find LegalHoldMemberships by their active state. True
                returns active LegalHoldMemberships, False returns inactive LegalHoldMemberships,
                None returns all LegalHoldMemberships regardless of state. Defaults to True.
            page_size (int, optional): The size of the page. Defaults to `pycpg.settings.items_per_page`.

        Returns:
            :class:`pycpg.response.PycpgResponse`:
        """
        active_state = _active_state_map(active)
        page_size = page_size or settings.items_per_page
        params = {
            "userUid": user_uid,
            "legalHoldUid": legal_hold_matter_uid,
            "user": user,
            "active": active_state,
            "page": page_num,
            "pageSize": page_size,
        }
        uri = f"{self._uri_prefix}/legal-hold-membership/list"
        try:
            return self._connection.get(uri, params=params)
        except PycpgBadRequestError as ex:
            if "At least one criteria must be specified" in ex.response.text:
                raise PycpgLegalHoldCriteriaMissingError(ex)
            raise

    def get_all_matter_custodians(
        self, legal_hold_matter_uid=None, user_uid=None, user=None, active=True
    ):
        """Gets all Legal Hold memberships.

        Each user (Custodian) who has been added to a Legal Hold Matter is returned by the server as
        a LegalHoldMembership object in the response body.  If the object's active state is
        "INACTIVE", they have been removed from the Matter and are no longer subject to the Legal
        Hold retention rules. Users can be Custodians of multiple Legal Holds at once (and thus
        would be part of multiple LegalHoldMembership objects).

        Args:
            legal_hold_matter_uid (str, optional): Find LegalHoldMemberships for the Legal Hold Matter
                with this unique identifier. Defaults to None.
            user_uid (str, optional): Find LegalHoldMemberships for the user with this identifier.
                Defaults to None.
            user (str, optional): Find LegalHoldMemberships by flexibly searching on username,
                email, extUserRef, or last name. Will find partial matches. Defaults to None.
            active (bool or None, optional): Find LegalHoldMemberships by their active state. True
                returns active LegalHoldMemberships, False returns inactive LegalHoldMemberships,
                None returns all LegalHoldMemberships regardless of state. Defaults to True.

        Returns:
            generator: An object that iterates over :class:`pycpg.response.PycpgResponse` objects
            that each contain a page of LegalHoldMembership objects.
        """
        return get_all_pages(
            self.get_custodians_page,
            None,
            legal_hold_matter_uid=legal_hold_matter_uid,
            user_uid=user_uid,
            user=user,
            active=active,
        )

    def get_events_page(
        self,
        legal_hold_uid=None,
        min_event_date=None,
        max_event_date=None,
        page_num=1,
        page_size=None,
    ):
        """Gets an individual page of Legal Hold events.


        Args:
            legal_hold_uid (str): Find LegalHoldEvents for the Legal Hold
                Matter with this unique identifier. Defaults to None.
            min_event_date (str or int or float or datetime, optional): Find
                LegalHoldEvents whose eventDate is equal to or after this time.
                E.g. yyyy-MM-dd HH:MM:SS. Defaults to None.
            max_event_date (str or int or float or datetime, optional): Find
                LegalHoldEvents whose eventDate is equal to or before this time.
                E.g. yyyy-MM-dd HH:MM:SS. Defaults to None.
            page_num (int): The page number to request. Defaults to 1.
            page_size (int, optional): The size of the page.
                Defaults to `pycpg.settings.items_per_page`.

        Returns:
            :class:`pycpg.response.PycpgResponse`:
        """
        page_size = page_size or settings.items_per_page
        if min_event_date:
            min_event_date = parse_timestamp_to_milliseconds_precision(min_event_date)
        if max_event_date:
            max_event_date = parse_timestamp_to_milliseconds_precision(max_event_date)
        params = {
            "legalHoldUid": legal_hold_uid,
            "minEventDate": min_event_date,
            "maxEventDate": max_event_date,
            "page": page_num,
            "pageSize": page_size,
        }
        uri = "/api/v38/legal-hold-event/list"

        return self._connection.get(uri, params=params)

    def get_all_events(
        self, legal_hold_uid=None, min_event_date=None, max_event_date=None
    ):
        """Gets an individual page of Legal Hold events.

        Args:
            legal_hold_uid (str): Find LegalHoldEvents for the Legal Hold Matter
                with this unique identifier. Defaults to None.
            min_event_date (str or int or float or datetime, optional): Find
                LegalHoldEvents whose eventDate is equal to or after this time.
                E.g. yyyy-MM-dd HH:MM:SS. Defaults to None.
            max_event_date (str or int or float or datetime, optional): Find
                LegalHoldEvents whose eventDate is equal to or before this time.
                E.g. yyyy-MM-dd HH:MM:SS. Defaults to None.

        Returns:
            generator: An object that iterates over :class:`pycpg.response.PycpgResponse` objects
            that each contain a page of LegalHoldEvent objects.
        """
        return get_all_pages(
            self.get_events_page,
            None,
            legal_hold_uid=legal_hold_uid,
            min_event_date=min_event_date,
            max_event_date=max_event_date,
        )

    def add_to_matter(self, user_uid, legal_hold_matter_uid):
        """Add a user (Custodian) to a Legal Hold Matter.

        Args:
            user_uid (str): The identifier of the user.
            legal_hold_matter_uid (str): The identifier of the Legal Hold Matter.

        Returns:
            :class:`pycpg.response.PycpgResponse`
        """
        uri = f"{self._uri_prefix}/legal-hold-membership/create"
        data = {"legalHoldUid": legal_hold_matter_uid, "userUid": user_uid}
        try:
            return self._connection.post(uri, json=data)
        except PycpgBadRequestError as err:
            if "USER_ALREADY_IN_HOLD" in err.response.text:
                matter = self.get_matter_by_uid(legal_hold_matter_uid)
                matter_id_and_name_text = f"legal hold matter id={legal_hold_matter_uid}, name={matter['name']}"
                raise PycpgUserAlreadyAddedError(err, user_uid, matter_id_and_name_text)
            raise
        except PycpgForbiddenError as err:
            raise PycpgLegalHoldNotFoundOrPermissionDeniedError(
                err, legal_hold_matter_uid
            )

    def remove_from_matter(self, legal_hold_membership_uid):
        """Remove a user (Custodian) from a Legal Hold Matter.

        Args:
            legal_hold_membership_uid (str): The identifier of the LegalHoldMembership
                representing the Custodian to Matter relationship.

        Returns:
            :class:`pycpg.response.PycpgResponse`
        """
        uri = f"{self._uri_prefix}/legal-hold-membership/deactivate"
        data = {"legalHoldMembershipUid": legal_hold_membership_uid}
        try:
            return self._connection.post(uri, json=data)
        except PycpgForbiddenError as err:
            raise PycpgLegalHoldNotFoundOrPermissionDeniedError(
                err, legal_hold_membership_uid, self._membership_string
            )

    def deactivate_matter(self, legal_hold_matter_uid):
        """Deactivates and closes a Legal Hold Matter.

        Args:
            legal_hold_matter_uid (str): The identifier of the Legal Hold Matter.

        Returns:
            :class:`pycpg.response.PycpgResponse`
        """
        uri = f"{self._uri_prefix}/legal-hold-matter/deactivate"
        data = {"legalHoldUid": legal_hold_matter_uid}
        try:
            return self._connection.post(uri, json=data)
        except PycpgBadRequestError as err:
            if "ALREADY_DEACTIVATED" in err.response.text:
                raise PycpgLegalHoldAlreadyDeactivatedError(err, legal_hold_matter_uid)
            raise
        except PycpgForbiddenError as err:
            raise PycpgLegalHoldNotFoundOrPermissionDeniedError(
                err, legal_hold_matter_uid
            )

    def reactivate_matter(self, legal_hold_matter_uid):
        """Reactivates and re-opens a closed Matter.

        Args:
            legal_hold_matter_uid (str): The identifier of the Legal Hold Matter.

        Returns:
            :class:`pycpg.response.PycpgResponse`
        """
        uri = f"{self._uri_prefix}/legal-hold-matter/activate"
        data = {"legalHoldUid": legal_hold_matter_uid}
        try:
            return self._connection.post(uri, json=data)
        except PycpgBadRequestError as err:
            if "ALREADY_ACTIVE" in err.response.text:
                raise PycpgLegalHoldAlreadyActiveError(err, legal_hold_matter_uid)
            raise
        except PycpgForbiddenError as err:
            raise PycpgLegalHoldNotFoundOrPermissionDeniedError(
                err, legal_hold_matter_uid
            )
