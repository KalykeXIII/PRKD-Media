import lupa


lua = lupa.LuaRuntime()

def read_lua_from_file(file_name):
    # Read a Lua script from file
    # And return the string
    pass

class Coverage:
    """
    This class object is to be used as a tool for all tournaments covered by PRKD Media.
    The tools in this class are used to gather, transform and input data into the coverage produced in an effective, efficient and simple way

    Create a new timeline -> create all of the templates -> scorecard, leaderboard (start and finish of 9 for each), ITB if a front 9, create the base scoring overlay (may as well also add generating the commentary box in there as well, and the hole flyovers graphics)
    Enter the score ordering using a function -> ExportMarkers and strip the details from them to get the ordering of scores on the hole
    Then have this script process it and generate the stills using the scripts from before (ExportStillsAtMarkers)

    Once all of this is gathered try to place the hole and score overlays on top according to the markers

    Try and do the same thing for the score animations
    """
    def __init__(self, pdga_event_number: int, tournament_alias: str):
        self.pdga_event_number = pdga_event_number
        self.tournament_name = tournament_alias

    def add_card(self, round_number: int, player_names: list):
        # Given a round number and a list of players saves the 'card' details to the object
        # The order of the player_names list is the tee order of the group and thus the order of the scoreboard object created
        pass

    def create_itbs(self, round_number):
        pass

    def create_player_itb(self, player):
        pass

    def create_leaderboard(self, round_number):
        pass

    def create_scorecard(self, round_number, round_progress):
        pass

    def save_object(self):
        # Saves the coverage object to a JSON object that can be read on reload
        pass

    def load_object(self):
        # Loads a prior coverage project from storage
        pass
