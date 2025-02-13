import os
import sys

import django


def _add_django_paths():
    """Common path setup for both knowledge service and app contexts"""
    # for working in docker container
    sys.path.append(
        os.path.abspath(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "julee_django"
            )
        )
    )
    # for working directly on the file system
    sys.path.append(
        os.path.abspath(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "..", "julee_django"
            )
        )
    )
    sys.path.append(
        os.path.abspath(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
        )
    )


def setup_django():
    """Setup for knowledge service context"""
    from dotenv import load_dotenv

    load_dotenv(
        os.path.join(
            os.path.dirname(__file__), "..", ".envs", ".local", ".django"
        )
    )
    os.environ["CELERY_BROKER_URL"] = "redis://redis:6379/0"
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "julee_django.julee.settings"
    )
    _add_django_paths()
    django.setup()


def setup_django_for_app():
    """Setup for app context"""
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "julee_django.julee.settings"
    )
    _add_django_paths()
    django.setup()
