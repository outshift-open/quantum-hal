# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""Pytest configuration for conformance tests"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
# Looks for .env in test/conformance/ or test/ directories
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if not os.path.exists(dotenv_path):
    dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path)

# Add generated proto stubs to Python path
# This runs once when pytest starts, before importing test modules
gen_python_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../gen/python'))
if gen_python_path not in sys.path:
    sys.path.insert(0, gen_python_path)
