import csv
import glob
import openmeteo_requests
import datetime
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

daysOfWeek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
#Specfic to The Bounty Pub
ExcludeList = ["", "Description", "1 Scoop Kellys", "2 scoop Kellys", "Bacon Fries 24g", "Biscuit packs", "Black Pudding & Mustard Fiddlers Crisps 40g", "Bombay Sapphire Single", "Bombay Sapphire Double", "Cheese & Onion Fiddlers Crisps 40g", "Chilli nuts", "Chilly Billy ", "Cornetto Classico", "Cornetto Mint", "Cornetto Strawberry", "Doggie Bags", "Dry Roasted Nuts", "Exhibit rose", "FAB", "Feast", "Fruit Pastille ", "Fruity Rainbow", "Gin 0% Single", "Gin 0% Double", "Gordons Lemon Single", "Gordons Gin Single", "Gordons Gin Double", "Gordons Orange Double", "Gordons Orange Single", "Gordons Peach Double ", "Gordons Peach Single", "Gordons Pink Double", "Gordons Pink Single", "Gordons Gin Single", "Greenalls Double", "Hendricks Single", "Hendricks Double", "Ice Cream", "Kleidal Chenin blanc", "Kit Kat 41.5g", "Lion Bar 50g", "Magnum Almond", "Magnum Classic", "Magnum Mint ", "Magnum White Chocolate", "Montguéret Tête Det", "Mini Cheddars 50g", "Place du village white", "Pork Scratchings", "Quavers", "Rountrees Black Current Push Up", "Rountrees Fruit Stack", "Rountrees Orange Push Up", "Salted Cashews 50g", "Salted Nuts 50g", "Scampi Fries 27g", "Sea Salt & Vinegar Fiddlers Crisps 40g", "Sea Salt Fiddlers Crisps 40g", "Smartie Push Up", "Smarties", "Solero", "Sweet Chilli Fiddlers Crisps 40g", "Tanqueray Single", "Tanqueray Double", "Twiglets 45g", "Twix 50g", "Watermelon Rowntrees"]

#Extracts the event dates from the eventDates.csv file and returns them as a list. If the file does not exist, it returns an empty list.
def loadEventDates():
    try:
        with open("eventDates.csv", "r") as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        return []

eventDates = loadEventDates()

#Reads all the csv files in the DailySalesFiles folder and returns a dictionary of items and their total orders, the total number of files, and the number of files for the specified day of the week. If isTotalAverage is True, it will return the total orders for all days.
def readFiles(dayOfWeek, isTotalAverage):
    itemList = {}
    files = glob.glob("DailySalesFiles/*.csv")
    totalnumfiles = 0
    dayNumFiles = 0
    for file in files:
        totalnumfiles += 1
        fileDate = file[16:26]
        date = datetime.date.fromisoformat(fileDate)
        if(date.weekday() == dayOfWeek or isTotalAverage == True):
            dayNumFiles += 1
            with open(file, newline="") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if(row[2] not in ExcludeList):
                        if row[2] in itemList:
                            itemList.update({row[2]: int(itemList[row[2]]) + int(row[6])})
                        else:
                            itemList.update({row[2]: int(row[6])})

    itemList = {k: v for k, v in sorted(itemList.items(), key=lambda item: item[0])}
    return itemList, totalnumfiles, dayNumFiles

def printDict(inDict):
    for x, y in inDict.items():
        print(x, y)

#Calculates the average orders for each item in the input dictionary. Returns a new dictionary with the average orders.
def AverageOrders(inDict, numfiles):
    averagesList = inDict.copy()
    for item, amount in averagesList.items():
        averagesList[item] = round((amount / numfiles), 2)
    return averagesList

#Gets the weather data for the specified date. If forecast is True, it will get the forecast data, otherwise it will get the historical data. Returns a dictionary with the maximum temperature and rain sum.
def getWeather(date, forecast):
    openmeteo = openmeteo_requests.Client()
    if forecast == True:
        url = "https://api.open-meteo.com/v1/forecast"
    else:
        url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": 51.576367630995136,
        "longitude": -0.7164894580753421,
        "daily": ["temperature_2m_max", "rain_sum"],
        "start_date": date,
        "end_date": date
    }
    try:
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]
        daily = response.Daily()
        return { "temp_max": daily.Variables(0).ValuesAsNumpy()[0], "rain": daily.Variables(1).ValuesAsNumpy()[0] }
    except Exception:
        print("Could not get data for", date)
        return { "temp_max": 0, "rain": 0 }

#Creates a dataset from the csv files in the DailySalesFiles folder. It reads each file, gets the total orders, weather data, and other relevant information, and appends it to a list. The list is then converted to a pandas DataFrame and returned.
def createDataSet():
    dataset = []
    files = glob.glob("DailySalesFiles/*.csv")

    for file in files:
        fileDate = file[16:26]

        totalOrders = 0
        with open(file, newline="") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if(row[2] not in ExcludeList):
                        totalOrders += int(row[6])

        weather = getWeather(fileDate, False)
        date = datetime.date.fromisoformat(fileDate)

        row = {
            "Date": fileDate,
            "Orders": totalOrders,
            "MaxTemp": round(float(weather["temp_max"]), 1),
            "Rain": weather["rain"],
            "DayofWeek": date.weekday(),
            "Month": date.month,
            "IsEventOn" : True if fileDate in eventDates else False
        }

        dataset.append(row)
        dataset = sorted(dataset, key=lambda x: x["Date"])

    return pd.DataFrame(dataset)

