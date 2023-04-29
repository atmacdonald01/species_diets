import wikipedia
import csv
import requests
from bs4 import BeautifulSoup
from collections import Counter



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
   
    
    
#####read in data and print the resulting list######
species_list = species_dict("allison_song_diet.csv")  #insert name of data file here
print(len(species_list))
for item in species_list:
    print(item)
    

#####make a list/set of scientific and common names for use in our search functions; name is tuple of scientific name/common name######
species_list_non_dict = []
for item in species_list:
    name = item['species_name']
  #  scientific = item['scientific_name']
   # common = item['common_name']
    #name = (scientific, common)
    
    #avoid repeats
    if name not in species_list_non_dict:
        species_list_non_dict.append(name)

print(len(species_list_non_dict))




########split the big list into smaller ones so it's easier for the eol function to digest--trying to do thousands of species at once overloads the function###############
#produces an embedded list: the original list split into chunks 500 species long, and each chunk added to a list
small_lists = []
working_list = []
total_count = 0
count = 0
for item in species_list_non_dict:
    working_list.append(item)
    count += 1
    total_count += 1
    #if the list is 500 long, add that chunk to the master list and start a new chunk
    if count == 500:
        small_lists.append(working_list)
        count = 0
        working_list = []
    elif total_count == len(species_list_non_dict):
        small_lists.append(working_list)
        
#check -- print the length of each chunk and the first item in that chunk
for item in small_lists:
    print(len(item))
    print(item[0])
    print("\n")
    
    
    
    
######EOL SEARCH FUNCTION##########
#using html/BeautifulSoup, scrape the Encyclopedia of Life website for diet data
#this function looks up the species in EOL, checks the "eat" section of its page, looks at the species overview, and looks at
#its "data" section for information about its data

