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
from zyngui import zynthian_gui_config

# ------------------------------------------------------------------------------------------------------------------
# Nektar Pacer
# ------------------------------------------------------------------------------------------------------------------


class zynthian_ctrldev_nektar_pacer(zynthian_ctrldev_zynpad):

    dev_ids = ["PACER IN 1"]
    driver_description = "Clip launcher (2-switch initial test)"

    def init(self):
        self.cols = 2
        self.rows = 1
        super().init()

    def update_pad(self, row, col, pad_info):
        midi_chan = 0
        velocity = 0
        try:
            state = pad_info["state"]
            if state == zynseq.SEQ_STOPPED:
                if not pad_info["empty"]:
                    velocity = 64
            elif state in (zynseq.SEQ_PLAYING, zynseq.SEQ_CHILD_PLAYING):
                velocity = 127
            elif state in (zynseq.SEQ_STOPPING, zynseq.SEQ_STOPPING_SYNC, zynseq.SEQ_FORCED_STOP, zynseq.SEQ_CHILD_STOPPING):
                velocity = 96
            elif state == zynseq.SEQ_STARTING:
                velocity = 96
        except:
            pass

        if col < self.cols:
            note = 36 + col
            lib_zyncore.dev_send_note_on(self.idev_out, midi_chan, note, velocity)

    def midi_event(self, ev):
        evtype = (ev[0] >> 4) & 0x0F
        if evtype == 0x9:
            note = ev[1] & 0x7F
            vel = ev[2] & 0x7F
            if vel > 0:
                col = note - 36
                if 0 <= col < self.cols:
                    row = 0
                    phrase = row + self.scroll_v
                    midi_chan = self.get_filtered_midi_chan_by_index(col)
                    if midi_chan is not None:
                        try:
                            self.zynseq.libseq.togglePlayState(self.zynseq.scene, phrase, midi_chan)
                        except:
                            pass
            return True
        elif ev[0] == 0xF0:
            logging.info(f"Pacer received SysEx => {ev.hex(' ')}")
            return True

    def light_off(self):
        for col in range(self.cols):
            note = 36 + col
            lib_zyncore.dev_send_note_on(self.idev_out, 0, note, 0)

    def sleep_on(self):
        pass

    def sleep_off(self):
        pass

# ------------------------------------------------------------------------------
