from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Class that extends Pydantics base settings to read in
    environment variables from a file.
    """

    # used to connect to icat
    icat_url: str
    # used to authenticate the api against icat
    icat_authenticator_name: str
    icat_username: str
    icat_password: str
    icat_check_cert: bool
    # whether to check certs when using requests
    ssl_cert_verification: bool

    class Config:
        env_file = "./config.env"


# create a single instance on the class to import
settings = Settings()
