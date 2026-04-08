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
    driver_name = "Nektar Pacer"
    driver_description = "Clip launcher (factory preset A5: FS1=note 52, FS2=note 54)"

    # Note numbers from factory preset A5 (E minor scale notes)
    # FS1=52(E3), FS2=54(F#3), FS3=55(G3), FS4=57(A3), FS5=59(B3), FS6=60(C4)
    # Currently testing with FS1 and FS2 only
    _note_to_col = {52: 0, 54: 1}

    def init(self):
        self.cols = 2
        self.rows = 1
        self._recording = {}
        super().init()

    def _col_to_note(self, col):
        return 52 + (col * 2)

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
            note = self._col_to_note(col)
            lib_zyncore.dev_send_note_on(self.idev_out, midi_chan, note, velocity)

    def midi_event(self, ev):
        evtype = (ev[0] >> 4) & 0x0F
        if evtype == 0x9:
            note = ev[1] & 0x7F
            vel = ev[2] & 0x7F
            if vel > 0:
                col = self._note_to_col.get(note)
                if col is not None and col < self.cols:
                    row = 0
                    phrase = row + self.scroll_v
                    midi_chan = self.get_filtered_midi_chan_by_index(col)
                    if midi_chan is not None:
                        try:
                            if self._toggle_clip_record(phrase, midi_chan, col):
                                return True
                            self.zynseq.libseq.togglePlayState(self.zynseq.scene, phrase, midi_chan)
                        except:
                            pass
            return True
        elif ev[0] == 0xF0:
            logging.info(f"Pacer received SysEx => {ev.hex(' ')}")
            return True

    def _toggle_clip_record(self, phrase, midi_chan, col):
        pated = zynthian_gui_config.zyngui.screens.get("pattern_editor")
        if pated is None:
            return False

        pattern = self.zynseq.libseq.getPattern(self.zynseq.scene, phrase, midi_chan, 0, 0)
        if pattern < 0:
            return False

        is_recording = self._recording.get(col, False)
        if is_recording:
            pated.toggle_midi_record(False)
            self._recording[col] = False
            return True

        if not self.zynseq.libseq.isEmpty(self.zynseq.scene, phrase, midi_chan):
            return False

        pated.phrase = phrase
        pated.sequence = midi_chan
        pated.channel = midi_chan
        pated.load_pattern(pattern)
        if not self.zynseq.libseq.selectSequence(self.zynseq.scene, phrase, midi_chan):
            return False
        pated.toggle_midi_record(True)
        self.zynseq.libseq.setPlayState(self.zynseq.scene, phrase, midi_chan, zynseq.SEQ_STARTING)
        self._recording[col] = True
        return True

    def light_off(self):
        for col in range(self.cols):
            note = self._col_to_note(col)
            lib_zyncore.dev_send_note_on(self.idev_out, 0, note, 0)

    def sleep_on(self):
        pass

    def sleep_off(self):
        pass

# ------------------------------------------------------------------------------