def check_eol(species):
    diet = []                        #establish diet list
    og_species = species.lower()     #and species name
    
    no_eats = False
    
    #first, build the search URL from the species name
    species = species.lower().split(" ")
    species = "+".join(species)
    url = "https://eol.org/search?utf8=%E2%9C%93&q=" + species
    
    #go to the url
    page = requests.get(url)      #use 'requests' library to grab the html code of the url
    #and get the html
    soup = BeautifulSoup(page.content, "html.parser")      #get the html content of the page using BeautifulSoup
    
    #get the list of search results
    search = soup.find(class_="search-results js-search-results")                    #pick out the results section from the html
    if search != None:
        results_list = search.find_all("a")                                             #pick out the list of search results
    
    
        #find the result with the most associated media
        highest = 0
        choice = ""
        species_link = ""
        for item in results_list:                                        #for each result, find the species name and how many articles are associated with it
            link = item['href']                                        #get the link for the result
            result = item.find("div", class_="search-title").text       #get the search title (the text of the result)
            if og_species in result.lower():                           #if the result has the correct species name, look at it
                media = item.find("ul", class_="resource-bubbles")
                total_media = media.text.split("MEDIA")[0].strip()            #split off the first number (the # of associated media) from other numbers
                if total_media.isdigit() and int(total_media) > highest:                                   #if this number is a true number (not \n or '1 MEDIUM', for ex)
                    highest = int(total_media)
                    choice = item
                    species_link = "http://eol.org" + link #+ "/data"         #get the address of the page with the highest results and go to the "data" section
            
        #now that we have a species page, we need to check the overview, the "data" page, and the "articles" page for diet information
        if len(species_link) > 0:
            
            #####
            #the first step is to go to the overview page and see if there's a diet category there
            general_page = requests.get(species_link)
            general_soup = BeautifulSoup(general_page.content, "html.parser")
            general = general_soup.find("p")
            try:
                general_info = general.text.lower()
                for item in all_diet_query:
                    #if we find a diet type, get the sentence and add it to "diet"
                    if item in general_info:
                        sentence = ""
                        index = general_info.index(item)
                        stop = False
                        #add the sentence up to the next period to get the full sentence from where diet was mentioned
                        while stop == False:
                            try:
                                sentence += general_info[index]
                            except IndexError:
                                break
                            index += 1
                            try:
                                if general_info[index] == ".":
                                    stop = True
                            except IndexError:
                                break
                        diet.append(sentence)             #add the sentence to the diet list
            except AttributeError:
                print("No overview found.")

            ######
            #the next step is to go to the "data" page and see if there's an "eat" section, so we'll get the html content of the species data page
            species_data_link = species_link + "/data"
            data_page = requests.get(species_data_link)
            data_soup = BeautifulSoup(data_page.content, "html.parser")
        
            #find the "eat" category out of the "data" section on the species page
            categories = data_soup.find_all("a", class_="item")             #find all the data categories on the "data" page of the species
            diet_link = ""
            for category in categories:
                if category.text == "eat":
                    diet_link = "http://eol.org" + category['href']             #if there's an "eat" section, get the diet page url
    
            #if there was an "eat" section, get the html content of the diet page
            if len(diet_link) > 0:
                diet_page = requests.get(diet_link)
                diet_soup = BeautifulSoup(diet_page.content, "html.parser")
    
                #add each eaten species to the diet list
                eats = diet_soup.find_all("div", class_="trait-val")       #find the listed species that species eats
                for eat in eats:
                    diet.append(eat.text.strip())
        
            #if there's no "eat" section, say so
            else:
                print("No eats found.")
                no_eats = True
            
            ########
            #if diet is still empty, the next step is to check the "articles" section for diet information
            if no_eats == True and diet == []:
                species_article_link = species_link + "/articles"
                article_page = requests.get(species_article_link)
                article_soup = BeautifulSoup(article_page.content, "html.parser")

                #now that we have the html of the "articles" page, we need to get its text and look through it for diet keywords
                article_text = []                                     # a list to hold the text of the articles
                articles = article_soup.find_all("div", class_="body uk-margin-small-top")        #get the article sections
                #and add each article to the list of article_text
                for article in articles:
                    article_text.append(article.text)

                #then, go through each item in article_text and look for diet information
                for a in article_text:
                    for item in all_diet_query:                #loop through our list of diet types and see if they're mentioned in the page
                        #if we find a diet type in the article
                        if item in a:
                            sentence = ""
                            index = a.index(item)
                            stop = False
                            #add the sentence up to the next period to get the full sentence from where diet was mentioned
                            while stop == False:
                                try:
                                    sentence += a[index]
                                except IndexError:
                                    break
                                index += 1
                                try:
                                    if a[index] == ".":
                                        stop = True
                                except IndexError:
                                    break
                            diet.append(sentence)             #add the sentence to the diet list

            ######
            #if diet is still empty, try looking up the classification tree
            tree = general_soup.find("div", class_="hier js-hier-summary")
            try:
                branches = tree.find_all("a")
                #look at each step in the tree and add it to diet if it matches a diet type (amphibians, carnivores, etc.)
                for branch in branches:
                    if branch.text.lower() in all_diet_query:
                        diet.append(branch.text.lower())
            except AttributeError:
                print("No tree found.")
            
            
            #######                
            #if we go through all that and still have no diet info, say so
            if no_eats == True and diet == []:
                print("No diet section and no article diet data.")
                diet = "No diet section and no article diet data."
        
        #if there's no species link, say so
        else:
            print("No species link found.") 
            diet = "No species link found."
        
    #if there's no results page, say so
    else:
        print("No results found.")
        diet = "No results found."
        
    return diet



######use eol function on our species list##########
#using the check_eol function, create a dictionary of each species and the diet results found from scraping the EOL website

eol_species_diet = {}          #dictionary to hold our results

#counts to measure results and where data is found or missing
count = 0
eats_unfound = 0
link_unfound = 0
species_unfound = 0

#go through each mini-list; for each species, grab the scientific name and run the check_eol function on it
for list_ in full_test_lists:
    count += 1
    print("NOW CRUNCHING THROUGH LIST: ", count, "\n")
    eol_species_diet[count] = {}
    for species in list_:
        try:
            scientific_name = species[0]
        except IndexError:
            print("unhashable species name")
     #   common_name = species[1]
        eol_species_diet[count][scientific_name] = []
#    eol_species_diet[species] = []
        result = check_eol(scientific_name)
        
        if result == "No diet section and no article diet data.":
            eats_unfound += 1
            
        elif result == "No species link found.":
            link_unfound += 1
            
        elif result == "No results found.":
            species_unfound += 1
            
        else:
            eol_species_diet[count][scientific_name] = result
            print(species, result)
            
print(eats_unfound)
print(link_unfound)




#############store EOL data############
#next, write the data in eol_species_diet to a .csv; that way it's stored safely and we can read it into other functions

