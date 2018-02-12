from git import Repo, InvalidGitRepositoryError

from .util import AbortError


def git_info_from_directory(directory):
    try:
        repo = Repo(directory, search_parent_directories=True)
    except InvalidGitRepositoryError:
        raise AbortError('No git repository found in, or above, "{}"'.format(directory))

    return {
        'commit': repo.head.commit.hexsha,
        'dirty': repo.is_dirty(),
    }
