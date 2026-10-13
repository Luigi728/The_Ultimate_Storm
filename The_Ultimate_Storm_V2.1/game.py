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
def Setup_Game_State(n_Players, Play_Order, Card_Lookup, Card_Order, 
                     Movement_Deck, Intensity_Deck, Action_Deck, Ocean_ACE, Cities_DF):
    Game_State = {"Round": 1, "Player Position": 0, "Status": "Initialize", "Play Order": Play_Order, 
    "Card Lookup": Card_Lookup, "Card Order": Card_Order, 
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
    Game_State = Setup_Game_State(n_Players, Play_Order, Card_Lookup, Card_Order, 
                                  Movement_Deck, Intensity_Deck, Action_Deck, Ocean_ACE, Cities_DF)
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



## Running Each Round

# Get current player
def Get_Current_Player(Game_State):
    Play_Order = Game_State["Play Order"]
    Position = Game_State["Player Position"]
    return (Play_Order[Position])

# Move to next player
def Advance_Player(Game_State):
    n_Players = len(Game_State["Play Order"])
    Game_State["Player Position"] += 1
    # If the last player has finished
    if Game_State["Player Position"] >= n_Players:
        Game_State["Player Position"] = 0
        Game_State["Round"] += 1
    return (Game_State)

# Start playing phase
def Start_Playing_Phase(Player_Name, Player_Data, Game_State):
    Player_Data[Player_Name]["Cards Played This Round"] = []
    Player_Data[Player_Name]["Max Cards"] = 3
    # Sort hand
    Player_Data[Player_Name]["Hand"].sort(key=lambda Card: Game_State["Card Order"][Card])
    return (Player_Data, Game_State)



## Playing Cards

# Play selected card
def Play_Selected_Card(Player_Name, Card_Index, Player_Data, Game_State, Choice=None):
    Hand = Player_Data[Player_Name]["Hand"]
    Played_This_Round = Player_Data[Player_Name]["Cards Played This Round"]

    # Check whether maximum cards have been played
    if len(Played_This_Round) >= Player_Data[Player_Name]["Max Cards"]:
        return (Player_Data, Game_State, "Maximum number of cards reached.")

    # Validate card index
    if Card_Index < 0 or Card_Index >= len(Hand):
        return (Player_Data, Game_State, "Invalid card index.")

    Card = Hand[Card_Index]

    # Check whether card is playable
    if not Is_Card_Playable(Card, Player_Name, Player_Data, Game_State):
        return (Player_Data, Game_State, f"{Card} cannot currently be played.")
    
    # Validate movement cards
    Card_Type, Card_Info = Game_State["Card Lookup"][Card]
    if Card_Type == "Movement" and bool(Card_Info.iloc[0]["Option"]):
        Allowed_Choices = {"W/E 1": ["W", "E"], "N/S 1": ["N", "S"], "W/E/N/S 1": ["W", "E", "N", "S"]}
        if Choice not in Allowed_Choices.get(Card, []):
            return (Player_Data, Game_State, "Please select a valid direction.")

    # Play card
    Played_Card = Hand.pop(Card_Index)
    Played_This_Round.append(Played_Card)

    # Apply card effect
    Find_Card_Type(Played_Card, Player_Name, Player_Data, Game_State, True)
    return (Player_Data, Game_State, f"{Player_Name} played {Played_Card}.")


# Function to find card type
def Find_Card_Type(Card_Name, Player_Name, Player_Data, Game_State, Play_Card, Choice=None):
    Card_Type, Card_Info = Game_State["Card Lookup"][Card_Name]
    
    # Play movement card
    if Card_Type == "Movement":
        if Play_Card == True:
            Message = Play_Movement_Cards(Card_Name, Card_Info, Player_Name, Player_Data, Choice)
        else:
            Message = None
        Game_State["Movement Discard"].append(Card_Name)
        
    # Play intensity card
    elif Card_Type == "Intensity":
        if Play_Card == True:
            Message = Play_Intensity_Cards(Card_Name, Card_Info, Player_Name, Player_Data)
        else:
            Message = None
        Game_State["Intensity Discard"].append(Card_Name)
        
    # Play action card
    elif Card_Type == "Action":
        if Play_Card == True:
            Message = Play_Action_Cards(Card_Name, Card_Info, Player_Name, Player_Data, Game_State, Choice)
        else:
            Message = None
        Game_State["Action Discard"].append(Card_Name)

    return (Message)


# Get playable cards
def Get_Playable_Cards(Player_Name, Player_Data, Game_State):
    Hand = Player_Data[Player_Name]["Hand"]
    Playable_Indices = [i for i, Card in enumerate(Hand) if Is_Card_Playable(Card, Player_Name, Player_Data, Game_State, Card_Lookup)]
    return (Playable_Indices)

# Function for deciding if a card is playable
def Is_Card_Playable(Card_Name, Player_Name, Player_Data, Game_State, Card_Lookup):
    # Find previous card
    if len(Player_Data[Player_Name]["Cards Played This Round"]) > 0:
        Prev_Card = Player_Data[Player_Name]["Cards Played This Round"][-1]
    else:
        Prev_Card = None

    if Card_Lookup[Card_Name][0] == "Intensity":
        # Intensity cards cannot be used on land
        if Player_Data[Player_Name]["Zone"] >= 4:
            return (False)

        # Intensity cards cannot be used when eyewall replacement in effect
        if Has_Effect(Player_Name, "Eyewall Replacement", Game_State) == True:
            return (False)

    elif Card_Lookup[Card_Name][0] == "Action":
        # Rapid intensification can only be used when previous card is an intensity card
        if Card_Name == "Rapid Intensification":
            if Prev_Card == None or Card_Lookup[Prev_Card][0] != "Intensity":
                return (False)

        # Cyclone express can only be used when previous card is a movement card
        elif Card_Name == "Cyclone Express":
            if Prev_Card == None or Card_Lookup[Prev_Card][0] != "Movement":
                return (False)

        # Wrong way round can only be used when previous card is a movement card
        elif Card_Name == "Wrong Way Round":
            if Prev_Card == None or Card_Lookup[Prev_Card][0] != "Movement":
                return (False)

        # Expand circulation can only be used when there is at least one adjacent city
        elif Card_Name == "Expand Circulation":
            if len(Find_Adj_Cities(Player_Data[Player_Name]["Lon"], Player_Data[Player_Name]["Lat"], Player_Name, Game_State)) == 0:
                return (False)

    # Else return true
    return (True)

# Find if a player has a effect
def Has_Effect(Player_Name, Effect_Name, Game_State):
    for Effect in Game_State["Effects"]:
        if Effect["Effect"] == Effect_Name and Effect["Player"] == Player_Name:
            return (True)
    return (False)



## Playing Movement Cards

# Function for playing movement cards
def Play_Movement_Cards(Card_Name, Card_Info, Player_Name, Player_Data, Game_State, Choice=None):
    Card_Row = Card_Info.iloc[0]
    Messages = [f"{Player_Name} played {Card_Name}."]

    # Find movement velocity
    if not Card_Row["Roll"] and not Card_Row["Option"]:
        Lon_Change = (Card_Info.iloc[0]["E"] - Card_Info.iloc[0]["W"]) * 2
        Lat_Change = (Card_Info.iloc[0]["N"] - Card_Info.iloc[0]["S"]) * 2
        
    # Roll dice to find movement velocity
    elif Card_Info.iloc[0]["Roll"] == True:
        Roll = Dice(1)
        Lon_Change = (Card_Info.iloc[0]["E"] - Card_Info.iloc[0]["W"]) * 2 * Roll
        Lat_Change = (Card_Info.iloc[0]["N"] - Card_Info.iloc[0]["S"]) * 2 * Roll
        Messages.append(f"{Player_Name} rolled {Roll}: {Card_Name[0]} {Roll}")
        
    # Movement wildcards: ask player to choose movement direction
    elif Card_Row["Option"]:
        if Card_Name == "W/E 1":
            Options = ["W", "E"]
        elif Card_Name == "N/S 1":
            Options = ["N", "S"]
        elif Card_Name == "W/E/N/S 1":
            Options = ["W", "E", "N", "S"]
        if Choice not in Options:
            raise (ValueError("Invalid or missing movement direction."))
        Lon_Change, Lat_Change = Movement_Choice(Choice)

    # Apply storm movement
    Landfall_Message = Apply_Movement(Lon_Change, Lat_Change, Player_Name, Player_Data, Game_State)
    Messages.append(Landfall_Message)
    return (" ".join(Messages))

# Movement wildcards choice
def Movement_Choice(Choice):
    if Choice == "W":
        return (-2, 0)
    elif Choice == "E":
        return (2, 0)
    elif Choice == "N":
        return (0, 2)
    elif Choice == "S":
        return (0, -2)
    raise ValueError(f"Invalid direction: {Choice}")

# Function for requesting movement wildcard input
def Request_Wildcard_Input(Input_Message, Options):
    while True:
        Choice = input(Input_Message).strip().upper()
        if Choice in Options:
            Lon_Change, Lat_Change = Movement_Choice(Choice)
            return (Lon_Change, Lat_Change)
        else:
            print ("Invalid choice. Please try again.")


# Function for applying storm movement
def Apply_Movement(Lon_Change, Lat_Change, Player_Name, Player_Data, Game_State):
    # Calculate new position
    Prev_Lon = Player_Data[Player_Name]["Lon"]
    Prev_Lat = Player_Data[Player_Name]["Lat"]
    New_Lon = Prev_Lon + Lon_Change
    New_Lat = Prev_Lat + Lat_Change

    # Keep within board boundaries
    New_Lon = max(99, min(159, New_Lon))
    New_Lat = max(1, min(43, New_Lat))

    # Store data
    Player_Data[Player_Name]["Prev Lon Change"] = Lon_Change
    Player_Data[Player_Name]["Prev Lat Change"] = Lat_Change
    Player_Data[Player_Name]["Prev Lon"] = Prev_Lon
    Player_Data[Player_Name]["Prev Lat"] = Prev_Lat
    
    # Move storm
    Player_Data[Player_Name]["Lon"] = New_Lon
    Player_Data[Player_Name]["Lat"] = New_Lat
    Player_Data[Player_Name]["Zone"] = Map_DF.loc[Player_Data[Player_Name]["Lat"], Player_Data[Player_Name]["Lon"]]

    # Detect landfall
    Landfall_Row = Cities_DF[(Cities_DF["Lon"] == Player_Data[Player_Name]["Lon"]) & (Cities_DF["Lat"] == Player_Data[Player_Name]["Lat"])]
    if not Landfall_Row.empty:
        return (Landfall(Player_Name, Player_Data, Game_State, Landfall_Row))


# Function for landfall
def Landfall(Player_Name, Player_Data, Game_State, Landfall_Row):
    Landfall_City = Landfall_Row.iloc[0]["City"]
    City_Name = Landfall_Row.iloc[0]["City Name"]

    # Check for City Fortress
    Fortress_Active = any(Effect["Effect"] == "City Fortress" and Effect["Player"] == Player_Name and Effect["City"] == Landfall_City 
                          and Effect["Rounds Left"] > 0 for Effect in Game_State["Effects"])
    if Fortress_Active:
        return(f"{Player_Name} has made landfall at {Landfall_City} ({City_Name}), but the city is protected by City Fortress. $0M gained.")
    
    else:
        # Calculate landfall cost
        Landfall_Cost = Player_Data[Player_Name]["Intensity"] * Landfall_Row.iloc[0]["Landfall Cost per kt"]
    
        # If player has never made landfall at this city yet
        if Landfall_City not in Player_Data[Player_Name]["Landfall Cities"]:
            
            # If remaining city budget less than landfall cost
            if Game_State["Cities Budget"][Landfall_City] < Landfall_Cost:
                Landfall_Cost = Game_State["Cities Budget"][Landfall_City]
                
            # Deduct landfall cost from city budget
            Game_State["Cities Budget"][Landfall_City] -= Landfall_Cost
            
            # Add landfall cost to player
            Player_Data[Player_Name]["Landfall Costs"] += Landfall_Cost
            Player_Data[Player_Name]["Landfall Cities"].append(Landfall_City)
            
            # Print message
            City_Name = Landfall_Row.iloc[0]["City Name"]
            if Landfall_Cost > 0:
                return (f"{Player_Name} has made landfall at {Landfall_City} ({City_Name}) and gains ${Landfall_Cost}M!")
                return (f"Remaining budget of {Landfall_City} ({City_Name}): ${Game_State["Cities Budget"][Landfall_City]}M.")
            else:
                return (f"{Player_Name} has made landfall at {Landfall_City} ({City_Name}), but {Landfall_City} is already bankrupt. $0M gained.")
    
        # If player has already made landfall at this city
        else:
            City_Name = Landfall_Row.iloc[0]["City Name"]
            return (f"{Player_Name} has already made landfall at {Landfall_City} ({City_Name}) previously. $0M gained.")



## Playing Intensity Cards

# Function for playing intensity cards
def Play_Intensity_Cards(Card_Name, Card_Info, Player_Name, Player_Data, Game_State):
    Messages = [f"{Player_Name} played {Card_Name}."]

    # Find W/m^2 amount
    if Card_Info.iloc[0]["Roll"] == False:
        Wm2 = Card_Info.iloc[0]["W/m^2"]
    # Roll dice to find W/m^2 amount
    else:
        Roll = Dice(1)
        Wm2 = Roll * 5
        Messages.append(f"{Player_Name} rolled {Roll}: + {Wm2} W/m^2")

    # Apply intensification
    Message = Apply_Intensification(Wm2, Player_Name, Player_Data)
    Messages.append(Message)
    return (" ".join(Messages))

# Function for applying intensification
def Apply_Intensification(Wm2, Player_Name, Player_Data):
    # Get current intensity and zone
    Current_Intensity = Player_Data[Player_Name]["Intensity"]
    Rem = Player_Data[Player_Name]["Remainder Wm2"]
    Zone = Player_Data[Player_Name]["Zone"]

    # Calculate intensification amount
    Intensity, Remainder = Intensify(Current_Intensity, Wm2, Rem, Zone)

    # Intensify storm
    Player_Data[Player_Name]["Intensity"] = Intensity
    if Intensity > Player_Data[Player_Name]["Peak Intensity"]:
        Player_Data[Player_Name]["Peak Intensity"] = Intensity
    Player_Data[Player_Name]["Prev Wm2"] = Wm2
    Player_Data[Player_Name]["Remainder Wm2"] = Remainder

    # Print message
    if Intensity > Current_Intensity:
        Message = (f"{Player_Name} has intensified to {Intensity} knots!")
    else:
        Message = (f"{Player_Name} remains at {Intensity} knots.")
    return (Message)

# Calculate intensification amount
def Intensify(Intensity, Wm2_New, Rem, Zone):
    Wm2 = Wm2_New + Rem
    while True:
        if Intensity < 65:
            if Zone <= 2:
                Cost = 5
            elif Zone == 3:
                Cost = 10
        elif Intensity < 100:
            Cost = 5 * Zone
        elif Intensity < 140:
            Cost = 5 * Zone + 5
        else:
            if Zone <= 2:
                Cost = 5 * Zone + 10
            elif Zone == 3:
                Cost = 30
        if Wm2 < Cost:
            break
        Intensity += 5
        Wm2 -= Cost
    return (Intensity, Wm2)



## Playing Action Cards



