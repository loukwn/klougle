from .spiders.cnnspider import CNNSpider
from .spiders.bbcspider import BBCSpider
from .spiders.guardianspider import GuardianSpider
from .indexingtools.indexer import PageIndexer

if __name__ == "__main__":

    print('=== Scraping and indexing tools ===')
    print('\n-Do you want to scrape from every category or select an individual? ')
    while True:
        print('1) Every\n2) Individual')
        sel = int(input())
        if sel == 1 or sel == 2:
            break

    print('-Up to how many pages should I fetch from every category? ')
    thres = int(input())

    if sel == 1:
        print('\n-Starting CNN scraper (all categories)')
        CNNSpider(threshold=thres).scrape_all()
        print('\n-Starting BBC scraper (all categories)')
        BBCSpider(threshold=thres).scrape_all()
        print('\n-Starting The Guardian scraper (all categories)')
        GuardianSpider(threshold=thres).scrape_all()
    else:
        print('-Type the category numbers (space separated) that you want to scrape from')
        print('1) Sports\n2) Business/Money\n3) Entertainment/Arts\n4) Technology\n5) Science/Environment\n')
        cats = [int(c)-1 for c in input().split(' ')]
        if len(cats) == 0:
            print('Error inserting values')
            exit(-1)
        print('\n> Starting CNN scraper (selected categories)')
        CNNSpider(threshold=thres).scrape_selected(cats)
        print('\n> Starting BBC scraper (selected categories)')
        BBCSpider(threshold=thres).scrape_selected(cats)
        print('\n> Starting The Guardian scraper (selected categories)')
        GuardianSpider(threshold=thres).scrape_selected(cats)

    print('-Finished scraping!')
    print('-Starting tagger/indexer tool..\n')
    PageIndexer().start()
    print('\n-Done indexing')
