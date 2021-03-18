import os
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import pkg_resources
from subprocess import call, check_output


@dataclass
class Dependency:
    name: str
    current_version: str
    update_version: Optional[str] = None


DIR = os.path.dirname(os.path.realpath(__file__))
DEPS: Dict[str, List[Dependency]] = {"dev.txt": [], "prod.txt": []}
UPDATED_DEPS: Dict[str, str] = {}


def upgrage_packages():
    packages = [dist.project_name for dist in pkg_resources.working_set]
    call("pip install --upgrade " + " ".join(packages), shell=True)


def check_dependency_files():
    file_list: List[str] = []
    for _file in Path(DIR).iterdir():
        if _file.name not in DEPS:
            continue
        file_list.append(_file.name)

    assert set(file_list) == set(
        DEPS
    ), f"Files do not match, {set(file_list)} and {set(DEPS)}"
    print("Dependency files check is OK")


def get_dependencies(file):
    with open(f"{DIR}/{file.name}", "r") as f:
        lines = f.readlines()
        for line in lines:
            if "\n" in line:
                line = line.replace("\n", "")
            line = line.split("==")
            DEPS[file.name].append(
                Dependency(
                    name=line[0], current_version=line[1] if len(line) > 1 else None
                )
            )


def get_current_dependencies():
    for _file in Path(DIR).iterdir():
        if _file.name in DEPS:
            get_dependencies(_file)


def get_updated_list():
    li = check_output(["pip", "freeze", "--disable-pip-version-check"])
    for line in li.splitlines():
        line = line.decode("utf-8")
        if "==" not in line:
            continue
        name, version = line.split("==")
        UPDATED_DEPS[name] = version
    print(f"Getting update list is complete with {len(UPDATED_DEPS)} dependencies")


def update_deps():
    for _file, dep_list in DEPS.items():
        for dep in dep_list:
            if dep.name not in UPDATED_DEPS:
                continue
            dep.update_version = UPDATED_DEPS[dep.name]
    print("Updating dependency objects is complete")


def write_to_files():
    for _file, dep_list in DEPS.items():
        content = ""
        for dep in dep_list:
            content += dep.name
            if dep.update_version:
                content += f"=={dep.update_version}"
            else:
                if dep.current_version:
                    content += f"=={dep.current_version}"
            content += "\n"
        with open(f"{DIR}/{_file}", "w") as f:
            f.write(content)

    print("Writing complete")


if __name__ == "__main__":
    upgrage_packages()
    check_dependency_files()
    get_current_dependencies()
    get_updated_list()
    update_deps()
    write_to_files()
    print("Program successfuly ended")