with open("allison_song_eol_species_data.csv", "w") as f:   #insert name of file here
    writer = csv.writer(f)
    header = ("SPECIES", "DATA")    #title of the columns
    writer.writerow(header)
    
    num = 0
    row_count = 0
    for count in eol_species_diet:                 #for each sub-list of 500 species
        for species in eol_species_diet[count]:    #for each species in the sub-list
            num += 1
            if eol_species_diet[count][species] != []:              #if a diet was found
                row = (species, eol_species_diet[count][species])   #make a row of the species and the data that was found
                writer.writerow(row)                                #and add it to the .csv
                row_count += 1
    
    #num tells us how many species there were total; row_count shows how many species had diet data
    print(num)
    print(row_count)
    
  


##########WIKIPEDIA SEARCH FUNCTION###############
#a function to search wikipedia: takes a species name and returns a dictionary of its diet data
def check_wiki(species):
    species = species.strip()   #clean species name of any extraneous spaces
    
    #establish dictionary and count of how many diet-type instances found
    diet = {}
    total_count = 0
    
    #look for the species in wikipedia
    try:
        page = wikipedia.page(species, auto_suggest=False)                 #get page, if possible
        page_content = page.content                                        #pull the content of the page
        for item in all_diet_query:                #loop through our list of diet types and see if they're mentioned in the page
            #if we find a diet type in page_content
            if item in page_content:
                #make an entry for each diet type that is found
                if item not in diet.keys():        
                    diet[item] = {}    
                    diet[item]["count"] = 0         
                    diet[item]["mentions"] = []
                    
                #add diet type to "diet" dictionary with spots for counts of each diet type mentioned and the sentences the mention occurs in
                index = page_content.index(item)
                sentence = ""
                stop = False
                #add the sentence up to the next period to get the full sentence from where diet was mentioned
                while stop == False:
                    try:
                        sentence += page_content[index]
                    except IndexError:
                        break
                    index += 1
                    try:
                        if page_content[index] == ".":
                            stop = True
                    except IndexError:
                        break
                
                #increase the count of the diet that was found and append the sentence to the dictionary
                diet[item]["count"] += 1
                diet[item]["mentions"].append(sentence)
                
                total_count += 1                   #count up that we've found a diet type
                
                
    except wikipedia.exceptions.PageError:
        print('Page not found: ' + species)
        return None
                    
    except wikipedia.exceptions.DisambiguationError:
        print("Ack! Disambiguation error.")
        return None
        
    #sometimes a KeyError is thrown for some strange reason...
    except KeyError:
        print("KeyError?")
        return None
        
    #return nothing if no diet types were found; otherwise, return the diet dictionary
    if total_count == 0:
        return None
    else:
        return diet
    

    
##########use wikipedia function on our species list##############
#search wikipedia for diets
wiki_species_diet = {}         #dictionary to hold species and the diets that are found

unfound = 0
no_keywords = []

#look through each species in our species list
for species in species_list_non_dict:
    
    diet = find_diet(species)                 #run find_diet on the species
    
    #if unsuccessful, try genus name
    if diet == None:
        genus = species.split()[0]
        diet = find_diet(genus)
    
    #if still unsuccessful, count as unfound
    if diet == None:
        unfound += 1
        no_keywords.append(species)
        
  #add diet to wiki_diets dictionary
    wiki_species_diet[species] = diet
        
  #  print(diet)
    
print(unfound)
print(no_keywords)
print(wiki_species_diet)



#######clean up the data a little bit##########
#a function to consolidate the diet types found by the wiki_diets function (e.g. "predator", "carnivorous" collapsed into "carnivore")
#also finds the most commonly mentioned diet type for each species

