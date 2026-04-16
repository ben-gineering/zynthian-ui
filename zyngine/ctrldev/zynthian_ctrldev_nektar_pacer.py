#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ******************************************************************************
# ZYNTHIAN PROJECT: Zynthian Control Device Driver
#
# Zynthian Control Device Driver for "Nektar Pacer"
#
# Copyright (C) 2015-2025 Fernando Moyano <jofemodo@zynthian.org>
#                         Brian Walton <brian@riban.co.uk>
#
# ******************************************************************************
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of
# the License, or any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# For a full copy of the GNU General Public License see the LICENSE.txt file.
#
# ******************************************************************************

import logging

# Zynthian specific modules
from zynlibs.zynseq import zynseq
from zyncoder.zyncore import lib_zyncore
from zyngine.ctrldev.zynthian_ctrldev_base import zynthian_ctrldev_zynpad

# ------------------------------------------------------------------------------------------------------------------
# Nektar Pacer
# ------------------------------------------------------------------------------------------------------------------


class zynthian_ctrldev_nektar_pacer(zynthian_ctrldev_zynpad):

    dev_ids = ["PACER IN 1"]
    driver_name = "Nektar Pacer"
    driver_description = "Phrase launcher (notes 52, 54, 56 for rows A-C)"

    _note_to_row = {52: 0, 54: 1, 56: 2}

    def init(self):
        self.cols = 0
        self.rows = 3
        super().init()

    def update_pad(self, row, col, pad_info):
        pass

    def midi_event(self, ev):
        evtype = (ev[0] >> 4) & 0x0F
        if evtype == 0x9:
            note = ev[1] & 0x7F
            vel = ev[2] & 0x7F
            if vel > 0:
                row = self._note_to_row.get(note)
                if row is not None and row < self.rows:
                    phrase = row + self.scroll_v
                    try:
                        self.zynseq.libseq.togglePlayState(self.zynseq.scene, phrase, zynseq.PHRASE_CHANNEL)
                    except:
                        pass
            return True
        elif ev[0] == 0xF0:
            logging.info(f"Pacer received SysEx => {ev.hex(' ')}")
            return True

    def light_off(self):
        pass

    def sleep_on(self):
        pass

    def sleep_off(self):
        pass

# ------------------------------------------------------------------------------
