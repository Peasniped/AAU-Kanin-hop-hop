# -*- coding: utf-8 -*-
"""
'Kanin Hop Hop'-brætspil - main.py
@author: Morten Zink Stage
https://github.com/Peasniped/Kanin-hop-hop

Created on Mon Nov 4 2022
"""

import PySimpleGUI as sg
import matplotlib 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from io import BytesIO
from random import randint
from time import sleep
import spil
matplotlib.use("TkAgg")

# TODO-Liste: -------------------------------------------------------
#
# FIXME BUG: Progressbar virker ikke rigtigt. Hvis man simulerer 100k spil så bliver progress bar færdig alt for hurtig.
#	^ Det er fordi at matematikken ikke er med i progressbar, kun gennemløb af spillene - der skal gøres så progress bar mangler måske 10%, når den er færdig med at gennemløbe spillene ^
#
# TODO Feature: Slider til at vælge antal af kaniner
# TODO Feature: Der skal laves en besked i slutningen af enkeltSpil, hvor der står noget a la: "Det er en tragisk dag, hvor vi siger farvel til de {døde} modige kaniner som ikke blev reddet op af ingangshullerne."
# TODO Feature: Oprettelse af skaleringsvariabel som bare ligger i toppen som (global) variabel.
# TODO Feature: Der skal stå på scorebord hvem der har vundet. Hvis flere spillere har samme point skal alle navne stå der.
#				Der kan evt laves en funktion erVinder(spiller) som ser om spilleren har flest point eller har samme antal point som den med flest point. Return er fx farven som spillerens navn skrives med på scoreboard. 
#
# -------------------------------------------------------------------

# Højde og bredde i pixels af billederne der bruges som baggrund
height = 800
width = 800

# Obligatorisk dark mode B)
sg.theme('Dark') 

def importBillede(billedsti):
	"""
	Indlæser et billede i en variabel
	"""
	billede = Image.open(billedsti)
	with BytesIO() as output:
		billede.save(output, format="PNG")
		return output.getvalue()

def placerKanin(x,y):
	"""
	Input koordinat for hvor du gerne vil have midten af bunden af kanin
	returnerer reviderede xy-koordinater
	"""
	imgWidth = 75
	imgHeight = 150
	newX = x - imgWidth/2
	newY = y + imgHeight
	return(newX, newY)

def matematik(vindertabel, gennemløb, spiller):
	"""
	Omregner med hver turs vinder til en tabel med frekvensen for hvor ofte den givne spiller har vundet
	Dette beregnes for hvert spillet spil og vi kommer derfor tættere og tættere på den sande sandsynlighed jo flere spil der gennemløbes
	"""
	frekvenstabel = []
	
	for i in range(1,int(gennemløb)):
		tabel = vindertabel[:i]
		vinderfrekvens = (tabel.count(spiller) / i ) * 100
		frekvenstabel.append(vinderfrekvens)
	return np.array(frekvenstabel)

def lavGraf(gennemløb, spillerantal, yMax, yMin, ft1, ft2, ft3=None, ft4=None, ft5=None, ft6=None, ft7=None, ft8=None):

	x = np.linspace(0,int(gennemløb),len(ft1))
		
	fig, ax = plt.subplots()
	ax.plot(x,ft1, label='Spiller 1')
	ax.plot(x,ft2, label='Spiller 2')

	if spillerantal >= 3:
		ax.plot(x,ft3, label='Spiller 3')
	if spillerantal >= 4:
		ax.plot(x,ft4, label='Spiller 4')
	if spillerantal >= 5:
		ax.plot(x,ft5, label='Spiller 5')
	if spillerantal >= 6:
		ax.plot(x,ft6, label='Spiller 6')
	if spillerantal >= 7:
		ax.plot(x,ft7, label='Spiller 7')
	if spillerantal >= 8:
		ax.plot(x,ft8, label='Spiller 8')
	
	plt.ylim(yMin,yMax)
	plt.xlabel('Antal Spil')
	plt.ylabel('Vinderfrekvens i %')
	plt.legend()

	return(fig)
	
def tegnGraf(canvas, figur):
	figure_canvas_agg = FigureCanvasTkAgg(figur, canvas)
	figure_canvas_agg.draw()
	figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
	return figure_canvas_agg

