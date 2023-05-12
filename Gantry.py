import requests
import json
import time

# ! Virtual Gantry
# host = "http://localhost:4020"

# ! AR2
host = "http://ar2-ar.local:4020"

# TODO Home Does Not Work
def home():
    url = "/home"

    payload = json.dumps({
        "axis": None
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)


def scanSafeZone(poi):
    url = host + "/scan-safe-zone"
    payload = json.dumps({
        "poi": poi
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)

def openDoor(printer):
    url = host + "/open-door"

    payload = json.dumps({
        "printer": printer
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)

def fetchBed(bedFeederIndex):
    url = host + "/fetch-bed"
    payload = json.dumps({
        "bedFeederIndex": bedFeederIndex
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def placeBed(printer):
    url = host + "/place-bed"
    payload = json.dumps({
        "printer": printer
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def closeDoor(printer):
    url = host + "/close-door"

    payload = json.dumps({
        "printer": printer
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def retrievePrint(printer):
    url = host + "/retrieve-print"
    payload = json.dumps({
        "printer": printer
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def storePrint(shelf):
    url = host + "/store-print"
    payload = json.dumps({
        "shelf": shelf
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def getState():
    url = host + "/state"

    payload={}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    return response.text

# ! metric not step move
def relativeMove(axis, direction, speed, distance):

    url = host + "/relative-move"

    payload = json.dumps({
        "axis": axis, # "X" | "Y" | "Z"
        "direction": direction, # 0 | 1
        "speed": speed, # number
        "distance": distance # number
    })

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def doorJob(cycles):
    previous_state = "home"
    count = 0

    while (count != cycles):
        state = getState()
        print(state)

        if ('"finished":true' in state and (previous_state == "home" or previous_state == "close_door")):
            openDoor(3)
            previous_state = "open_door"

        elif('"finished":true'in state and previous_state == "open_door"):
            closeDoor(3)
            previous_state = "close_door"
            count = count + 1
            print (count, " / ", cycles, end='\r')

        time.sleep(2)


def mainWorkflows(cycles, printer):
    previous_state = "home"
    count = 0
    shelf = 1
    bedFeederIndex = 0


    ## keep running for the desired number of cycles
    while (count != cycles):

        state = getState()
        # print(state)

        if ('"finished":true' in state and (previous_state == "home" or previous_state == "store_print")):
            print("fetching bed from index ", bedFeederIndex)
            fetchBed(bedFeederIndex)
            previous_state = "fetch_bed"

        elif('"finished":true' in state and previous_state == "fetch_bed"):
            print("place bed")
            placeBed(printer)
            previous_state = "place_bed"

        elif ('"finished":true' in state and previous_state == "place_bed"):
            print("retrieve print")
            retrievePrint(printer)
            previous_state = "retrieve_print"

        elif('"finished":true' in state and previous_state == "retrieve_print"):
            print("store print on shelf ", shelf)
            storePrint(shelf)
            shelf = shelf + 2
            previous_state = "store_print"
            count = count + 1
            print (count, " / ", cycles, end='\r')

            if (count % 10 == 0):
                bedFeederIndex += 1

        time.sleep(2)


def printerWorkflows(cycles, printer):
    previous_state = "home"
    count = 0

    ## keep running for the desired number of cycles
    while (count != cycles):

        state = getState()
        # print(state)

        if ('"finished":true' in state and (previous_state == "home" or previous_state == "retrieve_print")):
            print("place bed")
            placeBed(printer)
            previous_state = "place_bed"

        elif ('"finished":true' in state and previous_state == "place_bed"):
            print("retrieve print")
            retrievePrint(printer)
            previous_state = "retrieve_print"

            count = count + 1
            print (count, " / ", cycles, end='\r')

        time.sleep(2)

def storageCartWorkflows(cycles):
    previous_state = "home"
    count = 0
    shelf = 10
    bedFeederIndex = 0
    fetches_per_index = 10


    ## keep running for the desired number of cycles
    while (count != cycles):

        state = getState()
        # print(state)

        if ('"finished":true' in state and (previous_state == "home" or previous_state == "store_print")):
            print("fetching bed from index ", bedFeederIndex)
            fetchBed(bedFeederIndex)
            previous_state = "fetch_bed"

        elif('"finished":true' in state and previous_state == "fetch_bed"):
            print("store print on shelf ", shelf)
            storePrint(shelf)
            shelf = shelf + 4
            previous_state = "store_print"
            count = count + 1
            print (count, " / ", cycles, end='\r')

            if (count % fetches_per_index == 0):
                bedFeederIndex += 1

        time.sleep(2)

def main():

    print("Your host is: ", host)

    workflow = int(input("press 1 for door job \npress 2 for main workflows \npress 3 for placebed / retrieve print\npress 4 for fetch bed / store print\npress 5 to move to safe scan zone\n"))

    if (workflow != 5):
       cycles = int(input("enter the number of cycles \n"))

    if (workflow == 1):
        print("running ", cycles, "cycles of open/close door")
        doorJob(cycles)

    elif (workflow == 2):
        print("running ", cycles, "cycles of fetch bed, place bed, retrieve print, store print")
        printer = input("\nEnter printer number:\n")
        mainWorkflows(cycles, printer)

    elif (workflow == 3):
        print("running ", cycles, "cycles of printer workflows")
        printer = input("\nEnter printer number:\n")
        printerWorkflows(cycles, printer)

    elif (workflow == 4):
        print("running ", cycles, "cycles of storage cart workflows")
        storageCartWorkflows(cycles)

    elif (workflow == 5):
        poi = input("enter the scan zone you would like to move to\n")
        scanSafeZone(poi)

main()
