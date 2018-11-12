from bs4 import BeautifulSoup
from urllib.request import urlopen
import re

from selenium import webdriver      
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
 
import pandas 

PAGE_URL = "https://www.saboresdehoy.com/recetas"

#Función para obtener todos los links de recetas
#Utilizamos selenium para poder simular el click en el botón de Más recetas 
#De esta manera nos aseguramos de que se muestran todas las recetas existentes
def getLinks(url):
	PATIENCE_TIME = 60
	driver = webdriver.Chrome('./chromedriver.exe')
	driver.get(PAGE_URL)
	driver.maximize_window()

	loadMoreButton = driver.find_element_by_xpath("//div[@id='barracookies']/a[1]")
	time.sleep(2)
	loadMoreButton.click()

	while True:
		try:
			loadMoreButton = driver.find_element_by_id("loadMore")
			time.sleep(2)
			loadMoreButton.click()
			time.sleep(5)
		except Exception as e:
			print(e)
			break

	time.sleep(10)
	
	links = []
	
	links_elements = driver.find_elements_by_xpath("//a[contains(@href,'recetas/')]")
	
	for link in links_elements:
		links.append(link.get_attribute("href"))
		
	driver.quit()
	
	return list(set(links))

#Función para obtener los datos de la receta que vamos a incluir en nuestro dataset
#Utilizamos BeautifulSoup para extraer la información
def getRecipe(url):
	page = urlopen(url)
	soup = BeautifulSoup(page, "html.parser")
	
	nombre_tag = soup.find("span",attrs={"class": "titulo"})
	nombre = nombre_tag.text.replace(","," ")
	
	autor_tag = soup.find("span",attrs={"itemprop": "name"})
	autor = autor_tag['content'].replace(","," ")
	
	personas_tag = soup.find("span",attrs={"itemprop": "recipeYield"})
	personas = personas_tag.text
	
	calorias_tag = soup.find("div",attrs={"class": "textocalorias"})
	calorias = calorias_tag.text

	image_tag = soup.find("meta",attrs={"itemprop": "url"})
	image = image_tag['content']
	
	image_width_tag = soup.find("meta",attrs={"itemprop": "width"})
	image_width = image_width_tag['content']
	
	image_height_tag = soup.find("meta",attrs={"itemprop": "height"})
	image_height = image_height_tag['content']
	
	alergenos = ""
	i = 0
	
	div_alergenos = soup.find("div",attrs={"id": "alergenos"}).find_all("img")
			
	for child in div_alergenos:
		if (i == 0):
			alergenos = child.get('title')
		else:
			alergenos = alergenos + "|" + child.get('title')
		
		i = i + 1
		
	listado_ingredientes = soup.find_all("span",attrs={"itemprop": "ingredients"})
	
	filas = []
	for child in listado_ingredientes:
		txt_ingrediente = child.text
		campos = child.text.split(' ', maxsplit=2)
		cantidad = campos[0]
		unidad = campos[1]
		ingrediente = campos[2]
	
		filas.append([url,nombre,autor,personas,alergenos,calorias,ingrediente,cantidad,unidad,image,image_width,image_height])
				
	return filas

#Obtenemos todos los links	
url_recetas = getLinks(PAGE_URL)

#Guardamos en un dataset todos los registros de cada una de las recetas
dataset = []
for urls in url_recetas:
	dataset = dataset + getRecipe(urls)
	
#Utilizamos pandas para exportar a csv los registros del dataset	
pd = pandas.DataFrame(dataset)	
pd.to_csv('recipes.csv',index=False,encoding='iso-8859-1')



