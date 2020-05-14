from tkinter import *
import requests
import bs4
import re
import json

# On crée une fenêtre, racine de notre interface


def onScrapPressed():
	fenetre.withdraw()
	print("Génération du jeu de données en cours ...")

	selection = liste_magasins.curselection()

	if 0 in selection:
		scrapHm()

	#elif selection == 1:
		#zara

	fenetre.deiconify()

def scrapHm():

	categories = ["homme", "femme"]

	hm_dataset = {}

	for category in categories:
		headers = {
		'Accept-Language':'fr-FR',
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
		}

		link_all_items = "https://www2.hm.com/fr_fr/" + category + "/catalogue-par-produit/view-all.html"
		all_response = requests.get(link_all_items, headers=headers)
		all_soup = bs4.BeautifulSoup(all_response.text, 'html.parser')
		size = all_soup.find('h2',{"class":"load-more-heading"})['data-total']

		link_all_items_with_size = link_all_items + "?sort=stock&image-size=small&image=model&offset=0&page-size=" + size

		response = requests.get(link_all_items_with_size, headers=headers)
		soup = bs4.BeautifulSoup(response.text, 'html.parser')
		articles = soup.find_all("h3", {"class":"item-heading"})
		for article in articles:
			link = "https://www2.hm.com/" + article.find("a", {"class": "link"})["href"]
			headers['Referer'] = link
			response_article = requests.get(link, headers=headers)
			soup_article = bs4.BeautifulSoup(response_article.text, 'html.parser')
			article_details = soup_article.find_all("div", {"class":"details-attributes-list-item"})
			article_name = soup_article.find('h1',{"class":"primary product-item-headline"})
			article_img = soup_article.find('div',{"class":"product-detail-main-image-container"})

			if not article_name or not article_details:
				continue

			name = article_name.getText().strip()
			composition = ""
			reference = re.findall(r"productpage\.(.*)\.html",link)[0]
			image = article_img.find('img')['src']

			for detail_line in article_details:
				if detail_line.find("dt", {"class": "details-headline"}).getText() == "Composition":
					soup_composition = detail_line.find_all("dd", {"class": "details-list-item"})
					for composition_line in soup_composition:
						composition += composition_line.getText() + " "

			hm_dataset[reference] = {
				'nom' : name,
				'lien_produit' : link,
				'lien_image' : image,
				'composition' : composition,
				'reference' : reference

			}

			print("Ajout " + name + " " + reference)

	createJsonFile("H&M_dataset", hm_dataset)

def createJsonFile(name, data):
	json_dump = json.dumps(data)
	jsonfile = open(name + ".json","a") 
	jsonfile.write(json_dump)
	jsonfile.close() 




fenetre = Tk()
# On crée un label (ligne de texte) souhaitant la bienvenue
# Note : le premier paramètre passé au constructeur de Label est notre
# interface racine
champ_label = Label(fenetre, text="Outil de génération de jeu de donnée via scrapping")

# On affiche le label dans la fenêtre
champ_label.pack()

# On démarre la boucle Tkinter qui s'interompt quand on ferme la fenêtre


liste_magasins = Listbox(fenetre)
liste_magasins.insert(END, "H&M")
liste_magasins.insert(END, "ZARA")
liste_magasins.pack()

bouton_scrapper = Button(fenetre, text="Scrapper", command=onScrapPressed)
bouton_scrapper.pack()

bouton_quitter = Button(fenetre, text="Quitter", command=fenetre.quit)
bouton_quitter.pack()

fenetre.mainloop()