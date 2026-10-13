from flask import (Flask, render_template, request, redirect, url_for, flash)
from game import (Cities_DF, Genesis_DF, Map_DF, Assign_Genesis_Points, Setup_Game, Get_Pawn_Positions, 
                  Get_Current_Player, Advance_Player, Start_Playing_Phase, Get_Playable_Cards, Play_Selected_Card, 
                  Is_Card_Playable, Has_Effect)

app = Flask(__name__)
app.secret_key = "development-only-secret-key"
Player_Data = None
Game_State = None
Play_Order = None
Roll_Messages = None
Pending_n_Players = None
Pending_Player_Names = None
Pending_Player_Colours = None
Player_Data_History = []
Game_State_History = []


# Display home
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

    # Render game
    return (Render_Game())


# Display game
@app.route("/game")
def Game():
    if Game_State is None:
        return (redirect(url_for("Home")))
    return (Render_Game())


# Render game
def Render_Game():
    Current_Player = Get_Current_Player(Game_State)
    Pawns = Get_Pawn_Positions(Player_Data)
    Hand = Player_Data[Current_Player]["Hand"]
    Playable_Indices = Get_Playable_Cards(Current_Player, Player_Data, Game_State)
    return render_template("game.html", Player_Data=Player_Data, Game_State=Game_State, Pawns=Pawns, 
                           Current_Player=Current_Player, Hand=Hand)


# Play card
@app.route("/play_card", methods=["POST"])
def Play_Card():
    global Player_Data
    global Game_State
    if Game_State is None:
        return redirect(url_for("Home"))
    Current_Player = Get_Current_Player(Game_State)

    # Validate card index
    try:
        Card_Index = int(request.form["card_index"])
    except (KeyError, ValueError):
        return ("Invalid card selection.", 400)
    
    # Play selected card
    Choice = request.form.get("direction")
    Player_Data, Game_State, Message = Play_Selected_Card(Current_Player, Card_Index, Player_Data, Game_State, Choice)
    flash(Message)

    return (redirect(url_for("Game")))


# End turn
@app.route("/end_turn", methods=["POST"])
def End_Turn():
    global Game_State
    if Game_State is None:
        return (redirect(url_for("Home")))
    Current_Player = Get_Current_Player(Game_State)
    print(f"{Current_Player} ended their turn.")
    Game_State = Advance_Player(Game_State)
    return (redirect(url_for("Game")))



if __name__ == "__main__":
    app.run(debug=True, port=5001)
