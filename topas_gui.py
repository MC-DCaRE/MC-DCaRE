from __future__ import annotations

import logging
import os

import FreeSimpleGUI as sg
from src.gui.controller import GUIController
from src.gui.view import MainView
from src.orchestrator import Orchestrator

logging.basicConfig(level=logging.DEBUG)


def main() -> None:
    sg.theme("Reddit")
    sg.set_options(scaling=1)
    view = MainView()
    orchestrator = Orchestrator(os.getcwd())
    controller = GUIController(view, orchestrator)
    controller.run()
    view.close()


if __name__ == "__main__":
    main()