def consolidate(diet_dict):
    
    #first, make a dictionary that consolidates the various vocab (carnivore, carnivorous, etc.) into one diet category
    diet_key = {}
    diet_key[("carnivore", "carnivorous", 'Carnivorous', 'Carnivore', 'bird of prey', 'predatory', 'carnivora', 'amphibian', 'amphibians', 'carnivores', 'reptile', 'cephalopod')] = "carnivore"
    diet_key[("herbivore", "herbivorous", "Herbivore", "Herbivorous", 'iguana', 'tortoise')] = "herbivore"
    diet_key[("omnivore", "omnivorous", "Omnivore", "Omnivorous")] = "omnivore"
    diet_key[("insectivore", "Insectivore", "insectivorous", "Insectivorous", 'entomophagous', 'spider')] = "insectivore"
    diet_key[("frugivore", "Frugivore", "frugivorous", "Frugivorous")] = "frugivore"
    diet_key[("blood feeder", "Blood feeder", "Hematophagy", "hematophagy")] = "blood feeder"
    diet_key[("Scavenge", 'scavenge', 'detritivore', 'Detritivore', 'detritivorous', 'Detritivorous', 'carrion', 'Carrion', 'detrivorous')] = "scavenger"
    diet_key[("granivore", "Granivore", "granivorous", "Granivorous")] = "granivore"
    diet_key[("nectarivore", "Nectarivore", "nectarivorous", "Nectarivorous")] = "nectarivore"
    diet_key[("folivore", "Folivore", "folivorous", "Folivorous", "folivory", "Folivory")] = "folivore"
    diet_key[("gummivore", "Gummivore", "gummivorous", "Gummivorous", "gummivory", "Gummivory")] = "gummivore"
    diet_key[("filter feeder", "Filter feeder", "filter feed", "Filter feed", 'clam ', 'mollusk ')] = "filter feeder"
    diet_key[(' eat', ' food ', ' consume', ' diet ', ' prey')] = "undefined"
    

    #then, establish a dictionary that will hold the consolidated diet types for each animal
    categorized = {}
    
    #and go through the diet_dict to consolidate the diets of each species in diet_dict
    for species in diet_dict:
        categorized[species] = {}         #establish an entry for each species
        
        #for each diet of each species in diet_dict, look through diet_key and assign a category accordingly
        if diet_dict[species]['diet'] != None and diet_dict[species]['diet'] != []:
            for diet in diet_dict[species]['diet']:     #for each diet word listed under 'diet' 
          #      print(diet)
                for item in diet_key:                  #go through the diet categories and find which one the diet word fits into
                    if diet.lower() in item:
                        categorized_entry = diet_key[item]
                    
                #if need be, establish an entry in 'categorized' for this diet type
                if categorized_entry not in categorized[species]:
                    categorized[species][categorized_entry] = {}
                    categorized[species][categorized_entry]['count'] = 0
                    categorized[species][categorized_entry]['sentences'] = []

                #add the specific diet count to the category count, and append the relevant sentences
                categorized[species][categorized_entry]['count'] += diet_dict[species]['diet'][diet]['count']
                categorized[species][categorized_entry]['sentences'].append(diet_dict[species]['diet'][diet]['mentions'])

        #after going through all the diets per species, find which diet category has the most mentions
        highest = 0
        highest_cat = ''
        for category in categorized[species]:
            if categorized[species][category]['count'] > highest:
                highest = categorized[species][category]['count']
                highest_cat = category
        categorized[species]['most_likely'] = highest_cat
        

    return categorized


########consolidate wiki_species_diet using the consolidate function#########
consolidated_wiki_diets = consolidate(wiki_species_diet)


######store the wikipedia data########
#then, write the output of the consolidated dictionary to a .csv, just like we did for the EOL data

with open('allison_song_wikipedia_diets.csv', 'w') as f:          #insert name of file here
    writer = csv.writer(f)
    
    header = ["Species name", "Most likely diet", "All diets mentioned", "Diet sentences"]
    writer.writerow(header)
    
    for species in consolidated_wiki_diets:
        most_likely = consolidated_wiki_diets[species]['most_likely']
        sentences = []
        diets = []
        #go through each diet listed (carnivore, herbivore, etc.) and add the diet and its related sentences to the diet and sentences lists
        for diet in consolidated_wiki_diets[species]:
            if diet != 'most_likely' and diet != 'class_name' and diet != 'common_name':
       #         count = consolidated_diet[species][diet]['count']
                diets.append(diet)
                sentences.append(consolidated_diet[species][diet]['sentences'])
            
        #make a row of the species name, the most likely diet, all the listed diets, and all the diet sentences that were found
        row = (species, most_likely, diets, sentences)
        
        print(row)
        writer.writerow(row)
    
   


############COMBINE THE EOL AND WIKIPEDIA DATA#############
#now that we have both the EOL data and the wikipedia data, we can read both of those files back in and make a consolidated file
#with all of the data we have.

#####
#first, read the EOL data into a dictionary
eol_diets = {}
with open('allison_song_eol_species_data.csv', 'r') as f:    #open the file we put the eol data in
    file = csv.DictReader(f)
    for line in file:
        name = ""
        species = line['SPECIES']                     #get the species out of the line
  #      print(species)
        name = species
        eol_diets[name] = {}                         #make an entry in the dictionary for that species
        eol_diets[name]['diet'] = line['DATA']       #and fill in the diet based on the eol data we have for that speceis