def sletGraf(fig):
    """
    Deletes figure from plot
    """
    fig.get_tk_widget().forget()
    plt.close('all')

# Spillets billeder indlæses
billedeForside = importBillede('Kaninhop-forside.png')
billedeSpilleplade = importBillede('Kaninhop-spilleplade.png')
billedekanin = importBillede('Kanin.png')
billedekanin2 = importBillede('Kanin2.png')
billedeTerningSlå = importBillede('terning-slå.png')
billedeTerningBlå = importBillede('terning-blå.png')
billedeTerningGrøn = importBillede('terning-grøn.png')
billedeTerningGul = importBillede('terning-gul.png')
billedeTerningKanin = importBillede('terning-kanin.png')
billedeTerningLilla = importBillede('terning-lilla.png')
billedeTerningRød = importBillede('terning-rød.png')
billedeSlutBesked = importBillede('slutbesked.png')
billedePodium = importBillede('podium.png')

# Forsidevinduets layout
layoutForside = [[sg.Graph((height,width), graph_bottom_left= (0,0), 
					graph_top_right=(height,width),
					background_color = 'white',
					key = '-graph-forside-',
					enable_events = True)],]

# Layout for menu til enkelt spil
layoutMenuEnkelt = [[sg.Text('Vælg dine indstillinger og tryk start for at komme i gang!')],
					[sg.Text('Spiltype', font=('Helvetica', 15), justification='left')],
					[sg.Radio('Hurtig', 'spiltype', key = '-spiltype-hurtig-', size=(12, 1)), sg.Radio('Normal', 'spiltype', key = '-spiltype-normal-', default=True, size=(12, 1)), sg.Radio('Langsom', 'spiltype', key = '-spiltype-langsom-', size=(12, 1)),],
			  
					[sg.Text('Antal Spillere', font=('Helvetica', 15), justification='left')],
					[sg.Slider((2,8), 4, orientation = 'h', size=(45,20), key ='-antal-spillere-')],

					[sg.Button('Start spil!', key = '-knap-menuenkelt-start-', button_color=('white', 'green')),],]

# Layout for menu til simulerede spil
layoutMenuMangeIndstillinger = [[sg.Text('Vælg dine indstillinger og tryk start for at komme i gang!')],
					[sg.Text('Spiltype', font=('Helvetica', 15), justification='left')],
					[sg.Radio('Hurtig', 'spiltype', key = '-spiltype-hurtig-', size=(12, 1)), sg.Radio('Normal', 'spiltype', key = '-spiltype-normal-', default=True, size=(12, 1)), sg.Radio('Langsom', 'spiltype', key = '-spiltype-langsom-', size=(12, 1)),],
			  
					[sg.Text('Antal Spillere', font=('Helvetica', 15), justification='left')],
					[sg.Slider((2,8), 4, orientation = 'h', size=(45,20), key ='-antal-spillere-')],

					[sg.Text('Antal Gennemspilninger (n)', font=('Helvetica', 15), justification='left')],
					[sg.Slider((100,10000), 1000, orientation = 'h', size=(45,20), resolution=100, key ='-antal-gennemspil-')],
					[sg.Text('Øvre grænseværdi for y-akse (yMax)', font=('Helvetica', 15), justification='left')],
					[sg.Slider((10,100), 50, orientation = 'h', enable_events = True, size=(45,20), key ='-yMax-')],
					[sg.Text('Nedre grænseværdi for y-akse (yMin)', font=('Helvetica', 15), justification='left')],
					[sg.Slider((0,90), 10, orientation = 'h', enable_events = True, size=(45,20), key ='-yMin-')],					

					[sg.Text('')],
					[sg.Button('Simuler spil!', key = '-knap-menumange-start-', button_color=('white', 'green')),],
					[sg.ProgressBar(100, orientation = 'h', key = '-progress-bar-', size=(37,20), bar_color = ("green", "grey")),],
					[sg.Text('Vindersandsynlighed ved n spil:', font=('Helvetica', 12, "bold"), justification='left')],
					[sg.Text('', key='-besked-vindsans-', font=('Helvetica', 10, "bold"), justification='left')],]
layoutMenuMangeGraf = [[sg.Canvas(key = '-graf-')],]

layoutMenuMange = [
	[sg.Column(layoutMenuMangeIndstillinger),
     sg.VSeperator(),
     sg.Column(layoutMenuMangeGraf),]]

