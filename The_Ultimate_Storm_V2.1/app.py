from flask import Flask, render_template, request
from game import Setup_Game, Get_Pawn_Positions

app = Flask(__name__)
Player_Data = None
Game_State = None
Player_Data_History = []
Game_State_History = []

@app.route("/")
def Home():
    return render_template("index.html")



# Start game
@app.route("/start_game", methods=["POST"])
def Start_Game():
    global Player_Data
    global Game_State
    global Player_Data_History
    global Game_State_History

    # Read webpage inputs for player names and pawn colours
    n_Players = int(request.form["n_players"])
    Player_Names = []
    Colours_List = []
    for i in range(1, n_Players+1):
        Player_Name = request.form[f"player_{i}_name"]
        Player_Colour = request.form[f"player_{i}_colour"]
        Player_Names.append(Player_Name)
        Colours_List.append(Player_Colour)
    
    # Validate player names and pawn colours
    if len(Colours_List) != len(set(Colours_List)):
        return "Each player must choose a different colour."
    if len(Player_Names) != len(set(Player_Names)):
        return "Each player must have a different name."
    if Player_Name == "":
        return "Player names cannot be empty."
    Player_Colours = dict(zip(Player_Names, Colours_List))

    # Setup game
    (Player_Data, Game_State, Player_Data_History, Game_State_History) = Setup_Game(n_Players, Player_Names, Player_Colours)

    # Setup pawns
    Pawns = Get_Pawn_Positions(Player_Data)

    # Display game
    return render_template("game.html", Player_Data=Player_Data, Game_State=Game_State, Pawns=Pawns)



if __name__ == "__main__":
    app.run(debug=True, port=5000)