#print to check that it worked
for entry in eol_diets:
    print(entry)
    print(eol_diets[entry])
    
    
#####
#then read the wikipedia data into a dictionary
wikipedia_diets = {}
with open('allison_song_wikipedia_diets.csv', 'r') as f:
    file = csv.DictReader(f)
    for line in file:
        name = line['Species name']
     #   name = (line['Species name'], line['Common name'])
        
        wikipedia_diets[name] = {}
        wikipedia_diets[name]['diet mentions'] = line['Mentions']
        wikipedia_diets[name]['likely diet'] = line['Most likely diet']

#print to check that it worked
for entry in wikipedia_diets:
    print(entry)
    print(wikipedia_diets[entry])

    
#####
#then, make a consolidated dictionary of both the EOL and wikipedia data
all_diets = {}
for species in species_list_non_dict:
    #make an entry for each species we have with slots for wikipedia data, eol data, and a diet guess
    try:
        species = species[0]
        all_diets[species] = {}
        all_diets[species]['wikipedia'] = []
        all_diets[species]['eol'] = []
        all_diets[species]['diet_guess'] = ""
    except IndexError:
        print("blank")

#go through the wikipedia diets and add the data to all_diets
for species in wikipedia_diets:
    species = [species]            #make species a list so the indexing works
    all_diets[species[0]]['wikipedia'] = wikipedia_diets[species[0]]['diet mentions']
    #if there's no diet guess for this species, fill in the wikipedia diet guess
    if all_diets[species[0]]['diet_guess'] == "":
        all_diets[species[0]]['diet_guess'] = wikipedia_diets[species[0]]['likely diet']

#go through the eol diets and add teh data to all_diets
for species in eol_diets:
    all_diets[species]['eol'] = eol_diets[species]['diet']

    
#and print all_diets so we can check it worked
for species in all_diets:
    print(species)
    print(all_diets[species])

    
    
#####store consolidated data in a .csv##########
#write the data we have to a .csv
with open('allison_song_all_species_data.csv', 'w') as f:
    writer = csv.writer(f)
    
    header = ("species name", "Wikipedia data", "EOL data", "diet guess")
    writer.writerow(header)
    
    for entry in all_diets:
        row = ""
        species = entry
        wiki = all_diets[entry]['wikipedia']
        eol = all_diets[entry]['eol']
        guess = all_diets[entry]['diet_guess']
        row = (species, wiki, eol, guess)
        writer.writerow(row)
    
  

########POST PROCESSING###############
#finalize diet guesses and examine the data more thoroughly to try to categorize "undefined" diets


####first, we have to read in the species data####
u_diets = {}         #dictionary to hold all the species with an "undefined" diet type

with open('allison_song_all_species_data.csv', 'r') as f:     #open the file with the EOL/wikipedia data and the diet guesses for each species
    
    next(f)    #skip the header
    
    reader = csv.reader(f)
    
    for row in reader:
        #filter out the undefined diets
        if row[-1] == "undefined":
  #          print(row)
            species = row[0]
            u_diets[species] = []               #create an entry for the undefined species
            if row[1] != []:                    #and add the EOL and wikipedia data, if it's there
                u_diets[species].append(row[1])
            if row[2] != []:
                u_diets[species].append(row[2])


                
#####first, look through the entries for species that have one of the diet categories listed above. These will be stored in "diet_words"
#Also record how many times each diet category is mentioned--many of these undefined species fall under multiple categories########

diet_words = {}

#go through the species data and look for existing keywords
for species in u_diets:
    print(species)
    for item in u_diets[species]:    #for each dataset (EOL, wikipedia) for each species
        print(item)
        for list_ in all_diet_query:   #for the lists of each diet category (carnivore, herbivore, etc.)
            for entry in list_:           #for each diet word in the diet category
                if entry in item.lower():          #if that diet word is in the EOL or wikipedia dataset
                    if species not in diet_words:
                        diet_words[species] = {}    #give that species an entry in diet_words
                    print(entry, '\n')
                    if entry not in diet_words[species]:  #and add the diet word and its count to the species in diet_words
                        diet_words[species][entry] = 0
                    diet_words[species][entry] += 1

   

