#!/usr/bin/python
from pyvirtualdisplay import Display
from selenium import webdriver
import products_db as my_db
from random import randint
from time import sleep
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains


#redirecting output display when using ssh server
display = Display(visible=0, size=(1000, 800))
display.start()

database_dir = "/home/bt2/14CS10055/BTP_Resources/Data"
database_path_links = database_dir + "/links.db"
database_path_reviews = database_dir + "/reviews.db"
database_path_prod =  database_dir + "/products.db"

img_table_name = "IMG"
desc_table_name = "DESC"
prod_table_name = "PROD"
lin_table_name = "LINKS"
domain = "IN"

#stores metadata in current page
def store_metadata_in_page(ProdId, address, driver):
	# driver = webdriver.Firefox()
	prod_db = my_db.database_sqlite()
	prod_db.create_connection(database_path_prod)
	prod_db.set_table_name(domain)
	driver.get(address)
	print "Retrieved Product Page successfully!!!"

	results = driver.find_element_by_xpath('.//span[@id="productTitle"]')
	#getting title of product
	title = results.text

	#getting star of product
	result = driver.find_element_by_xpath('.//div[@id="averageCustomerReviews"]')
	try:
		result = result.find_element_by_xpath('.//span[@id="acrPopover"]')
		stars = result.get_attribute('title').split(" ")[0]
	except:
		stars="0"
	#insert into product table
	prod_db.insert_prod(ProdId, title, stars)

	#getting features of the product
	results = driver.find_element_by_xpath('.//div[@id="feature-bullets"]')
	features = results.find_elements_by_xpath('./ul/li')
	i=0
	for feature in features:
		i+=1
		prod_db.insert_desc(ProdId, feature.text, ProdId+"#"+str(i))

	#getting images of product
	results = driver.find_element_by_xpath('.//div[@id="altImages"]')
	altImages = results.find_elements_by_xpath('./ul/li')
	for img in altImages:
		hover = ActionChains(driver).move_to_element(img)
		hover.perform()		
	results = driver.find_element_by_xpath('.//div[@id="main-image-container"]')
	img = results.find_element_by_xpath('./ul')
	images = img.find_elements_by_xpath('.//img')
	i=0
	for image in images:
		i+=1
		img_src = image.get_attribute('src')
		prod_db.insert_img(ProdId, img_src, ProdId+"#"+str(i))

	#save changes
	prod_db.save_changes()
	print ProdId,  "Retrived successfully!!!"
	prod_db.get_count(prod_table_name)
	return 1

def testing():
	database_path = "/home/gulab/pythonsqlite.db"
	initialise_conn(database_path)
	my_db.insert_link("opbfhd", "fdhfjgh")
	my_db.print_all()
	my_db.save_changes()

#getting metadata for all products in LINK table
def get_all_metadata():
	links_table = my_db.database_sqlite()
	links_table.create_connection(database_path_links)
	links_table.set_table_name(domain)
	#initialise a cursor in db
	links_table.initialise_cursor(lin_table_name)
	#get next row in db
	row = links_table.get_next_element()
	retry_cnt = 5
	while retry_cnt:
		try:
			driver = webdriver.Firefox()
			print "Firefox Running!!"
			while row:	
				print "Getting metadata for : ", row[0]
				sleep(randint(5,15))
				store_metadata_in_page(row[0],row[1],driver)
				row = links_table.get_next_element()
			break
		except Exception as e:
			print "Error in getting metadata!"
			print e
			try:
				driver.quit()
			except Exception as e:
				print e
			print "Retrying..."
			retry_cnt-=1
	links_table.get_count(lin_table_name)

def main():
	prod_table = my_db.database_sqlite()
	prod_table.create_connection(database_path_prod)
	prod_table.set_table_name(domain)

	prod_table.create_table_products()
	prod_table.create_table_img()
	prod_table.create_table_desc()
	
	get_all_metadata()

	prod_table.get_count(prod_table_name)
	prod_table.print_all(prod_table_name)
	prod_table.print_all(desc_table_name)
	prod_table.print_all(img_table_name)
	prod_table.get_count(prod_table_name)
	prod_table.get_count(desc_table_name)
	prod_table.get_count(img_table_name)

if __name__ == '__main__':
	main()
