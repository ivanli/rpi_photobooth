#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_state_screensaver
----------------------------------

Tests for `state_screensaver` module.
"""

import pytest

from rpi_photobooth import state_screensaver

@pytest.fixture
def state():
    return state_screensaver.ScreenSaverState()


def test_initial_state(state):
    """Sample pytest test function with the pytest fixture as an argument.
    """
    assert state.Activated == False