########the next step is to look at the entries that don't have those convenient keywords and use a more specialized list to try to define their diet type.#####

m_diets = {}            #m_diets for mystery diets
for item in u_diets:
    if item not in diet_words:          #add all the species + data that didn't have blatant keywords (didn't get into diet_words) to m_diets
        m_diets[item] = u_diets[item]  

        
        
######definining new sets of keywords########
adhoc_carnivore = ["fish", "meat", "invertebrates", "insects", "crabs", "crustaceans", "snake", "mammal", "frog", "bird", "arthropod", "caterpillar", "beetle", "prey"]
adhoc_herbivore = ["fruit", "seed", "flower", "leaves", "leaf,", "plant", "wood", "nectar", "tree", "shrub", "twig", "foliage", "bark", "berries", "leaf litter", "pollen", "seeds", "algae", "mosses", "sap", "brassicas", "spurge", "lichens", "iguana", "tortoise"]
adhoc_omnivore = ["eggs", "fungi"]
adhoc_scavenger = ["dung", "feces", "faeces"]
adhoc_diet_query = (adhoc_carnivore, adhoc_herbivore, adhoc_omnivore, adhoc_scavenger)
keyphrases = ["feed on", "feeds on", "feeding on"]



###############go through m_diets species data and look for diet words (the ones defined in the ad hoc lists above), keeping track of counts##########
#pretty much exactly the same thing we did with diet_words
m_diet_words = {}
for species in m_diets:
    for item in m_diets[species]:
  #      print(item)
        diet_found = False              #boolean to keep track of whether we found any diet words or not
        for list_ in adhoc_diet_query:
            for entry in list_:
                if entry in item and "prey of" not in item:
                    diet_found = True
                    if species not in m_diet_words:
                        m_diet_words[species] = {}
                    if entry not in m_diet_words[species]:
                        m_diet_words[species][entry] = 0
                    m_diet_words[species][entry] += 1
        #if we find a phrase like "feed on", it's usu vy specific, so just add the whole sentence to the dictionary rather than trying to find a specific diet word
        if diet_found == False:
            for phrase in keyphrases:
                if phrase in item:
                    if species not in m_diet_words:
                        m_diet_words[species] = {}
                    if item not in m_diet_words[species]:
                        m_diet_words[species][item] = 0
                    m_diet_words[species][item] += 1
              #      print(entry, item)

for species in m_diet_words:
    print(species)
 #   print(m_diets[species])
    print(m_diet_words[species])


    
##########create the inverse of the ad hoc lists so that we can reverse-categorize species in m_diet_words based on what specific foods they were found to consume#########
searchable_diet_keywords = {}
searchable_diet_keywords['carnivore'] = ["fish", "meat", "invertebrates", "insects", "crabs", "crustaceans", "snake", "mammal", "frog", "bird", "arthropod", "caterpillar", "beetle", "prey", "carnivore", "carnivorous", 'Carnivorous', 'Carnivore', 'bird of prey', 'predatory', 'carnivora', 'amphibian', 'amphibians', 'carnivores', 'reptile', 'cephalopod']
searchable_diet_keywords['herbivore'] = ["fruit", "seed", "flower", "leaves", "leaf,", "plant", "wood", "nectar", "tree", "shrub", "twig", "foliage", "bark", "berries", "leaf litter", "pollen", "seeds", "algae", "mosses", "sap", "brassicas", "spurge", "lichens", "herbivore", "herbivorous", "Herbivore", "Herbivorous", 'tortoise', 'iguana']
searchable_diet_keywords['omnivore'] = ["eggs", "fungi", "omnivore", "omnivorous", "Omnivore", "Omnivorous"]
searchable_diet_keywords['scavenger'] = ["dung", "feces", "faeces", "Scavenge", 'scavenge', 'detritivore', 'Detritivore', 'detritivorous', 'Detritivorous', 'carrion', 'Carrion', 'detrivorous']
searchable_diet_keywords['insectivore'] = ["insectivore", "Insectivore", 'insectivorous', "Insectivorous", 'entomophagous', 'spider']
searchable_diet_keywords['frugivore'] = ["frugivore", "Frugivore", 'frugivorous', 'Frugivorous']
searchable_diet_keywords['bloodfeeder'] = ["blood feeder", "Blood feeder", "Hematophagy", "hematophagy"]
searchable_diet_keywords['granivore'] = ["granivore", "Granivore", "granivorous", "Granivorous"]
searchable_diet_keywords['nectarivore'] = ["nectarivore", "Nectarivore", "nectarivorous", "Nectarivorous"]
searchable_diet_keywords['folivore'] = ["folivore", "Folivore", "folivorous", "Folivorous", "folivory", "Folivory"]
searchable_diet_keywords['gummivore'] = ["gummivore", "Gummivore", "gummivorous", "Gummivorous", "gummivory", "Gummivory"]
searchable_diet_keywords['filterfeeder'] = ["filter feeder", "Filter feeder", "filter feed", "Filter feed", 'clam ', 'mollusk ']
    
    
    
    
    
    
################go through m_diet_words and diet_words and recategorize them into carnivore, herbivore, etc., with counts###############

