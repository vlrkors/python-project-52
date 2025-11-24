import os
import sys
from pathlib import Path


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task_manager.settings")
    try:
        from django.core.management import execute_from_command_line
    except ModuleNotFoundError:
        base_dir = Path(__file__).resolve().parent
        venv_site = (
            base_dir
            / ".venv"
            / "lib"
            / f"python{sys.version_info.major}.{sys.version_info.minor}"
            / "site-packages"
        )
        sys.path.insert(0, str(venv_site))
        from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