# Layout for enkelt spil
layoutSpilEnkelt = [
		[sg.Graph((height,width), graph_bottom_left= (0,0), 
					graph_top_right=(height,width),
					background_color = 'white',
					key = '-graph-spilEnkelt-',
					enable_events = True)],
		[sg.Text('Slå med terningen for at komme igang!', key='-besked-spilenkelt-', font=('Helvetica', 12), justification='left')],
		[sg.Text('Velkommen til spillet - Spiller 1 starter!', key='-besked-hvisTurErDet-', font=('Helvetica', 18, "bold"), justification='left')],]

# Layout for scoreboard til enkelt spil
layoutScoreboard = [[sg.Graph((height,width), graph_bottom_left= (0,0), 
			graph_top_right=(height,width),
			background_color = 'white',
			key = '-graph-scoreboard-',
			enable_events = True)],]
	
def forside_Vindue():
	"""
	Danner vindue og kører events for forsiden
	"""

	forside = sg.Window('Kanin Hop Hop Forside', layout = layoutForside,finalize = True)
	forsideOpen = True

	forside['-graph-forside-'].draw_image(data=billedeForside, location=(0, height))

	while forsideOpen == True:
		event,values = forside.read()

		if event == '-graph-forside-':
			pos = values['-graph-forside-']

			if 65 < pos[0] < 350 and 50 < pos[1] < 130:
				forsideOpen = False
				forside.close()
				menuEnkelt_Vindue()
    
			if 450 < pos[0] < 735 and 50 < pos[1] < 130:
				forsideOpen = False
				forside.close()
				menuMange_Vindue()
        
		if event == sg.WIN_CLOSED:
			forsideOpen = False
	
	forside.close()

def menuEnkelt_Vindue():
	"""
	Danner vindue og kører events for menuen til enkeltspil
	"""
	menuEnkelt = sg.Window('Enkelt Spil Menu', layout = layoutMenuEnkelt, finalize = True)
	menuEnkeltOpen = True
	
	while menuEnkeltOpen == True:
		event,values = menuEnkelt.read()

		# Sæt spiltype
		if values['-spiltype-langsom-'] == True:
			spiltype = "langsom"
		elif values['-spiltype-normal-'] == True:
			spiltype = "normal"
		elif values['-spiltype-hurtig-'] == True:
			spiltype = "hurtig"

		# Sæt antal spillere
		spillerantal = values['-antal-spillere-']

		if event == '-knap-menuenkelt-start-':
			menuEnkelt.close()
			spilEnkelt_Vindue(spiltype, spillerantal)
			menuEnkeltOpen = False

		if event == sg.WIN_CLOSED:
			menuEnkeltOpen = False
	menuEnkelt.close()        