m_diet_categories = {}               #create a new dictionary to hold the categorization of the m_diets data
for species in m_diet_words:
    m_diet_categories[species] = {}  #add each species in m_diet _words to m_diet_categories
  #  print(species)
    for entry in m_diet_words[species]:              #for each diet word in m_diet_words
   #     print(entry, m_diet_words[species][entry])
        for list_ in searchable_diet_keywords:           #for each list of diets (carnivore, etc.)
            if entry in searchable_diet_keywords[list_]:  #if the current diet word is in the current list
                if list_ not in m_diet_categories[species]:  #if the list title (carnivore, herbivore, etc.) isn't already in m_diet_categories
                    m_diet_categories[species][list_] = 0   #add the diet type to m_diet_categories
                m_diet_categories[species][list_] += 1     #and keep track of how many times that category has appeared
                #*****could also change this to add the m_diet_words count--so if insects shows up 3 times and plants 1, it reflects that****

#for species that have counts of both carnivore and herbivore, class them as omnivores
for species in m_diet_categories:
    if "carnivore" in m_diet_categories[species] and "herbivore" in m_diet_categories[species]:
        m_diet_categories[species]['omnivore'] = m_diet_categories[species]['carnivore'] + m_diet_categories[species]['herbivore']
        del m_diet_categories[species]['carnivore']
        del m_diet_categories[species]['herbivore']

        
#now do the same thing for diet_words
u_diet_categories = {}
for species in diet_words:
    u_diet_categories[species] = {}
    for entry in diet_words[species]:
        for list_ in searchable_diet_keywords:
            if entry in searchable_diet_keywords[list_]:
                if list_ not in u_diet_categories[species]:
                    u_diet_categories[species][list_] = 0
                u_diet_categories[species][list_] += 1

for species in u_diet_categories:
    if "carnivore" in u_diet_categories[species] and "herbivore" in u_diet_categories[species]:
        u_diet_categories[species]['omnivore'] = u_diet_categories[species]['carnivore'] + u_diet_categories[species]['herbivore']
        del u_diet_categories[species]['carnivore']
        del u_diet_categories[species]['herbivore']
    print(species)
    print(u_diet_categories[species])

    
    
###############now that each species has a list of mentioned diets, put them all back into one dictionary###############
#which means adding m_diet_categories back into u_diet_categories
for entry in m_diet_categories:
    if entry not in u_diet_categories:
        u_diet_categories[entry] = m_diet_categories[entry]
print(len(u_diet_categories))
    
    
for entry in u_diet_categories:
    try:
        del u_diet_categories[entry]['likely diet']
    except KeyError:
        print('fine')
    print(entry, u_diet_categories[entry])
print(len(u_diet_categories))



############define broad categories--so e.g. something that's both a frugivore and a folivore is an herbivore###########
broad_herbivore = ['frugivore', 'herbivore', 'granivore', 'nectarivore', 'folivore']
broad_omnivore = ['omnivore', 'gummivore', 'filter feeder']
broad_carnivore = ['carnivore', 'insectivore', 'bloodfeeder', 'scavenger']

#for ease of use later, combine these broad categories into a dictionary
broad_categories = {}
broad_categories['herbivore'] = broad_herbivore
broad_categories['omnivore'] = broad_omnivore
broad_categories['carnivore'] = broad_carnivore

