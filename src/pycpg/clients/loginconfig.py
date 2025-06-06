from pycpg.response import PycpgResponse


class LoginConfigurationClient:
    def __init__(self, connection):
        self._connection = connection

    def get_for_user(self, username):
        """Retrieves login configuration for a given username. Possible `loginType` values are
        `LOCAL`, `LOCAL_2FA`, and `CLOUD_SSO`. If username does not exist the default
        return value is `LOCAL_2FA`.

        Args:
            username (str): Username to retrieve login configuration for.

        Returns:
            :class:`pycpg.response.PycpgResponse`
        """
        uri = f"{self._connection.host_address}/api/v3/LoginConfiguration"
        response = self._connection._session.get(uri, params={"username": username})
        return PycpgResponse(response)