def spilEnkelt_Vindue(spiltype, spillerantal):
	"""
	Danner vindue og kører events for spilvinduet til enkeltspil
	"""	
	spilEnkelt = sg.Window('Enkelt Spil Menu', layout = layoutSpilEnkelt, finalize = True)
	spilEnkeltOpen = True

	# Spilinstans oprettes fra class
	enkeltSpil = spil.spilInstans(spillerantal=spillerantal, spiltype=spiltype)

	kaninerMidte = []
	kaninType = {}
	kaninIHul = {"blå":"", "grøn":"", "gul":"", "lilla":"", "rød":""}

	spilEnkelt['-graph-spilEnkelt-'].draw_image(data=billedeSpilleplade, location=(0, height))
	spilEnkelt['-graph-spilEnkelt-'].draw_image(data=billedeTerningSlå, location=(width - 115, 115))

	slutBeskedFremme = False
	
	# Tegn 20 kaniner i midten
	for i in range(enkeltSpil.kaniner):
		if randint(1,5) == 5: 
			# 20% chance for at tegne en speciel kanin
			kaninID = spilEnkelt['-graph-spilEnkelt-'].draw_image(data=billedekanin2, location=(380 + randint(-120,120), 520 + randint(-115,115)))
			kaninType[kaninID] = "lenny"
			kaninerMidte.append(kaninID)
		else:
			kaninID = spilEnkelt['-graph-spilEnkelt-'].draw_image(data=billedekanin, location=(380 + randint(-120,120), 520 + randint(-115,115)))
			kaninType[kaninID] = "normal"
			kaninerMidte.append(kaninID)
	
	while spilEnkeltOpen == True:
		event,values = spilEnkelt.read()
		
		enkeltSpil.kaninRetur = False

		if event == '-graph-spilEnkelt-':
			pos = values['-graph-spilEnkelt-']

			### Slå med terningen -----------------------------
			if 685 < pos[0] < 790 and 18 < pos[1] < 120 and slutBeskedFremme == False:
				sleep(0.15)
				for i in range(randint(10,18)): # Terningen slår et tilfældigt antal gange (mellem 10 og 18)
					farve = enkeltSpil.terningslag()

					if farve == "blå":
						spilEnkelt['-graph-spilEnkelt-'].draw_image(data=billedeTerningBlå, location=(width - 115, 115))
						spilEnkelt.refresh()
					elif farve == "grøn":
						spilEnkelt['-graph-spilEnkelt-'].draw_image(data=billedeTerningGrøn, location=(width - 115, 115))
						spilEnkelt.refresh()
					elif farve == "gul":
						spilEnkelt['-graph-spilEnkelt-'].draw_image(data=billedeTerningGul, location=(width - 115, 115))
						spilEnkelt.refresh()
					elif farve =="kanin":
						spilEnkelt['-graph-spilEnkelt-'].draw_image(data=billedeTerningKanin, location=(width - 115, 115))
						spilEnkelt.refresh()
					elif farve == "lilla":
						spilEnkelt['-graph-spilEnkelt-'].draw_image(data=billedeTerningLilla, location=(width - 115, 115))
						spilEnkelt.refresh()
					elif farve == "rød":
						spilEnkelt['-graph-spilEnkelt-'].draw_image(data=billedeTerningRød, location=(width - 115, 115))
						spilEnkelt.refresh()
					sleep(0.06)
				### -----------------------------------------------

				# Den nuværende tur bliver gennemkørt med den slåede farve
				sleep(0.5)
				enkeltSpil.tur(farve)
				
				### Placer kanin i bestemt hul -------------------- #Selverkendelse: Det er fjollet, at denne snippet og enkeltSpil.tur() begge regner på hvad der skal ske.
				
				# Flyt kanin til Blåt hul	
				if enkeltSpil.huller["blå"] == 1 and kaninIHul["blå"] == "" and farve == "blå":
					selectKanin = kaninerMidte[-1]
					kaninerMidte.remove(selectKanin)

					if kaninType[selectKanin] == "lenny": 
						kaninID = spilEnkelt['-graph-spilEnkelt-'].draw_image(data=billedekanin2, location=placerKanin(300, 132))
						spilEnkelt['-graph-spilEnkelt-'].delete_figure(selectKanin)
					else:
						kaninID = spilEnkelt['-graph-spilEnkelt-'].draw_image(data=billedekanin, location=placerKanin(300, 132))
						spilEnkelt['-graph-spilEnkelt-'].delete_figure(selectKanin)
					kaninIHul["blå"] = kaninID

				# Flyt kanin til Grønt hul
				elif enkeltSpil.huller["grøn"] == 1 and kaninIHul["grøn"] == "" and farve == "grøn":
					selectKanin = kaninerMidte[-1]
					kaninerMidte.remove(selectKanin)

					if kaninType[selectKanin] == "lenny": 
						kaninID = spilEnkelt['-graph-spilEnkelt-'].draw_image(data=billedekanin2, location=placerKanin(627, 182))
						spilEnkelt['-graph-spilEnkelt-'].delete_figure(selectKanin)
					else:
						kaninID = spilEnkelt['-graph-spilEnkelt-'].draw_image(data=billedekanin, location=placerKanin(627, 182))
						spilEnkelt['-graph-spilEnkelt-'].delete_figure(selectKanin)
					kaninIHul["grøn"] = kaninID

				# Flyt kanin til Gult hul
				elif enkeltSpil.huller["gul"] == 1 and kaninIHul["gul"] == "" and farve == "gul":
					selectKanin = kaninerMidte[-1]
					kaninerMidte.remove(selectKanin)

					if kaninType[selectKanin] == "lenny": 
						kaninID = spilEnkelt['-graph-spilEnkelt-'].draw_image(data=billedekanin2, location=placerKanin(330, 606))
						spilEnkelt['-graph-spilEnkelt-'].delete_figure(selectKanin)
					else:
						kaninID = spilEnkelt['-graph-spilEnkelt-'].draw_image(data=billedekanin, location=placerKanin(330, 606))
						spilEnkelt['-graph-spilEnkelt-'].delete_figure(selectKanin)
					kaninIHul["gul"] = kaninID			

				# Flyt kanin til Lilla hul
				elif enkeltSpil.huller["lilla"] == 1 and kaninIHul["lilla"] == "" and farve == "lilla":
					selectKanin = kaninerMidte[-1]
					kaninerMidte.remove(selectKanin)

					if kaninType[selectKanin] == "lenny": 
						kaninID = spilEnkelt['-graph-spilEnkelt-'].draw_image(data=billedekanin2, location=placerKanin(161, 340))
						spilEnkelt['-graph-spilEnkelt-'].delete_figure(selectKanin)
					else:
						kaninID = spilEnkelt['-graph-spilEnkelt-'].draw_image(data=billedekanin, location=placerKanin(161, 340))
						spilEnkelt['-graph-spilEnkelt-'].delete_figure(selectKanin)
					kaninIHul["lilla"] = kaninID

				# Flyt kanin til Rødt hul
				elif enkeltSpil.huller["rød"] == 1 and kaninIHul["rød"] == "" and farve == "rød":
					selectKanin = kaninerMidte[-1]
					kaninerMidte.remove(selectKanin)

					if kaninType[selectKanin] == "lenny": 
						kaninID = spilEnkelt['-graph-spilEnkelt-'].draw_image(data=billedekanin2, location=placerKanin(635, 562))
						spilEnkelt['-graph-spilEnkelt-'].delete_figure(selectKanin)
					else:
						kaninID = spilEnkelt['-graph-spilEnkelt-'].draw_image(data=billedekanin, location=placerKanin(635, 562))
						spilEnkelt['-graph-spilEnkelt-'].delete_figure(selectKanin)
					kaninIHul["rød"] = kaninID

				# Flyt kanin ud af hul
				elif farve != "kanin" and enkeltSpil.huller[farve] == 0 and kaninIHul[farve] != "":
					selectKanin = kaninIHul[farve]
					kaninIHul[farve] = ""
					spilEnkelt['-graph-spilEnkelt-'].delete_figure(selectKanin)
				
				# Flyt kanin ud af midte (der er slået kanin med spiltype = hurtig eller normal)
				elif enkeltSpil.spiltype == "hurtig" or enkeltSpil.spiltype == "normal":
					selectKanin = kaninerMidte[-1]
					kaninerMidte.remove(selectKanin)
					spilEnkelt['-graph-spilEnkelt-'].delete_figure(selectKanin)	

				if enkeltSpil.kaninRetur == True:
					if randint(1,5) == 5: 
						# 20% chance for at tegne en speciel kanin
						kaninID = spilEnkelt['-graph-spilEnkelt-'].draw_image(data=billedekanin2, location=(380 + randint(-120,120), 520 + randint(-115,115)))
						kaninType[kaninID] = "lenny"
						kaninerMidte.append(kaninID)
					else:
						kaninID = spilEnkelt['-graph-spilEnkelt-'].draw_image(data=billedekanin, location=(380 + randint(-120,120), 520 + randint(-115,115)))
						kaninType[kaninID] = "normal"
						kaninerMidte.append(kaninID)						
				### -----------------------------------------------					

		# Antal kaniner opdateres
		#enkeltSpil.antalKaninerMidte = len(kaninerMidte)

		# Informationer skrives til GUI'en
		spilEnkelt['-besked-spilenkelt-'].update(f"Sidste tur: {enkeltSpil.lastMessage}")
		spilEnkelt['-besked-hvisTurErDet-'].update(enkeltSpil.hvisTurErDet)

		print(f"Tur {enkeltSpil.turTæller} er færdig:")
		print("")
		print(f"Der er {enkeltSpil.antalKaninerMidte} kaniner tilbage i midten")
		print(f"Der er {enkeltSpil.kaniner} kaniner tilbage på spillepladen")

		# Hvis der ikke er flere kaniner tilbage stoppes spillet
		if enkeltSpil.antalKaninerMidte == 0:
			
			spilEnkelt['-besked-hvisTurErDet-'].update("Alle kaniner er ude af midten - Spillet er nu slut")
			sleep(1)

			# Slutbesked kommer op
			if slutBeskedFremme == False:
				spilEnkelt['-graph-spilEnkelt-'].draw_image(data=billedeSlutBesked, location=(0,height))
				slutBeskedFremme = True
			# Tryk på knappen "Til Scoreboard!"
			if 310 < pos[0] < 490 and 350 < pos[1] < 390:
				spilEnkelt.close()
				scoreboard_Vindue(spillerantal, enkeltSpil.getPoint())
				spilEnkeltOpen = False

		if event == sg.WIN_CLOSED:
			spilEnkeltOpen = False
	spilEnkelt.close()  