print(broad_categories)
    
    
    
    
###########now, the final step is to look at those entries that have multiple diet types and try to pick the most likely diet/generalize to the highest level of the diet###########
#this is done by working with the counts of the diet types we've collected
u_diets_finished = {}
for species in u_diet_categories:
    print("\n")
    print(species)
    diets = []                       #list to hold the diets that were mentioned for the species
    likely_diet = ('filler', 1)       #a filler that will replaced by the most common diet
    threshold = 0
 #   print(species)
    u_diets_finished[species] = {}
 #   print(u_diet_categories[species])
    for entry in u_diet_categories[species]:      #for each diet type found for the species
  #      print(entry, u_diet_categories[species][entry])
        diets.append(entry)                       #add the diet type to 'diets'
  #      print(type(u_diet_categories[species][entry]))

        #if "omnivore" is in there, just assume it's an omnivore
        if entry == 'omnivore':
            u_diets_finished[species]['likely_diet'] = 'omnivore'
            break
            
        #otherwise, if there's a value that's greater than the others, keep the greatest value
        elif u_diet_categories[species][entry] > likely_diet[1]:
            u_diets_finished[species]['likely_diet'] = entry
            #threshold is the difference between the highest count and the previous highest count
            threshold = likely_diet[1] - u_diet_categories[species][entry]
            likely_diet = (entry, u_diet_categories[species][entry])
    
    #if multiple diets were found and the threshold of difference is less than 2
    if len(diets) > 1 and threshold < 2 and threshold > -2:
        print(diets)
        print(threshold)
     #   types = set()
        types = []
        eats = ""
        for item in diets:                      #go through each mentioned diet type and see which broad categories were mentioned
            for category in broad_categories:
                if item in broad_categories[category]:
        #            print(item)
           #         types.add(category)
                    types.append(category)
                    eats = category
        if len(types) > 1:                #if more than one broad diet type was mentioned (aka, if carnivore and herbivore were both mentioned)
      #      print(species)
            counter = Counter(types)            #keep track of number of times each element appears
            print(counter)
            print(types)
            ordered = counter.most_common()   #put the counter in order of highest to lowest
            highest = ordered[0]              #and get the highest number
            try:
                next_highest  = ordered[1]
                if highest[1] - next_highest[1] >= 1:   #if highest diet type is 1 or higher than the next diet type
                    likely_diet = highest[0]           #take highest element--since they're sorted into types, most common type is probably our best guess?
                else:                                 #if it's tied, call it an omnivore
                    likely_diet = "omnivore"
            except IndexError:
                likely_diet = highest[0]
           
            u_diets_finished[species]['likely_diet'] = likely_diet   #and add that categorization to the dictionary
     #       print(likely_diet)
        else:                                                        #if only one broad category was found, add that category to the dictionary
            likely_diet = types
            u_diets_finished[species]['likely_diet'] = likely_diet
        print(likely_diet)
      #      print(species)
       #     print(u_diet_categories[species])
        #    print(types)
         #   print(likely_diet)
           
    
    
############finalizing and storing data################### 
#now that we have updated diets in u_diets_finished, we can:
    #read in the original .csv with the undefined diets
    #go through and update the entries with the diet info in u_diets_finished
    #read the updated dictionary into a new .csv file

#read in original file

cat_diets = {}     #dictionary to hold the species data (cat for soon-to-be-categorized)

with open('allison_song_all_species_data.csv', 'r') as f:
    
    next(f)  #skip the header
    
    reader = csv.reader(f)
    count = 0
    unfound = 0
    
    for row in reader:
        try:
            species = row[0]
        except IndexError:
            print("blank")
        if species not in cat_diets:  #add species to cat_diets
            cat_diets[species] = []
            
        #find the undefined diets and, if a more specific diet was found, update the diet type
   #     print(row)
        if row[-1] == "undefined":
            if species in u_diets_finished:
                count += 1
                print(species)
                try:
                    print(u_diets_finished[species]['likely_diet'])
                    del row[-1]                                     #delete "undefined"
                    diet = u_diets_finished[species]['likely_diet']
                    row.append(diet)
                except KeyError:
                    print('remains undefined')
                    unfound += 1
            
            cat_diets[species] = row         #put in remaining diet data (eol, wiki, etc.)
        
        else:      #if the diet is already defined, keep everything as is
            cat_diets[species] = row
    print(count)
    print(unfound)
            
    
#last, write the updated data in cat_diets to a new .csv
with open('allison_song_all_diets_categorized.csv', 'w') as f:
    writer = csv.writer(f)
    for species in cat_diets:
        row = []
        row.append(species)
        for item in cat_diets[species]:
            row.append(item)
        writer.writerow(row)
    
    
