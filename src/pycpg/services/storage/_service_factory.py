from functools import lru_cache

from pycpg.exceptions import PycpgError
from pycpg.services._connection import Connection
from pycpg.services.storage.archive import StorageArchiveService
from pycpg.services.storage.restore import PushRestoreService


class StorageServiceFactory:
    def __init__(self, connection, device_service):
        self._connection = connection
        self._device_service = device_service

    def create_push_restore_service(self, device_guid):
        conn = Connection.from_device_connection(self._connection, device_guid)
        return PushRestoreService(conn)

    @lru_cache(maxsize=None)  # noqa: B019
    def create_archive_service(self, device_guid, destination_guid):
        url = self.get_storage_url(device_guid, destination_guid)
        conn = self._connection.clone(url)
        return StorageArchiveService(conn)

    def get_storage_url(self, device_guid, destination_guid):
        uri = "api/v1/WebRestoreInfo"
        params = {"srcGuid": device_guid, "destGuid": destination_guid}
        response = self._connection.get(uri, params=params)
        return response["serverUrl"]

    def auto_select_destination_guid(self, device_guid):
        response = self._device_service.get_by_guid(
            device_guid, include_backup_usage=True
        )
        # take the first destination guid we find
        destination_list = response["backupUsage"]
        if not destination_list:
            raise PycpgError(f"No destinations found for device guid: {device_guid}")
        return destination_list[0]["targetComputerGuid"]
