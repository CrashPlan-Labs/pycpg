class AuditLogsClient:
    """`Rest documentation <https://developer.crashPlan.com/api/#tag/Audit-Log>`__"""

    def __init__(self, audit_log_service):
        self._audit_log_service = audit_log_service

    def get_page(
        self,
        page_num=1,
        page_size=None,
        begin_time=None,
        end_time=None,
        event_types=None,
        user_ids=None,
        usernames=None,
        user_ip_addresses=None,
        affected_user_ids=None,
        affected_usernames=None,
        **kwargs
    ):
        """Retrieve a page of audit logs, filtered based on given arguments.

        Note: `page_num` here can be used same way as other methods that have a
        `page_num` parameter in pycpg. However, under the hood, it subtracts one from
        the given `page_num` in the implementation as the CrashPlan Audit-Logs API expects
        the start page to be zero.
        `Rest Documentation <https://developer.crashPlan.com/api/#operation/rpc/search/search-audit-log>`__

        Args:
            page_num (int, optional): The page number to get. Defaults to 1.
            page_size (int, optional): The number of items per page. Defaults to `pycpg.settings.items_per_page`.
            begin_time (int or float or str or datetime, optional): Timestamp in milliseconds or
                str format "yyyy-MM-dd HH:MM:SS" or a datetime instance. Defaults to None.
            end_time (int or float or str or datetime, optional): Timestamp in milliseconds or
                str format "yyyy-MM-dd HH:MM:SS" or a datetime instance. Defaults to None.
            event_types (str or list, optional): A str or list of str of valid event types. Defaults to None.
            user_ids (str or list, optional): A str or list of str of CrashPlan userUids. Defaults to None.
            usernames (str or list, optional): A str or list of str of CrashPlan usernames. Defaults to None.
            user_ip_addresses (str or list, optional): A str or list of str of user ip addresses. Defaults to None.
            affected_user_ids (str or list, optional): A str or list of str of affected CrashPlan userUids. Defaults to None.
            affected_usernames (str or list, optional): A str or list of str of affected CrashPlan usernames. Defaults to None.

        Returns:
            :class:`pycpg.response.PycpgResponse`
        """
        return self._audit_log_service.get_page(
            page_num=page_num,
            page_size=page_size,
            begin_time=begin_time,
            end_time=end_time,
            event_types=event_types,
            user_ids=user_ids,
            usernames=usernames,
            user_ip_addresses=user_ip_addresses,
            affected_user_ids=affected_user_ids,
            affected_usernames=affected_usernames,
            **kwargs
        )

    def get_all(
        self,
        begin_time=None,
        end_time=None,
        event_types=None,
        user_ids=None,
        usernames=None,
        user_ip_addresses=None,
        affected_user_ids=None,
        affected_usernames=None,
        **kwargs
    ):
        """Retrieve audit logs, filtered based on given arguments.
        `Rest Documentation <https://developer.crashPlan.com/api/#operation/rpc/search/search-audit-log>`__

        Args:
            begin_time (int or float or str or datetime, optional): Timestamp in milliseconds or
                str format "yyyy-MM-dd HH:MM:SS" or a datetime instance. Defaults to None.
            end_time (int or float or str or datetime, optional): Timestamp in milliseconds or
                str format "yyyy-MM-dd HH:MM:SS" or a datetime instance. Defaults to None.
            event_types (str or list, optional): A str or list of str of valid event types. Defaults to None.
            user_ids (str or list, optional): A str or list of str of CrashPlan userUids. Defaults to None.
            usernames (str or list, optional): A str or list of str of CrashPlan usernames. Defaults to None.
            user_ip_addresses (str or list, optional): A str or list of str of user ip addresses. Defaults to None.
            affected_user_ids (str or list, optional): A str or list of str of affected CrashPlan userUids. Defaults to None.
            affected_usernames (str or list, optional): A str or list of str of affected CrashPlan usernames. Defaults to None.

        Returns:
            generator: An object that iterates over :class:`pycpg.response.PycpgResponse` objects
            that each contain a page of audit logs.
        """
        return self._audit_log_service.get_all(
            begin_time=begin_time,
            end_time=end_time,
            event_types=event_types,
            user_ids=user_ids,
            usernames=usernames,
            user_ip_addresses=user_ip_addresses,
            affected_user_ids=affected_user_ids,
            affected_usernames=affected_usernames,
            **kwargs
        )