def scoreboard_Vindue(spillerAntal, pointliste):
	"""
	Denne funktion danner et vindue og tegner et scoreboard.

	ADVARSEL: Rigtig grim kode! Da jeg kom hertil, ville jeg bare gerne være færdig, så koden er ikke så flot C:
	"""
	scoreboard = sg.Window('Kanin Hop Hop Scoreboard', layout = layoutScoreboard,finalize = True)
	scoreboardOpen = True

	# Danner tabel afhængigt af spillerantal:
	if spillerAntal == 2:
		col1 = 1 * width/3
		col2 = 2 * width/3
	elif spillerAntal in [3,6]:
		col1 = 1 * width/4
		col2 = 2 * width/4
		col3 = 3 * width/4
	elif spillerAntal in [4,8]:
		col1 = 1 * width/5
		col2 = 2 * width/5
		col3 = 3 * width/5
		col4 = 4 * width/5
	elif spillerAntal in [5]:
		col1 = 1 * width/5
		col2 = 2 * width/5
		col3 = 3 * width/5
		col4 = 4 * width/5
		colCenter = width/2
	elif spillerAntal in [7]:
		col1 = 1 * width/5
		col2 = 2 * width/5
		col3 = 3 * width/5
		col4 = 4 * width/5
		colL1 = 1 * width/4
		colL2 = 2 * width/4
		colL3 = 3 * width/4

	scoreboard['-graph-scoreboard-'].draw_image(data=billedePodium, location=(0,height))

	# Scorebord 2 spillere
	if spillerAntal == 2: 
		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 1", font=('Helvetica', 20, 'bold'), location=(col1, 130))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[0]}", font=('Helvetica', 15), location=(col1, 100))

		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 2", font=('Helvetica', 20, 'bold'), location=(col2, 130))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[1]}", font=('Helvetica', 15), location=(col2, 100))

	# Scorebord 3 spillere
	if spillerAntal == 3:
		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 1", font=('Helvetica', 20, 'bold'), location=(col1, 130))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[0]}", font=('Helvetica', 15), location=(col1, 100))

		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 2", font=('Helvetica', 20, 'bold'), location=(col2, 130))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[1]}", font=('Helvetica', 15), location=(col2, 100))

		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 3", font=('Helvetica', 20, 'bold'), location=(col3, 130))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[2]}", font=('Helvetica', 15), location=(col3, 100))

	# Scorebord 4 spillere
	if spillerAntal == 4:
		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 1", font=('Helvetica', 20, 'bold'), location=(col1, 130))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[0]}", font=('Helvetica', 15), location=(col1, 100))

		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 2", font=('Helvetica', 20, 'bold'), location=(col2, 130))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[1]}", font=('Helvetica', 15), location=(col2, 100))

		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 3", font=('Helvetica', 20, 'bold'), location=(col3, 130))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[2]}", font=('Helvetica', 15), location=(col3, 100))

		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 4", font=('Helvetica', 20, 'bold'), location=(col4, 130))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[3]}", font=('Helvetica', 15), location=(col4, 100))

	# Scorebord 5 spillere
	if spillerAntal == 5:
		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 1", font=('Helvetica', 17, 'bold'), location=(col1, 165))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[0]}", font=('Helvetica', 12), location=(col1, 140))

		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 2", font=('Helvetica', 17, 'bold'), location=(col2, 165))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[1]}", font=('Helvetica', 12), location=(col2, 140))

		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 3", font=('Helvetica', 17, 'bold'), location=(col3, 165))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[2]}", font=('Helvetica', 12), location=(col3, 140))

		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 4", font=('Helvetica', 17, 'bold'), location=(col4, 165))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[3]}", font=('Helvetica', 12), location=(col4, 140))

		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 4", font=('Helvetica', 17, 'bold'), location=(colCenter, 110))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[3]}", font=('Helvetica', 12), location=(colCenter, 85))

	# Scorebord 6 spillere
	if spillerAntal == 6:
		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 1", font=('Helvetica', 17, 'bold'), location=(col1, 165))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[0]}", font=('Helvetica', 12), location=(col1, 140))

		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 2", font=('Helvetica', 17, 'bold'), location=(col2, 165))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[1]}", font=('Helvetica', 12), location=(col2, 140))

		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 3", font=('Helvetica', 17, 'bold'), location=(col3, 165))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[2]}", font=('Helvetica', 12), location=(col3, 140))

		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 4", font=('Helvetica', 17, 'bold'), location=(col1, 110))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[3]}", font=('Helvetica', 12), location=(col1, 85))

		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 5", font=('Helvetica', 17, 'bold'), location=(col2, 110))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[4]}", font=('Helvetica', 12), location=(col2, 85))

		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 6", font=('Helvetica', 17, 'bold'), location=(col3, 110))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[5]}", font=('Helvetica', 12), location=(col3, 85))
	
	# Scorebord 7 spillere
	if spillerAntal == 7:
		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 1", font=('Helvetica', 17, 'bold'), location=(col1, 165))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[0]}", font=('Helvetica', 12), location=(col1, 140))

		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 2", font=('Helvetica', 17, 'bold'), location=(col2, 165))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[1]}", font=('Helvetica', 12), location=(col2, 140))

		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 3", font=('Helvetica', 17, 'bold'), location=(col3, 165))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[2]}", font=('Helvetica', 12), location=(col3, 140))

		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 4", font=('Helvetica', 17, 'bold'), location=(col4, 165))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[3]}", font=('Helvetica', 12), location=(col4, 140))

		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 5", font=('Helvetica', 17, 'bold'), location=(colL1, 110))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[4]}", font=('Helvetica', 12), location=(colL1, 85))

		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 6", font=('Helvetica', 17, 'bold'), location=(colL2, 110))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[5]}", font=('Helvetica', 12), location=(colL2, 85))

		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 7", font=('Helvetica', 17, 'bold'), location=(colL3, 110))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[6]}", font=('Helvetica', 12), location=(colL3, 85))

	# Scorebord 8 spillere
	if spillerAntal == 8:
		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 1", font=('Helvetica', 17, 'bold'), location=(col1, 165))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[0]}", font=('Helvetica', 12), location=(col1, 140))

		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 2", font=('Helvetica', 17, 'bold'), location=(col2, 165))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[1]}", font=('Helvetica', 12), location=(col2, 140))

		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 3", font=('Helvetica', 17, 'bold'), location=(col3, 165))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[2]}", font=('Helvetica', 12), location=(col3, 140))

		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 4", font=('Helvetica', 17, 'bold'), location=(col4, 165))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[3]}", font=('Helvetica', 12), location=(col4, 140))

		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 5", font=('Helvetica', 17, 'bold'), location=(col1, 110))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[4]}", font=('Helvetica', 12), location=(col1, 85))

		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 6", font=('Helvetica', 17, 'bold'), location=(col2, 110))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[5]}", font=('Helvetica', 12), location=(col2, 85))

		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 7", font=('Helvetica', 17, 'bold'), location=(col3, 110))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[6]}", font=('Helvetica', 12), location=(col3, 85))

		scoreboard['-graph-scoreboard-'].draw_text(text="Spiller 8", font=('Helvetica', 17, 'bold'), location=(col4, 110))
		scoreboard['-graph-scoreboard-'].draw_text(text=f"Point: {pointliste[7]}", font=('Helvetica', 12), location=(col4, 85))

	while scoreboardOpen == True:
		event,values = scoreboard.read()

		if event == '-graph-scoreboard-':
			pos = values['-graph-scoreboard-']

			if 350 < pos[0] < 545 and 10 < pos[1] < 60:
				scoreboard.close()
				scoreboardOpen = False
				
		if event == sg.WIN_CLOSED:
			scoreboardOpen = False
	scoreboard.close()

