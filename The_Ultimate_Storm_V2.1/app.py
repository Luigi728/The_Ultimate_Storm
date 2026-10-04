from flask import (Flask, render_template, request)
from game import (Cities_DF, Genesis_DF, Map_DF, Assign_Genesis_Points, Setup_Game, Get_Pawn_Positions)

app = Flask(__name__)
Player_Data = None
Game_State = None
Play_Order = None
Roll_Messages = None
Pending_n_Players = None
Pending_Player_Names = None
Pending_Player_Colours = None
Player_Data_History = []
Game_State_History = []

@app.route("/")
def Home():
    return (render_template("index.html"))

# Roll dice to assign genesis points and play order
@app.route("/roll_dice", methods=["POST"])
def Roll_Dice():
    global Player_Data
    global Play_Order
    global Roll_Messages
    global Pending_n_Players
    global Pending_Player_Names
    global Pending_Player_Colours

    # Read webpage inputs for player names and pawn colours
    n_Players = int(request.form["n_players"])
    Player_Names = []
    Colours_List = []
    for i in range(1, n_Players+1):
        Player_Name = request.form[f"player_{i}_name"]
        Player_Colour = request.form[f"player_{i}_colour"]
        if Player_Name == "":
            return ("Player names cannot be empty.")
        Player_Names.append(Player_Name)
        Colours_List.append(Player_Colour)
    
    # Validate player names and pawn colours
    if len(Colours_List) != len(set(Colours_List)):
        return ("Each player must choose a different colour.")
    if len(Player_Names) != len(set(Player_Names)):
        return ("Each player must have a different name.")
    Player_Colours = dict(zip(Player_Names, Colours_List))

    # Assign genesis points and play order
    (Play_Order, Player_Data, Roll_Messages) = Assign_Genesis_Points(Player_Names, Player_Colours, Genesis_DF, Map_DF)
    Pending_n_Players = n_Players
    Pending_Player_Names = Player_Names
    Pending_Player_Colours = Player_Colours

    return (render_template("index.html", n_Players=n_Players, Player_Names=Player_Names, Player_Colours=Player_Colours, 
                           Roll_Messages=Roll_Messages, Play_Order=Play_Order, Dice_Rolled=True))

# Start game
@app.route("/start_game", methods=["POST"])
def Start_Game():
    global Player_Data
    global Game_State
    global Player_Data_History
    global Game_State_History
    global Play_Order
    global Pending_n_Players

    # Setup game
    (Player_Data, Game_State, Player_Data_History, Game_State_History) = Setup_Game(Pending_n_Players, Player_Data, Play_Order)

    # Setup pawns
    Pawns = Get_Pawn_Positions(Player_Data)

    # Display game
    return (render_template("game.html", Player_Data=Player_Data, Game_State=Game_State, Pawns=Pawns))



if __name__ == "__main__":
    app.run(debug=True, port=5001)