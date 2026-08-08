import csv
import glob

itemList = {}
ExcludeList = ["", "Description", "1 Scoop Kellys", "2 scoop Kellys", "Bacon Fries 24g", "Biscuit packs", "Black Pudding & Mustard Fiddlers Crisps 40g", "Bombay Sapphire Single", "Bombay Sapphire Double", "Cheese & Onion Fiddlers Crisps 40g", "Chilli nuts", "Chilly Billy ", "Cornetto Classico", "Cornetto Mint", "Cornetto Strawberry", "Doggie Bags", "Dry Roasted Nuts", "Exhibit rose", "FAB", "Feast", "Fruit Pastille ", "Fruity Rainbow", "Gin 0% Single", "Gin 0% Double", "Gordons Lemon Single", "Gordons Gin Single", "Gordons Gin Double", "Gordons Orange Double", "Gordons Orange Single", "Gordons Peach Double ", "Gordons Peach Single", "Gordons Pink Double", "Gordons Pink Single", "Gordons Gin Single", "Greenalls Double", "Hendricks Single", "Hendricks Double", "Ice Cream", "Kleidal Chenin blanc", "Kit Kat 41.5g", "Lion Bar 50g", "Magnum Almond", "Magnum Classic", "Magnum Mint ", "Magnum White Chocolate", "Montguéret Tête Det", "Mini Cheddars 50g", "Place du village white", "Pork Scratchings", "Quavers", "Rountrees Black Current Push Up", "Rountrees Fruit Stack", "Rountrees Orange Push Up", "Salted Cashews 50g", "Salted Nuts 50g", "Scampi Fries 27g", "Sea Salt & Vinegar Fiddlers Crisps 40g", "Sea Salt Fiddlers Crisps 40g", "Smartie Push Up", "Smarties", "Solero", "Sweet Chilli Fiddlers Crisps 40g", "Tanqueray Single", "Tanqueray Double", "Twiglets 45g", "Twix 50g", "Watermelon Rowntrees"]

path = "DailySalesFiles"
files = glob.glob(path + "/*.csv")
numfiles = 0

for file in files:
    numfiles += 1
    with open(file, newline="") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if(row[2] not in ExcludeList):
                if row[2] in itemList:
                    itemList.update({row[2]: int(itemList[row[2]]) + int(row[6])})
                else:
                    itemList.update({row[2]: int(row[6])})

itemList = {k: v for k, v in sorted(itemList.items(), key=lambda item: item[0])}

def printDict(inDict):
    for x, y in inDict.items():
        print(x, y)

def AverageOrders(inDict):
    averagesList = inDict.copy()
    for item, amount in averagesList.items():
        averagesList[item] = amount / numfiles
    return averagesList

def AllDaysMenu(itemList):
    print("All Days Menu")
    inp = input("1.All Days Average\n2.All Days Top Orders\nX.Return to Main Menu\n:")
    if inp == "1":
        printDict(AverageOrders(itemList))
    elif inp == "2":
        itemList = {k: v for k, v in sorted(itemList.items(), key=lambda item: item[1], reverse=True)}
        printDict(itemList)
    elif inp == "X":
        mainMenu(itemList) 
    else:
        print("Command not valid")
        AllDaysMenu(itemList)

def SpecficDayMenu(itemList):
    print("Specific Day Menu")
    specDay = input("Enter a specific day of the week\n:")
    inp = input("1.Specific Day Average\n2.Specific Day Top Orders\nX.Return to Main Menu\n:")
    if inp == "1":
        printDict(AverageOrders(itemList))
    elif inp == "2":
        itemList = {k: v for k, v in sorted(itemList.items(), key=lambda item: item[1], reverse=True)}
        printDict(itemList)
    elif inp == "X":
        mainMenu(itemList) 
    else:
        print("Command not valid")
        SpecficDayMenu(itemList)

def mainMenu(itemList):
    print("Welcome message")
    inp = input("1.All Days Menu\n2.Specific Day Menu\n:")
    if inp == "1":
        AllDaysMenu(itemList)
    elif inp == "2":
        SpecficDayMenu(itemList)


mainMenu(itemList)