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
    def __init__(self, spillerantal, spiltype, kaninAntal):
        """
        Startindstillinger til en spilinstans
        """
        self.kaniner = int(kaninAntal)   # Hvor mange kaniner der skal være på spillepladen til at starte med
        self.huller = {"rød":0, "gul":0, "grøn":0, "blå":0, "lilla":0}
        self.spiller = 1            # Spiller 1 starter
        self.spillerantal = int(spillerantal) # Spillerantal indlæses fra parameter
        self.spiltype = spiltype    # Spiltype indlæses fra parameter
        self.point = {}             # Pointtabel laves/ryddes
        self.lastMessage = ""       # Besked som sendes videre til GUI
        self.hvisTurErDet = ""      # Besked som sendes videre til GUI
        self.kaninRetur = False     # Spilleren skal aflevere en kanin til midten
        self.antalKaninerMidte = self.kaniner # Ved spilstart er antallet af kaniner i midten = antallet af kaniner i alt
        self.turTæller = 0          # Tæller, hvor mange ture der er gennemløbet

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
        self.ekstraTur = False      # Rydder ekstraTur-flag

        if farve == "kanin":
            # Der er slået kanin i hurtigt spil => +1 point + slå igen
            if self.spiltype == "hurtig": 
                if self.antalKaninerMidte >= 1:
                    self.point[self.spiller] += 1
                    self.kaniner -= 1
                    self.lastMessage = (f"Spiller {self.spiller} har reddet en kanin: +1 point - Spiller {self.spiller} har nu {self.point[self.spiller]} point")
                    self.antalKaninerMidte -= 1
                self.ekstraTur = True

            # Der er slået kanin i normalt spil => +1 point
            elif self.spiltype == "normal":
                if self.antalKaninerMidte >= 1:
                    self.point[self.spiller] += 1
                    self.kaniner -= 1
                    self.lastMessage = (f"Spiller {self.spiller} har reddet en kanin: +1 point - Spiller {self.spiller} har nu {self.point[self.spiller]} point")
                    self.antalKaninerMidte -= 1

            # Der er slået kanin i langsomt spil => -1 point og kanin retur til midten
            elif self.spiltype == "langsom":
                if self.point[self.spiller] > 0:
                    self.point[self.spiller] -= 1
                    self.kaniner += 1
                    self.kaninRetur = True
                    self.lastMessage = (f"Spiller {self.spiller} har mistet en kanin til midten: -1 point - Spiller {self.spiller} har nu {self.point[self.spiller]} point")
                    self.antalKaninerMidte += 1
                else:
                    self.lastMessage = (f"Spiller {self.spiller} har ingen kaniner at miste. Tur slut")
  
        # Hullet som passer til terningens farve et tomt => kanin flyttes i hul
        elif self.huller[farve] == 0:
            if self.antalKaninerMidte >= 1:
                self.huller[farve] = 1
                self.lastMessage = (f"{farve.capitalize()} er tom, kanin er flyttet hertil")
                self.antalKaninerMidte -= 1

        # Hullet som passer til terningens farve et fyldt => kanin flyttes ud og spiller får point
        elif self.huller[farve] == 1:
            self.point[self.spiller] += 1
            self.kaniner -= 1
            self.huller[farve] = 0
            self.lastMessage = (f"Kaninen i {farve} er reddet - Spiller {self.spiller}: +1 point - Spiller {self.spiller} har nu {self.point[self.spiller]} point")

        # Hvis ikke spilleren skal have en ekstra tur, går turen videre til næste spiller
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
        """
        Returnerer en liste med alle spilleres nuværende point
        """        
        pointTabel = []
        for spiller in self.point:
            pointTabel.append(self.point[spiller])
        return pointTabel

    def getVinder(self):
        """
        Returnerer en liste med nummeret de spillere som har flest point lige nu.
        """
        # Find værdien af den første key med den højeste værdi
        maxPoint = self.point[max(self.point, key=self.point.get)]
        
        # Lav ListComprehension for alle keys med samme værdi som maxPoint
        keyOnes = []

        for each in self.point:
            if self.point[each] == maxPoint:
                keyOnes.append(each)
        return(keyOnes)