import copy
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random

## Load Game Data

# Open cities file
Cities_DF = pd.read_csv("data/Cities_Pacific.csv")

# Open genesis points file
Genesis_DF = pd.read_csv("data/Genesis_Pacific.csv")

# Open cards files
Movement_Cards = pd.read_csv("data/Cards_Movement.csv")
Intensity_Cards = pd.read_csv("data/Cards_Intensity.csv")
Action_Cards = pd.read_csv("data/Cards_Action.csv")

# Open map grid file
Map_DF = pd.read_csv("data/Map_Pacific.csv", index_col=0)
Map_DF.index = Map_DF.index.astype(int)
Map_DF.columns = Map_DF.columns.astype(int)


## Initializing Game

# Assign genesis points and create player data dictionary
def Assign_Genesis_Points(Player_Names, Player_Colours, Genesis_DF, Map_DF):
    Taken_Positions = set()
    Player_Data = {}
    Roll_Messages = []
    for Player in Player_Names:
        while True:
            
            # Roll dice
            Roll = Dice(2)
            if Roll not in Taken_Positions:
                Taken_Positions.add(Roll)
                Message = (f"{Player} rolled {Roll} and is assigned genesis point {Roll}.")
                Roll_Messages.append(Message)
                
                # Find lat lon coordinates of genesis point
                Genesis_Row = Genesis_DF[Genesis_DF["Point"] == Roll]
                Lon = int(Genesis_Row.iloc[0]["Lon"])
                Lat = int(Genesis_Row.iloc[0]["Lat"])
                Zone = Map_DF.loc[Lat, Lon]
                
                # Initialize player data
                Colour = Player_Colours[Player]
                Player_Data[Player] = {"Colour": Colour, "Order": 0, "Round": 0, "Status": "Initialize", "Genesis Point": Roll, 
                                       "Lon": Lon, "Lat": Lat, "Zone": Zone, "Hand": [], "Cards Played This Round": [], "Max Cards": 3, 
                                       "Prev Wm2": 0, "Remainder Wm2": 0, "Prev Lon": Lon, "Prev Lat": Lat, "Prev Lon Change": 0, "Prev Lat Change": 0, 
                                       "Intensity": 25, "Peak Intensity": 25, "ACE": 0, "Landfall Costs": 0, "Landfall Cities": []}
                break
                
            # If roll result is already taken, roll again
            else:
                Message = (f"{Player} rolled {Roll}, but genesis point {Roll} is already taken. Rolling again...")
                Roll_Messages.append(Message)
    
    # Decide play order based on roll result
    Play_Order = sorted(Player_Names, key=lambda Name: Player_Data[Name]["Genesis Point"], reverse=True)
    Player_Data_Sorted = {Name: Player_Data[Name] for Name in Play_Order}
    for Order, Name in enumerate(Play_Order, start=1):
        Player_Data[Name]["Order"] = Order
    return (Play_Order, Player_Data_Sorted, Roll_Messages)

# Roll dice
def Dice(n):
    Rolls = [np.random.randint(1, 7) for _ in range(n)]
    Result = sum(Rolls)
    return (Result)

# Shuffle cards
def Shuffle_Cards(Cards):
    # Build full deck
    Deck = []
    for _, Row in Cards.iterrows():
        Deck.extend([Row["Card"]] * int(Row["Count"]))
        
    # Shuffle deck
    random.shuffle(Deck)
    return (Deck)

# Deal cards
def Deal_Cards(Deck, Player_Data, Cards_Per_Player):
    for i in range(Cards_Per_Player):
        for Player in Player_Data:
            Player_Data[Player]["Hand"].append(Deck.pop())
    return (Deck)

# Build card order
def Build_Card_Order(Movement_Cards, Intensity_Cards, Action_Cards):
    Card_Order = {}
    Position = 0
    for Card in Movement_Cards["Card"]:
        Card_Order[Card] = Position
        Position += 1
    for Card in Intensity_Cards["Card"]:
        Card_Order[Card] = Position
        Position += 1
    for Card in Action_Cards["Card"]:
        Card_Order[Card] = Position
        Position += 1
    return (Card_Order)

