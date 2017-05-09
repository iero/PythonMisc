from bs4 import BeautifulSoup
#pip install selenium
import selenium.webdriver as webdriver

def getLastEntries(user) :

    url = 'http://instagram.com/'+user+'/'
    driver = webdriver.Firefox()
    driver.get(url)

    soup = BeautifulSoup(driver.page_source)

    for x in soup.findAll('div', {'class':'_jjzlb'}):
        print(x)

getLastEntries("lilian_dauzat")
