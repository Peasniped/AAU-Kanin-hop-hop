# -*- coding: utf-8 -*-
"""
'Kanin Hop Hop'-brætspil - spil.py
@author: Morten Zink Stage
https://github.com/Peasniped/Kanin-hop-hop

Created on Mon Nov 4 2022
"""

from random import randint

class spilInstans:
    """
    Spawner én instans af spillet
    """
    def __init__(self, spillerantal, spiltype):
        """
        Startindstillinger til en spilinstans
        """
        self.kaniner = 5 # Hvor mange kaniner der skal være på spillepladen til at starte med
        self.huller = {"rød":0, "gul":0, "grøn":0, "blå":0, "lilla":0}
        self.spiller = 1
        self.spillerantal = int(spillerantal)
        self.spiltype = spiltype
        self.point = {}
        self.lastMessage = ""
        self.hvisTurErDet = ""
        self.kaninRetur = False
        self.antalKaninerMidte = self.kaniner
        self.turTæller = 0

        # Udfylder scoreboard(dictionary) med 0 point for hver spiller
        for i in range(self.spillerantal):
            self.point[i + 1] = 0
    
    def terningslag(self): # Indbygget i GUI
        """
        Slår med terningen og returnerer en farve/side
        """
        sider = ["blå", "grøn", "gul", "kanin", "lilla", "rød"]
        tal = randint(1,6)
        farve = sider[tal-1]
        return(farve)

    def tur(self, farve):
        """
        Gennemkører én tur i spillet input er terningslag()
        """ 
        self.ekstraTur = False

        if farve == "kanin":
            if self.spiltype == "hurtig": # -> kanin = +1 point + slå igen
                if self.antalKaninerMidte >= 1:
                    self.point[self.spiller] += 1
                    self.kaniner -= 1
                    self.lastMessage = (f"Spiller {self.spiller} har reddet en kanin: +1 point - Spiller {self.spiller} har nu {self.point[self.spiller]} point")
                    self.antalKaninerMidte -= 1
                self.ekstraTur = True

            elif self.spiltype == "normal": # -> kanin = +1 point 
                if self.antalKaninerMidte >= 1:
                    self.point[self.spiller] += 1
                    self.kaniner -= 1
                    self.lastMessage = (f"Spiller {self.spiller} har reddet en kanin: +1 point - Spiller {self.spiller} har nu {self.point[self.spiller]} point")
                    self.antalKaninerMidte -= 1

            elif self.spiltype == "langsom": # -> kanin = returner kanin til hul
                if self.point[self.spiller] > 0:
                    self.point[self.spiller] -= 1
                    self.kaniner += 1
                    self.kaninRetur = True
                    self.lastMessage = (f"Spiller {self.spiller} har mistet en kanin til midten: -1 point - Spiller {self.spiller} har nu {self.point[self.spiller]} point")
                    self.antalKaninerMidte += 1
                else:
                    self.lastMessage = (f"Spiller {self.spiller} har ingen kaniner at miste. Tur slut")
  
        elif self.huller[farve] == 0:
            if self.antalKaninerMidte >= 1:
                self.huller[farve] = 1
                self.lastMessage = (f"{farve.capitalize()} er tom, kanin er flyttet hertil")
                self.antalKaninerMidte -= 1

        elif self.huller[farve] == 1:
            self.point[self.spiller] += 1
            self.kaniner -= 1
            self.huller[farve] = 0
            self.lastMessage = (f"Kaninen i {farve} er reddet - Spiller {self.spiller}: +1 point - Spiller {self.spiller} har nu {self.point[self.spiller]} point")

        if self.ekstraTur == False:
            if self.spiller < self.spillerantal:
                self.spiller += 1 
            else:
                self.spiller = 1
            self.hvisTurErDet = (f"Det er Spiller {self.spiller}s tur til at slå!")
        else:
            self.hvisTurErDet = (f"Det er Spiller {self.spiller}s tur til at slå igen!")
        self.turTæller += 1
    
    def getPoint(self):
        pointTabel = []
        for spiller in self.point:
            pointTabel.append(self.point[spiller])
        return pointTabel

    def getVinder(self):
        """
        Returnerer nummeret på den spiller som har flest point.
        Hvis to spillere har det samme pointantal returnerer den (desværre) den spiller med det laveste spillernummer
        """
        return(max(self.point, key=self.point.get))