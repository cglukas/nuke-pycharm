"""Module for editing python script knobs of nuke node inside PyCharm"""
import inspect
import logging
import pathlib
import shutil
import subprocess
from typing import Dict, List

import nuke

PYCHARM = (
    r"C:\Program Files\JetBrains\PyCharm Community Edition 2021.3.1\bin\pycharm64.exe"
)
TEMP_FOLDER = pathlib.Path(inspect.getfile(inspect.currentframe())).parent / "knob_tmp"


def get_python_scripts(node: nuke.Node) -> Dict[str, str]:
    """get all scripts from python script buttons

    Args:
        node: node to extract scripts from

    Returns:
        dict with knob name and corresponding script
    """
    scripts = {}
    for knob in node.allKnobs():
        if not isinstance(knob, nuke.PyScript_Knob):
            continue
        scripts[knob.name()] = knob.value()
    return scripts


def create_temp_files(_scripts: Dict) -> List[str]:
    """Create the temp python files from the extracted code

    Args:
        _scripts: knobnames and python scripts

    Returns:
        list of created temp files
    """

    edit_files = []
    for name, script in _scripts.items():
        temp_file = TEMP_FOLDER / f"{name}.py"
        with open(temp_file, "w") as tmp:
            tmp.write(script)
        edit_files.append(str(temp_file))
    return edit_files


def main(node: nuke.Node = None):
    """Edit the scripts of PyScript knobs inside PyCharm

    Args:
        node: (optional) nuke node, default is the selected node

    Notes:
        This will show up a message box. Therefore, it will require the nuke GUI
    """
    # IDK if anybody would ever want to edit from the commandline interface
    if not nuke.GUI:
        logging.warning('Nuke GUI required.')
        return

    try:
        TEMP_FOLDER.mkdir(exist_ok=True)
        node = node or nuke.selectedNode()

        scripts = get_python_scripts(node)
        if not scripts:
            logging.info(f"Node '{node.name()}' has no PyScript-knobs.")
            return

        edit_files = create_temp_files(scripts)

        # Arguments following the PyCharm executable will be opened in the editor
        subprocess.call([PYCHARM, *edit_files])
        nuke.message("Click OK as soon as you saved your code changes")

        for name, script in zip(scripts.keys(), edit_files):
            with open(script) as tmp:
                node.knob(name).setValue(tmp.read())

    except ValueError:
        logging.warning('No node selected!')
    finally:
        shutil.rmtree(TEMP_FOLDER)


if __name__ == "__main__":
    main()