# Setup game state
def Setup_Game_State(n_Players, Ocean_ACE, Movement_Deck, Intensity_Deck, Action_Deck, Cities_DF):
    Game_State = {"Round": 1, "Player Position": 0, "Status": "Initialize", 
    "Movement Deck": Movement_Deck, "Intensity Deck": Intensity_Deck, "Action Deck": Action_Deck, 
    "Movement Discard": [], "Intensity Discard": [], "Action Discard": [], 
    "Ocean ACE": Ocean_ACE, "Cities Budget": {}, "Effects": [], "Game End": False}

    # Define cities budget
    for i in range(len(Cities_DF)):
        Game_State["Cities Budget"][Cities_DF.iloc[i]["City"]] = Cities_DF.iloc[i]["Initial Budget"]
    return (Game_State)

# Save player data and game state history
def Save_State(Player_Data, Game_State, Player_Data_History, Game_State_History):
    Player_Data_History.append(copy.deepcopy(Player_Data))
    Game_State_History.append(copy.deepcopy(Game_State))

# Setup game
def Setup_Game(n_Players, Player_Data, Play_Order):

    # Create card lookup dictionary
    Card_Lookup = {}
    for Card in Movement_Cards["Card"]:
        Card_Lookup[Card] = ("Movement", Movement_Cards[Movement_Cards["Card"] == Card])
    for Card in Intensity_Cards["Card"]:
        Card_Lookup[Card] = ("Intensity", Intensity_Cards[Intensity_Cards["Card"] == Card])
    for Card in Action_Cards["Card"]:
        Card_Lookup[Card] = ("Action", Action_Cards[Action_Cards["Card"] == Card])
    Card_Order = Build_Card_Order(Movement_Cards, Intensity_Cards, Action_Cards)

    # Shuffle cards
    Movement_Deck = Shuffle_Cards(Movement_Cards)
    Intensity_Deck = Shuffle_Cards(Intensity_Cards)
    Action_Deck = Shuffle_Cards(Action_Cards)

    # Deal cards
    Movement_Deck = Deal_Cards(Movement_Deck, Player_Data, 4)
    Intensity_Deck = Deal_Cards(Intensity_Deck, Player_Data, 4)
    Action_Deck = Deal_Cards(Action_Deck, Player_Data, 2)

    # Define ocean ACE
    if n_Players == 2:
        Ocean_ACE = 1500
    elif n_Players == 3:
        Ocean_ACE = 2000
    elif n_Players == 4:
        Ocean_ACE = 2400
    elif n_Players == 5:
        Ocean_ACE = 2500

    # Setup game state
    Game_State = Setup_Game_State(n_Players, Ocean_ACE, Movement_Deck, Intensity_Deck, Action_Deck, Cities_DF)
    Game_State["Play Order"] = Play_Order

    # Save player data and game state history
    Player_Data_History = []
    Game_State_History = []
    Save_State(Player_Data, Game_State, Player_Data_History, Game_State_History)
    return (Player_Data, Game_State, Player_Data_History, Game_State_History)

# Get pawns position
def Get_Pawn_Positions(Player_Data):
    Position_Groups = {}
    for Player in Player_Data:
        Position = (Player_Data[Player]["Lon"], Player_Data[Player]["Lat"])
        if Position not in Position_Groups:
            Position_Groups[Position] = []
        Position_Groups[Position].append(Player)

    Pawns = []
    for Position, Players in Position_Groups.items():
        Lon, Lat = Position
        # One player in gridbox
        if len(Players) == 1:
            Player = Players[0]
            X, Y = Board_Position(Lon, Lat)
            Pawns.append({"Player": Player, "X": X, "Y": Y, "Colour": Player_Data[Player]["Colour"]})

        # Multiple players in same gridbox
        else:
            Offsets = [(0.25, 0.25), (-0.25, -0.25), (0.25, -0.25), (-0.25, 0.25), (0, 0)]
            for i, Player in enumerate(Players):
                Lon_Offset, Lat_Offset = Offsets[i]
                X, Y = Board_Position(Lon + Lon_Offset, Lat + Lat_Offset)
                Pawns.append({"Player": Player, "X": X, "Y": Y, "Colour": Player_Data[Player]["Colour"]})
    return (Pawns)

# Calculate pawns position on board
def Board_Position(Lon, Lat):
    Min_Lon = 98
    Max_Lon = 160
    Min_Lat = 0
    Max_Lat = 44
    Left = 2.5
    Right = 98.5
    Top = 1.0
    Bottom = 96.7
    Lon_Frac = ((Lon - Min_Lon) / (Max_Lon - Min_Lon))
    Lat_Frac = ((Max_Lat - Lat) / (Max_Lat - Min_Lat))
    X = Left + Lon_Frac * (Right - Left)
    Y = Top + Lat_Frac * (Bottom - Top)
    return (X, Y)