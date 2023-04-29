import wikipedia
import csv
import requests
from bs4 import BeautifulSoup



####define diet categories####

carnivore = ["carnivore", "carnivorous", 'Carnivorous', 'Carnivore', 'bird of prey', 'predatory', 'carnivora', 'amphibian', 'amphibians', 'carnivores', 'reptile', 'cephalopod'] # 'predator']  #how to deal with words like "predator" that are used in contradictory contexts?
herbivore = ["herbivore", "herbivorous", "Herbivore", "Herbivorous", 'tortoise', 'iguana']
omnivore = ["omnivore", "omnivorous", "Omnivore", "Omnivorous", 'omnivores']
insectivore = ["insectivore", "Insectivore", 'insectivorous', "Insectivorous", 'entomophagous', 'spider']
frugivore = ["frugivore", "Frugivore", 'frugivorous', 'Frugivorous']
bloodfeeder = ["blood feeder", "Blood feeder", "Hematophagy", "hematophagy"]
scavenger = ["Scavenge", 'scavenge', 'detritivore', 'Detritivore', 'detritivorous', 'Detritivorous', 'carrion', 'Carrion', 'detrivorous']
granivore = ["granivore", "Granivore", "granivorous", "Granivorous"]
nectarivore = ["nectarivore", "Nectarivore", "nectarivorous", "Nectarivorous"]
folivore = ["folivore", "Folivore", "folivorous", "Folivorous", "folivory", "Folivory"]
gummivore = ["gummivore", "Gummivore", "gummivorous", "Gummivorous", "gummivory", "Gummivory"]
filterfeeder = ["filter feeder", "Filter feeder", "filter feed", "Filter feed", 'clam ', 'mollusk ']
#and a category for food-related words that aren't specific to one diet
undefined = [' eat', ' food ', ' consume', ' feed', ' diet ', ' prey']

#make a master list of all query strings
all_diet_query=carnivore + herbivore + omnivore + insectivore + frugivore + bloodfeeder + scavenger + granivore + nectarivore + folivore + gummivore + filterfeeder + undefined


#######read in initial species list###########

#a function that takes a .csv file with species data and returns that data as a dictionary
#values can be adjusted depending on how csv is organized

def species_dict(file):
    
    #a list to hold the species in the file
    species_list = []
    
    #open the file and read the values into our 
    with open(file, "r") as metadata:
        
        #skip the first line, since that's just the title line
        next(metadata)
        
        csvreader = csv.reader(metadata)
        
        #for each row, make a dictionary for the species
        for row in csvreader:
            species = {}
            species['species_name'] = row[0].strip()    #values can be adjusted depending on layout of file being read
            species['common_name'] = row[1].strip()
            species['class_name'] = row[2].strip()
            
            #and add it to the species_list, avoiding repeats
            if species not in species_list:
                species_list.append(species)
            
    return species_list
    
    
    
   
