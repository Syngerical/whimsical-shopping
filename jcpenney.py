from PIL import Image
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq
from random import *
import json
import urllib
import urllib.request

# lists containing the departments and categories that we are looking for
validDepartments = ["men", "women"]
validCategories = ["shirts", "pants"]

# urls is a dictionary with the categories we care about as the key and all products in those categories
# as the value. We will randomly pick one product from each category in urls to create an outfit
# initalize urls with each category as a key and an empty list for value
urls = {category: [] for category in validCategories}

def main():
    departmentIDs = getDepartmentIDs()
    categoryIDs = getCategoryIDs(departmentIDs)
    getProductUrls(categoryIDs)
    print(urls)
    getOutfit()
                
# returns a list of department IDs, only contains IDs for departments listed in validDepartments
def getDepartmentIDs():
    # holds the department IDs
    departmentIDs = []
    # base url to use for each API call
    baseUrl = "https://api.jcpenney.com/v2/"
    # opens url for all the departments jc penney has like bed&bath, windows, mens (clothing), womens (clothing)
    with urllib.request.urlopen(baseUrl + "departments") as url:
        # departments is a list of dictionaries, each list index is a department
        departments = json.loads(url.read().decode())
        for department in departments:
            # if this department is in validDepartments, add its ID to department IDs
            if(department["name"] in validDepartments):
                departmentIDs.append(department["id"])
    # return department IDs
    return departmentIDs

# returns a list of category IDs, only contains IDs for categories listed in validCategories
# @param departmentIDs: list of IDs for the departments we want to check
def getCategoryIDs(departmentIDs):
    # holds the category IDs
    categoryIDs = []
    # base url to use for each API call
    baseUrl = "https://api.jcpenney.com/v2/categories/"
    # iterates through each department ID and retrieves its JSON information
    for id in departmentIDs:
        with urllib.request.urlopen(baseUrl + id) as url:
            # categories is a list of categories like belts, socks, shoes, etc within each department
            categories = json.loads(url.read().decode())["categories"]
            # iterates through each category. if the name of the category is in validCategores, adds
            # its ID to categoriesToCheck
            for category in categories:
                if(category["name"] in validCategories):
                    categoryIDs.append(category["id"])
    # return category IDs
    return categoryIDs

# updates globoal variable urls 
def getProductUrls(categoryIDs):
    # base url to use for each category ID
    baseUrl = "https://api.jcpenney.com/v2/categories/"
    # iterates through each category ID and retrieves its JSON information
    for id in categoryIDs:
        with urllib.request.urlopen(baseUrl + id + "/products") as url:
            # results is a list of all the products in that category. we need this so we can also
            # have a way to find the 'name' field so we know what category this is
            results = json.loads(url.read().decode())
            # products gets the list of actual products without some extra info in results like name, id, etc
            products = results["products"]
            # iterates through each product and gets its link to the actual jc penney website and
            # adds it to the global variable urls under the proper key for the category
            for product in products:
                product_links = product["links"][0]
                product_url = product_links.get("href")
                urls[results["name"]].append(product_url)
                
# gets the randomized outfit
def getOutfit():
    # iterates through each category
    for key in urls:
        # holds the list of products for that category, ie all the shirts or all the pants
        products = urls[key]
        # holds the index we randomly generated to select the random outfit
        index = randint(0, len(products) - 1)
        # picks an item from that category
        pickItem(products[index])
        
# given a specific product url, web scrapes for an image and displays it to the user
def pickItem(product):
    # opens up connection, grabs the page
    uClient = uReq(product)
    page_html = uClient.read()
    uClient.close()
    # web scrapes for images from that page
    page_soup = soup(page_html, "html.parser")
    imgs = page_soup.findAll("img")
    # grabs the first image, found that it is the most accurate representation
    img = imgs[0]
    
    # grabs link for that specific image
    image_link = img.get("src")
    # if the link retrieved was partial, add the https: part
    if image_link[:1] == "/":
        image_link = "https:" + image_link
        
    # holds what we will name the file
    image_name = img.get("alt")
    if image_name == "":
        image_name = "unnamed"
    
    # saves the image locally        
    imagefile = open(image_name + ".jpeg", "wb")
    imagefile.write(urllib.request.urlopen(image_link).read())
    imagefile.close()
    
    # opens the image we just saved
    picture = Image.open(image_name + ".jpeg")
    picture.show()


if __name__ == '__main__':
    main()
