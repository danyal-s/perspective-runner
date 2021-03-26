import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    BINANCE_API_SECRET = os.environ.get("BINANCE_API_SECRET", None)
    BINANCE_API_KEY = os.environ.get("BINANCE_API_KEY", None)
    ETHERSCAN_API_KEY = os.environ.get("ETHERSCAN_API_KEY", None)
    BACKEND_API_PORT = os.environ.get("BACKEND_API_PORT", None)


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True