#!/usr/bin/env python3
"""Entrypoint: copy the pre-rendered entry image to the output dir."""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
shutil.copyfile(
    os.path.join(HERE, "entry.png"),
    os.path.join(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"),
                 "entry.png"))