def menuMange_Vindue():
	"""
	Danner vindue og kører events for menuen til simulerede spil
	"""	
	menuMange = sg.Window('Mange-Spil Menu', layout = layoutMenuMange, finalize = True)
	menuMangeOpen = True
	guiFigur = None
	startPressed = False
	
	while menuMangeOpen == True:
		event,values = menuMange.read()

		# Sæt spiltype
		if values['-spiltype-langsom-'] == True:
			spiltype = "langsom"
		elif values['-spiltype-normal-'] == True:
			spiltype = "normal"
		elif values['-spiltype-hurtig-'] == True:
			spiltype = "hurtig"

		# Sæt antal spillere
		spillerantal = values['-antal-spillere-']

		# Sæt antal gennemspilninger
		gennemspilninger = values['-antal-gennemspil-']

		# Start et spil
		if event == '-knap-menumange-start-':
			startPressed = True

			# Hvis der allerede er tegnet en graf slettes den først
			if guiFigur != None:
				sletGraf(guiFigur)

			# Opretter spilinstans fra class
			mangeSpil = spil.spilInstans(spillerantal=spillerantal, spiltype=spiltype)

			# Konfiguration af progress-bar
			menuMange['-progress-bar-'].update(max = gennemspilninger)

			# Oprettelse af lister
			pointtabel = []
			vindertabel = []

			# Gennemløb af spillet
			for i in range(int(gennemspilninger)):
				# Spillets attributes nulstilles til default før hvert spil
				mangeSpil.__init__(mangeSpil.spillerantal, mangeSpil.spiltype)
				# Der køres spilture med terningslag() indtil at der ikke er flere kaniner i midten
				while mangeSpil.kaniner >= 1:
					mangeSpil.tur(mangeSpil.terningslag())
				vindertabel.append(mangeSpil.getVinder())
				menuMange['-progress-bar-'].update("simulerer spil", current_count = ((i + 1) / gennemspilninger) * 100)

			datap1 = matematik(vindertabel,gennemspilninger,1)
			datap2 = matematik(vindertabel,gennemspilninger,2)
			datap3 = matematik(vindertabel,gennemspilninger,3)
			datap4 = matematik(vindertabel,gennemspilninger,4)
			datap5 = matematik(vindertabel,gennemspilninger,5)
			datap6 = matematik(vindertabel,gennemspilninger,6)
			datap7 = matematik(vindertabel,gennemspilninger,7)
			datap8 = matematik(vindertabel,gennemspilninger,8)

			yMax = values['-yMax-']
			yMin = values['-yMin-']
			grafdata = lavGraf(gennemspilninger,spillerantal,yMax,yMin,datap1,datap2,datap3,datap4,datap5,datap6,datap7,datap8)
			guiFigur = tegnGraf(menuMange['-graf-'].TKCanvas, grafdata)

			# Vindersandsynlighed:
			datapxs = [datap1, datap2, datap3, datap4, datap5, datap6, datap7, datap8]
			vindsans = []
			vindsansStrs = []

			for datapx in datapxs:
				if datapx[-1] > 0:
					vindsan = datapx[-1]
					vindsans.append(vindsan.round(2))
			for i in range(len(vindsans)):
				vindsansStr = (f"Spiller {i+1}: " + str(vindsans[i]) + "%")
				vindsansStrs.append(vindsansStr)

			menuMange['-besked-vindsans-'].update(vindsansStrs)
		
		# Hvis grafen er lavet opdateres grafen med det samme når yMax eller yMin rettes
		if event == '-yMax-' and startPressed == True:
			sletGraf(guiFigur)
			yMax = values['-yMax-']
			grafdata = lavGraf(gennemspilninger,spillerantal,yMax,yMin,datap1,datap2,datap3,datap4,datap5,datap6,datap7,datap8)
			guiFigur = tegnGraf(menuMange['-graf-'].TKCanvas, grafdata)
		if event == '-yMin-' and startPressed == True:
			sletGraf(guiFigur)
			yMin = values['-yMin-']
			grafdata = lavGraf(gennemspilninger,spillerantal,yMax,yMin,datap1,datap2,datap3,datap4,datap5,datap6,datap7,datap8)
			guiFigur = tegnGraf(menuMange['-graf-'].TKCanvas, grafdata)		

		if event == sg.WIN_CLOSED:
			menuMangeOpen = False
	menuMange.close()    

forside_Vindue()