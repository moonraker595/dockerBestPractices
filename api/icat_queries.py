import logging

from icat.client import Client
from icat.query import Query

from api.config import settings


class IcatQueries:
    """
    A wrapper Class around python icat that logs into ICAT and stores the client,
    as a global variable, for use elsewhere.
    """

    def __init__(self):
        self.CLIENT = None
        self.create_client()

    def create_client(self):
        """
        Method to create the client when the application first starts
        """
        try:
            self.CLIENT = Client(settings.icat_url, checkCert=settings.icat_check_cert)
        except Exception as e:
            raise Exception(
                "Could not create python-icat client, check VPN / Firewall. Error: "
                f"{settings.icat_url}, {e}",
            )

    def login(self):
        """
        Method to set the global `CLIENT` for use elsewhere in the script
        """

        self.CLIENT.login(
            settings.icat_authenticator_name,
            {
                "username": settings.icat_username,
                "password": settings.icat_password,
            },
        )
        logging.info(
            f"Successfully logged into ICAT as username: {self.CLIENT.getUserName()}, "
            f"ICAT Version: {self.CLIENT.getVersion()}",
        )

    def get(self, object_type, search_key, search_value, includes=None):
        """
        Method to get objects in ICAT
        :param object_type: The type of object e.g: Investigations.
        :param search_key: What to search on e.g: name.
        :param search_value: What to search with e.g: "alex".
        :param includes: Any other objects to get relating to the object_type.
        :return: The return of the search, the ICAT object.
        """
        logging.info(f"Getting {object_type} with a {search_key} of {search_value}")

        query = Query(
            self.CLIENT,
            object_type,
            conditions={search_key: [f"= '{search_value}'"]},
            includes=includes,
        )
        icat_object = self.CLIENT.search(query)
        return icat_object[0]


# create a single instance
icatQueries = IcatQueries()  # noqa: N816
