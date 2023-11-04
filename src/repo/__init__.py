from .repo import Repository
from .sqlite import SQLite


REPOSITORIES = {
    'sqlite': SQLite,
}

def get_repository(repository_key: str) -> Repository:
    return REPOSITORIES[repository_key]()
