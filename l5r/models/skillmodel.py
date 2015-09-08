# -*- coding: utf-8 -*-
# Copyright (C) 2014 Daniele Simonetti
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

from PySide import QtGui, QtCore


import api.rules
import api.data
import api.data.skills
import api.character.skills
from util import log


class SkillItemModel(object):

    def __init__(self):
        self.name = ''
        self.rank = ''
        self.trait = ''
        self.base_roll = ''
        self.mod_roll = ''
        self.is_school = False
        self.emph = []
        self.skill_id = 0

    def __str__(self):
        return self.name


class SkillTableViewModel(QtCore.QAbstractTableModel):

    def __init__(self, parent=None):
        super(SkillTableViewModel, self).__init__(parent)
        self.items = []
        self.headers = ['Name', 'Rank', 'Trait', 'Base Roll', 'Mod Roll', 'Emphases']
        self.text_color = QtGui.QBrush(QtGui.QColor(0x15, 0x15, 0x15))
        self.bg_color = [QtGui.QBrush(QtGui.QColor(0xFF, 0xEB, 0x82)),
                         QtGui.QBrush(QtGui.QColor(0xEB, 0xFF, 0x82))]
        self.item_size = QtCore.QSize(28, 28)
        if parent:
            self.bold_font = parent.font()
            self.bold_font.setBold(True)

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.items)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.headers)

    def headerData(self, section, orientation, role=QtCore.Qt.ItemDataRole.DisplayRole):
        if orientation != QtCore.Qt.Orientation.Horizontal:
            return None
        if role == QtCore.Qt.DisplayRole:
            return self.headers[section]
        return None

    def data(self, index, role=QtCore.Qt.UserRole):
        if not index.isValid() or index.row() >= len(self.items):
            return None
        item = self.items[index.row()]
        if role == QtCore.Qt.DisplayRole:
            if index.column() == 0:
                return item.name
            if index.column() == 1:
                return item.rank
            if index.column() == 2:
                return item.trait
            if index.column() == 3:
                return str(item.base_roll)
            if index.column() == 4:
                return str(item.mod_roll)
            if index.column() == 5:
                return ', '.join(map(str,item.emph))
        elif role == QtCore.Qt.FontRole:
            if item.is_school and self.bold_font:
                return self.bold_font
        elif role == QtCore.Qt.ForegroundRole:
            return self.text_color
        elif role == QtCore.Qt.BackgroundRole:
            return self.bg_color[index.row() % 2]
        elif role == QtCore.Qt.SizeHintRole:
            return self.item_size
        elif role == QtCore.Qt.UserRole:
            return item.skill_id
        return None

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsDropEnabled
        flags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        return flags

    def add_item(self, item):
        row = self.rowCount()
        self.beginInsertRows(QtCore.QModelIndex(), row, row)
        self.items.append(item)
        self.endInsertRows()

    def clean(self):
        self.beginResetModel()
        self.items = []
        self.endResetModel()

    def build_item_model(self, sk):
        itm = SkillItemModel()
        itm.skill_id = sk.id
        itm.name = sk.name

        trait = api.data.get_trait_or_ring(sk.trait)

        if trait:
            itm.trait = trait.text
        else:
            itm.trait = sk.trait

        return itm

    def update_from_model(self, model):

        self.clean()
        for s in api.character.skills.get_all():

            sk = api.data.skills.get(s)

            if not sk:
                log.model.error(u"skill not found: %s", s)
                continue

            itm = self.build_item_model(sk)
            itm.rank = api.character.skills.get_skill_rank(s)
            itm.emph = api.character.skills.get_skill_emphases(s)
            itm.base_roll = api.rules.calculate_base_skill_roll(model, sk)
            itm.mod_roll = api.rules.calculate_mod_skill_roll(model, sk)
            itm.is_school = api.character.skills.is_starter(s)
            self.add_item(itm)
