import math
import fnmatch
from pathlib import Path
from typing import Iterable, List

import mobase

from ..basic_game import BasicGame
from ..basic_features import BasicModDataChecker, GlobPatterns
from ..basic_features.utils import is_directory

class UEGameModDataChecker(BasicModDataChecker):
    ue_game_dir:str
    def __init__(self, dir_name:str):
        super().__init__(
            GlobPatterns(
                move={
                    "content": dir_name + "/",
                    "paks": dir_name + "/Content/",
                    "~mods": dir_name + "/Content/Paks/",
                    "root": dir_name + "/Content/Paks/~mods/",
                    "**.pak": dir_name + "/Content/Paks/~mods/",
                    "**.ucas": dir_name + "/Content/Paks/~mods/",
                    "**.utoc": dir_name + "/Content/Paks/~mods/",
                },
                delete=[
                    "icon.png",
                    "screenshot.png",
                    "screenshot.jpg",
                ],
                valid = [
                    dir_name,
                    "root",
                ],
            )
        )
        self.ue_game_dir = dir_name
    
    def has_pak(self, filetree:mobase.IFileTree) -> bool:
        for entry in filetree:
            if not is_directory(entry) and entry.name().casefold().endswith(".pak"):
                return True
        return False
    
    def is_need_fix(self, filetree:mobase.IFileTree) -> bool:
        for entry in filetree:
            if is_directory(entry) :
                if self.has_pak(entry):
                    lname = entry.name().lower()
                    if (lname == "logicmods" or lname == "~mods"):
                        return False
                    else:
                        return True
                else:
                    return self.is_need_fix(entry)
        return False
    
    def fix_pak_path(self, root:mobase.IFileTree, filetree:mobase.IFileTree):
        for entry in list(filetree):
            if is_directory(entry) : #Eve-UltimateBunny Helmet and Necklace
                if self.has_pak(entry):
                    lname = entry.name().lower()
                    if (lname != "logicmods" and lname != "~mods"):
                        # 下面文件夹复制到指定位置
                        for subfile in list(entry):
                            if not is_directory(subfile):
                                root.move(subfile, entry.path() + "/"+ self.ue_game_dir + "/Content/Paks/~mods/")
                        #entry.detach()
                else:
                    self.fix_pak_path(root, entry)

    def dataLooksValid(
        self, filetree: mobase.IFileTree
    ) -> mobase.ModDataChecker.CheckReturn:
        check_return = super().dataLooksValid(filetree)
        if (check_return == self.INVALID and self.is_need_fix(filetree)):
            return self.FIXABLE
        return check_return

    def fix(self, filetree: mobase.IFileTree) -> mobase.IFileTree:
        filetree = super().fix(filetree)
        if is_directory(filetree) and self.is_need_fix(filetree):
            self.fix_pak_path(filetree, filetree)
        return filetree


class StellarBladeGame(BasicGame):
    Name = "Stellar Blade Support Plugin"
    Author = "Haibao666"
    Version = "1.0.0"

    GameName = "Stellar Blade"
    GameShortName = "stellarblade"
    GameNexusName = "stellarblade"
    GameSteamId = 3489700
    GameBinary = "SB/Binaries/Win64/SB-Win64-Shipping.exe"
    GameDataPath = "%GAME_PATH%"
    GameSavesDirectory = "%DOCUMENTS%/StellarBlade"
    GameSaveExtension = "sav"
    
    def init(self, organizer: mobase.IOrganizer) -> bool:
        super().init(organizer)
        self._register_feature(UEGameModDataChecker("SB"))
        return True
