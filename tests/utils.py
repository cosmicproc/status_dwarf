import os


def exclude_github_actions(func):
    def wrapper(*args, **kwargs):
        if not os.environ.get('GITHUB_ACTIONS'):
            return func(*args, **kwargs)

    return wrapper
