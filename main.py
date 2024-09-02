from colorama import Fore, Back, Style, init
import os
import ast
#site map file
from map import initMapping
#this file is use to tell what results from the site map are collection pages.
from whichIsCollections import findCollectionsURLs
from focusMap import initFocusMapping
from handleCaptcha import bypass
from pullText import pullFirstListing
from findDiv import getDiv
from getClasses import findClasses
import time

def printToConsole(text, color):
    terminal_width = os.get_terminal_size().columns
    padding = (terminal_width - len(text)) // 2
    paddingBar = (terminal_width - len('---------------------')) // 2
    print(color + ' ' * paddingBar + '---------------------')
    print(color + ' ' * padding + text)
    print(color + ' ' * paddingBar + '---------------------')



url = 'https://www.sportsdirect.com/'
#Mapping
uniqueURLs = initMapping(url)

if(len(uniqueURLs) < 2):
    print(Fore.RED + "SITE MAPPING FAILED")
    print(uniqueURLs)
else:
    printToConsole('SITE MAPPING WORKED', Fore.GREEN)
    print(uniqueURLs)

    collectionPages = findCollectionsURLs(uniqueURLs)
    printToConsole('COLLECTION ENTRY WORKED', Fore.GREEN)
    print(Fore.BLACK + collectionPages)
    url_list = ast.literal_eval(collectionPages)


    #Focus mapping
    focusMap = initFocusMapping(url, url_list[0], 1)
    print(focusMap[0], 'focus map 0')
    #Bypass
    imgFileResult = bypass(focusMap[0])
    print(f'https://mfraljoybtduzwhprbcp.supabase.co/storage/v1/object/public/TE/{imgFileResult}')
    #pull first product listing text
    time.sleep(11)
    listingText = pullFirstListing(f'https://mfraljoybtduzwhprbcp.supabase.co/storage/v1/object/public/TE/{imgFileResult}')
    printToConsole('PULLED LISTING TEXT WORKED', Fore.GREEN)
    print(listingText)
    outerHTML = getDiv(focusMap[0], listingText)
    print(outerHTML)
    classes = findClasses(outerHTML)
    print(classes)