#Uses a Random Forest Regressor to predict the number of orders for a given date and whether there is an event on that date. It first gets the dataset, then fits the model with the relevant features and target variable. It then gets the weather data for the specified date, creates a DataFrame with the features, and uses the model to make a prediction. The predicted number of orders is returned.
def prediction(date, eventOn):
    dataset = getDataSet()

    features = [
        "MaxTemp",
        "Rain",
        "DayofWeek",
        "Month",
        "IsEventOn"
    ]

    x = dataset[features]
    y = dataset["Orders"]

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42
    )

    model.fit(x, y)

    weather = getWeather(date, True)
    future = pd.DataFrame([{
        "MaxTemp": round(float(weather["temp_max"]), 1),
        "Rain": weather["rain"],
        "DayofWeek": date.weekday(),
        "Month": date.month,
        "IsEventOn": eventOn
    }])

    prediction = model.predict(future)[0]
    return(prediction)

#A text based menu system that allows the user to print the average orders or top orders for all days.
def AllDaysMenu():
    itemList, numfiles, _ = readFiles(-1, True)
    while True:
        print("All Days Menu")
        inp = input("1.All Days Average\n2.All Days Top Orders\n3.Return to Main Menu\n:")
        if inp == "1":
            printDict(AverageOrders(itemList, numfiles))
            break
        elif inp == "2":
            itemList = {k: v for k, v in sorted(itemList.items(), key=lambda item: item[1], reverse=True)}
            printDict(itemList)
            break
        elif inp == "3":
            break
        else:
            print("Command not valid")

#A text based menu system that allows the user to print the average orders or top orders for a specific day of the week.
def SpecificDayMenu():
    while True:
        print("Specific Day Menu")
        while True:
            specDay = input("Enter a specific day of the week\n:")
            if(specDay[0].upper() + specDay[1:].lower() in daysOfWeek):
                break
        specDayNum = daysOfWeek.index(specDay[0].upper() + specDay[1:].lower())
        itemList, _, dayNumFiles = readFiles(specDayNum, False)
        inp = input("1.Specific Day Average\n2.Specific Day Top Orders\n3.Return to Main Menu\n:")
        if inp == "1":
            printDict(AverageOrders(itemList, dayNumFiles))
            break
        elif inp == "2":
            itemList = {k: v for k, v in sorted(itemList.items(), key=lambda item: item[1], reverse=True)}
            printDict(itemList)
            break
        elif inp == "3":
            break
        else:
            print("Command not valid")

#A text based menu system that allows the user to input a date and whether there is an event on that date, and then predicts the number of orders for that date using the prediction function.
def PredictionMenu():
    while True:
        inpDate = input("Enter date in form YYYY-MM-DD\n:")
        try:
            inpDate = datetime.date.fromisoformat(inpDate)
            break
        except ValueError:
            print("Invalid date")
    isEvent = input("Is there an event on?\nY/N:")
    if isEvent[0].upper() == "Y":
        eventOn = True
    else:
        eventOn = False
    orderPrediction = round(float(prediction(inpDate, eventOn)))
    print(orderPrediction)

#Returns the dataset as a pandas DataFrame. If the dataset.csv file does not exist, it creates the dataset and saves it to the file.
def getDataSet():
    try:
        dataset = pd.read_csv("dataset.csv")
    except FileNotFoundError:
        dataset = createDataSet()
        dataset.to_csv("dataset.csv", index=False)
    return dataset

def updateDataSet():
    dataset = createDataSet()
    dataset.to_csv("dataset.csv", index=False)

#A text based menu system that allows the user to input a date and adds it to the eventDates list and saves it to the eventDates.csv file. It then updates the dataset.
def addEventDate():
    while True:
        eventDate = input("Enter date in form YYYY-MM-DD\n:")
        try:
            eventDate = datetime.date.fromisoformat(eventDate)
            break
        except ValueError:
            print("Invalid date")
    eventDates.append(eventDate)
    with open("eventDates.csv", "a") as file:
        file.write(datetime.date.isoformat(eventDate) + "\n")
    updateDataSet()

#A text based main menu that allows the user to navigate to the different menus and functions of the program.
    print("Welcome message")
    while True:
        inp = input("1.All Days Menu\n2.Specific Day Menu\n3.Order Prediction\n4.Display Dataset\n5.Update Dataset\n6.Add Event on Date\n7.Quit\n:")
        if inp == "1":
            AllDaysMenu()
        elif inp == "2":
            SpecificDayMenu()
        elif inp == "3":
            PredictionMenu()
        elif inp == "4":
            print(getDataSet())
        elif inp == "5":
            updateDataSet()
        elif inp == "6":
            addEventDate()
        elif inp == "7":
            return False
        else:
            print("Command not valid")

while True:
    if mainMenu() == False:
        break