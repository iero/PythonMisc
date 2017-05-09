#pip install wikipedia
import wikipedia

def getImage(page) :
    wikipage = wikipedia.page(page)
    if wikipage.images and len(wikipage.images) >= 1 :
        return wikipage.images[0]

def printAllImages(page) :
    wikipage = wikipedia.page(page)
    if wikipage.images and len(wikipage.images) >= 1 :
        for i in wikipage.images :
            print(i)


if __name__ == "__main__":
    printAllImages("Lennon")

# PAGES = ['New York', 'Mercury_(planet)', 'Tucana']
#
# for page in PAGES:
#     wikipage = wikipedia.page(page)
#     print "Page Title: %s" % wikipage.title
#     print "Page URL: %s" % wikipage.url
#     print "Nr. of images on page: %d" % len(wikipage.images)
#     print " - Main Image: %s" % wikipage.images[0]
#     print ""
