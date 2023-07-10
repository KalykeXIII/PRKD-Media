# This script calculates the scoring distribution for each hole over the course of the tournament
# It takes event id and division as input
import re
import sys
import json
import pandas as pd
from operator import add
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager


score_indexing = {'Birdie+': 0, 'Birdie': 1, 'Par': 2, 'Bogey': 3, 'Bogey+': 4}

class PDGAScoreProcessor:
    def __init__(self, event_id):
        # Get the details of the PDGA page for the event
        scores_contents = get_html_body('https://www.pdga.com/apps/tournament/live/event?view=Scores&eventId={}&round=1&division=All'.format(event_id))
        # From here we want to get all of the relevant details
        # - how many rounds
        # - which divisions
        self.all_rounds = get_div_text(scores_contents.find_all('div', class_="base-control-text"))
        # Get a list of all the divisions at the event
        self.all_divisions = get_div_text(scores_contents.find_all('a', class_="dropdown-item"), field='data-division')

        # From this we store all of the pages for each round for each division both scores and stats as a JSON lookup
        # Key = division+round+['Scores'/'Stats']
        self.pages = {}

        for round in range(len(self.all_rounds)):
            for division in self.all_divisions:
                # Query the page and store the resulting object in the lookup
                try:
                    self.pages[division + str(round) + 'Scores'] = get_html_body('https://www.pdga.com/apps/tournament/live/event?view=Scores&eventId={}&round={}&division={}'.format(event_id, round, division))
                    self.pages[division + str(round) + 'Stats'] = get_html_body('https://www.pdga.com/apps/tournament/live/event?view=Stats&eventId={}&round={}&division={}'.format(event_id, round, division))
                except:
                    pass
        # Dump it to a JSON object


def get_div_text(lst, to=None, field=None):
    new_list = []
    if field:
        for i in range(len(lst)):
            new_list.append(lst[i][field])
    else:
        for i in range(len(lst)):
            if to == 'int':
                if lst[i].text == ' E ':
                    new_list.append(0)
                else:
                    new_list.append(int(lst[i].text))
            else:
                new_list.append(lst[i].text)
    return new_list

def get_html_body(url):
    # Set up the Chrome driver options
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run the browser in headless mode (without a GUI)
    service = Service(executable_path=ChromeDriverManager().install())
    # Set up the Chrome driver service
    # Start the Chrome driver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    # Load the URL in the browser
    driver.get(url)
    # Wait for the page to fully load (by waiting for the body element to be present)
    wait = WebDriverWait(driver, 30)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'table-row')))
    # Retrieve the HTML content
    html_content = driver.page_source
    # Clean up
    driver.quit()
    # Use BeautifulSoup to parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    # Return the HTML body element
    return soup

def add_round_stats_to_total(total, new):
    # Add the scores from the new round and recalculate the hole average and total scores taken
    updated_overall_stats = []
    for hole_num in range(len(new)):
        hole_avg = round((total[-1][hole_num][3] + new[hole_num][3]) / 2, 2)
        hole_scores = list(map(add, total[-1][hole_num][4], new[hole_num][4]))
        updated_overall_stats.append([total[-1][hole_num][0], total[-1][hole_num][1], total[-1][hole_num][2], hole_avg, hole_scores])
    return updated_overall_stats

def hole_difficulty_rankings(hole_details):
    # Order the holes by the 3th number - the 2th number in descending order. Spit out the holes with the difference
    score_to_par = []
    for i in range(len(hole_details)):
        hole_num = hole_details[i][0]
        to_par = round(hole_details[i][3] - hole_details[i][2], 2)
        score_to_par.append((hole_num, to_par))
    # Order the list
    ordered_holes = sorted(score_to_par, key=lambda x: x[1], reverse=True)
    return ordered_holes

def get_scoreboard(eventID, division, round):
    # TODO: In rounds that are not the first there is a Total column as well as a Round column

    # Retrieve the main body object that we will use for all subsequent queries
    scores_contents = get_html_body('https://www.pdga.com/apps/tournament/live/event?eventId={}&division={}&view=Scores&round={}'.format(eventID, division, str(round)))
    stats_contents = get_html_body('https://www.pdga.com/apps/tournament/live/event?eventId={}&division={}&view=Stats&round={}'.format(eventID, division, str(round)))
    # Total - Round + each hole up until hole selected
    # Get the number of players and the number of holes
    total_players = len(scores_contents.find_all("div", {"class": "table-row"}))
    holes_played = len(stats_contents.find_all("div", {"class": "table-row"}))
    # Get the everything into a DataFrame somehow
    all_holes_scores = scores_contents.find_all('div', class_="hole-cell")
    overall_scores = []
    for player in range(total_players):
        # Goes in order of 1st to last player in sets of n holes
        player_scores = []
        for hole in range(holes_played):
            player_scores.append(int(all_holes_scores[(player * holes_played) + hole].text))
        overall_scores.append(player_scores)
    # Get the names player-first-name player-last-name
    first_names = get_div_text(scores_contents.find_all("span", {"class": "player-first-name"}))
    last_names = get_div_text(scores_contents.find_all("span", {"class": "player-last-name"}))
    full_names = []
    for name in range(len(first_names)):
        full_names.append(first_names[name][1:-1] + last_names[name][:-1])
    # Get the hole pars
    hole_pars = get_div_text(scores_contents.find_all("div", {"class": "hole-par"}))
    # Total
    course_par = hole_pars[-1]
    # Retrieve the total score for each player
    # For rounds not equal to 1
    if round != 1:
        total_score = get_div_text(scores_contents.find_all("div", {"style": 'flex-basis: 45px; flex-grow: 1; min-width: 45px;'}), 'int')
    else:
        total_score = [""] * total_players
    # Create a DataFrame out of this information
    columns = ['Position', 'Name', 'Total Score', 'Round Score'] + hole_pars[:-1]
    leaderboard = pd.DataFrame(columns=columns)
    # Add everything we've collected to the DataFrame object
    for row in range(total_players):
        # Create a row object
        new_row = ['', full_names[row], '', ''] + overall_scores[row]
        leaderboard.loc[row] = new_row
    # Calculate each rows score to par
    # Calculate the score for each player for the round in raw strokes
    leaderboard['Total'] = leaderboard.sum(axis=1, numeric_only=True)
    # Convert relative to par
    leaderboard['Round Score'] = leaderboard['Total'] - int(course_par)
    # If the round is round one the round score is the total score
    if round == 1:
        leaderboard['Total Score'] = leaderboard['Round Score']
    else:
        leaderboard['Total Score'] = total_score
    # Now calculate the positions based on total score
    leaderboard['Position'] = leaderboard['Total Score'].rank(method='min').astype(int)
    # Order the leaderboard by Position
    leaderboard = leaderboard.sort_values(by=['Position'])
    return leaderboard

def get_partial_scoreboard(full_round_scoreboard, hole):
    # Taking a full round scoreboard and a hole recalculate the scoreboard up until that hole
    # Firstly, calculate each players score at the start of the round
    starting_scores = full_round_scoreboard[['Name', 'Total Score', 'Round Score']]
    starting_scores['Starting Score'] = starting_scores['Total Score'] - starting_scores['Round Score']
    starting_scores['Partial Score'] = 0
    # For every hole up until hole given as input alter the partial scores
    cols = full_round_scoreboard.columns
    #
    hole_score_df = pd.DataFrame()
    for i in range(hole):
        # Get the par for the hole
        par = int(cols[4 + i])
        hole_scores = pd.DataFrame(full_round_scoreboard.iloc[:, 4 + i])
        scores_to_par = hole_scores - par
        starting_scores['Partial Score'] = starting_scores['Partial Score'] + scores_to_par.iloc[:,0]
        # Create a new DF for the scores_to_par
        hole_score_df['Hole' + str(i + 1)] = scores_to_par
    # Create a new column with the starting score and partial score
    starting_scores['Current Score'] = starting_scores['Starting Score'] + starting_scores['Partial Score']
    # Add the hole scores list for the holes selected (for now front 0 or back nine)
    if hole == 9:
        starting_scores['Hole Scores'] = hole_score_df[:].values.tolist()
    elif hole == 18:
        starting_scores['Hole Scores'] = hole_score_df[:].values.tolist()
    # Take the subset of the leaderboard that is relevant
    starting_scores = starting_scores[['Name', 'Current Score', 'Partial Score', 'Hole Scores']]
    starting_scores['Position'] = starting_scores['Current Score'].rank(method='min').astype(int)
    starting_scores = starting_scores.sort_values(by=['Position'])
    return starting_scores


def get_stats_for_multiple_rounds(eventID, division, rounds):
    # Each individual round is stored
    all_stats = []
    # Just one set of hole with the details and cumulative scoring avg and actual scores
    cumulative_stats = []
    # Go through this process for each round in rounds
    for round_num in range(rounds):
        round_stats = []
        # Retrieve the main body object that we will use for all subsequent queries
        scores_contents = get_html_body('https://www.pdga.com/apps/tournament/live/event?eventId={}&division={}&view=Scores&round={}'.format(eventID, division, str(round_num + 1)))
        stats_contents = get_html_body('https://www.pdga.com/apps/tournament/live/event?eventId={}&division={}&view=Stats&round={}'.format(eventID, division, str(round_num + 1)))
        # From this calculate the number of holes played in this round
        holes_played = len(stats_contents.find_all("div", {"class": "table-row"}))
        # Also retrieve the number of players in the division
        # TODO: Deal with DNFs
        total_players = len(scores_contents.find_all("div", {"class": "table-row"}))
        # TODO: Also calculate ratings for each score from the scores page
        # For each hole retrieve all necessary details:
        # - Hole Distance
        # - Hole Par
        # - Hole Average (not related to par)
        # - The scoring distribution (eagle or better, birdie, par, bogey, double bogey or worse) -> as a percentage
        # Each hole has 6 cells, so we iterate through in intervals of 6
        hole_details = stats_contents.find_all('div', class_="cell-wrapper")
        for i in range(holes_played):
            hole_name = hole_details[6*i].text
            hole_distance = int(hole_details[6*i + 1].text)
            hole_par = int(hole_details[6*i + 2].text)
            hole_average = float(hole_details[6*i + 3].text)
            # These are in the titles of the 5th element which we can use regex for
            score_names = re.findall(r'title\=\"([^\"]+)\"', str(hole_details[6*i + 5]))
            # Convert these percentages back to whole numbers using field size
            # While doing so make a more predictable array of length 5 also
            hole_scores = [0, 0, 0, 0, 0]
            for score in range(len(score_names)):
                # Get the actual percentage out of the score string
                score_name = re.findall(r'([^\:]+)', score_names[score])
                score_pct = re.findall(r'(\d+)%', score_names[score])
                actual_scores = int(((int(score_pct[0]) / 100) * total_players) + 0.5)
                hole_scores[score_indexing[score_name[0]]] = actual_scores
            
            new_round = [hole_name, hole_distance, hole_par, hole_average, hole_scores]
            round_stats.append(new_round)
            # Append one set of these to the cumulative stats
        if round_num == 0:
            cumulative_stats.append(round_stats)
        else:
            # Add the current round stats to the cumulative stats
            cumulative_stats.append(add_round_stats_to_total(cumulative_stats, round_stats))
        all_stats.append(round_stats)
    return all_stats, cumulative_stats

def get_stats_for_round(event_id, division, round):
    round_stats = []
    # Retrieve the main body object that we will use for all subsequent queries
    scores_contents = get_html_body('https://www.pdga.com/apps/tournament/live/event?eventId={}&division={}&view=Scores&round={}'.format(event_id, division, str(round)))
    stats_contents = get_html_body('https://www.pdga.com/apps/tournament/live/event?eventId={}&division={}&view=Stats&round={}'.format(event_id, division, str(round)))
    # From this calculate the number of holes played in this round
    holes_played = len(stats_contents.find_all("div", {"class": "table-row"}))
    # Also retrieve the number of players in the division
    # TODO: Deal with DNFs
    total_players = len(scores_contents.find_all("div", {"class": "table-row"}))
    # TODO: Also calculate ratings for each score from the scores page
    # For each hole retrieve all necessary details:
    # - Hole Distance
    # - Hole Par
    # - Hole Average (not related to par)
    # - The scoring distribution (eagle or better, birdie, par, bogey, double bogey or worse) -> as a percentage
    # Each hole has 6 cells, so we iterate through in intervals of 6
    hole_details = stats_contents.find_all('div', class_="cell-wrapper")
    for i in range(holes_played):
        hole_name = hole_details[6*i].text
        hole_distance = int(hole_details[6*i + 1].text)
        hole_par = int(hole_details[6*i + 2].text)
        hole_average = float(hole_details[6*i + 3].text)
        # These are in the titles of the 5th element which we can use regex for
        score_names = re.findall(r'title\=\"([^\"]+)\"', str(hole_details[6*i + 5]))
        # Convert these percentages back to whole numbers using field size
        # While doing so make a more predictable array of length 5 also
        hole_scores = [0, 0, 0, 0, 0]
        for score in range(len(score_names)):
            # Get the actual percentage out of the score string
            score_name = re.findall(r'([^\:]+)', score_names[score])
            score_pct = re.findall(r'(\d+)%', score_names[score])
            actual_scores = int(((int(score_pct[0]) / 100) * total_players) + 0.5)
            hole_scores[score_indexing[score_name[0]]] = actual_scores
        
        new_round = [hole_name, hole_distance, hole_par, hole_average, hole_scores]
        round_stats.append(new_round)
    return round_stats


def get_all_scoring_distributions(eventID):
    # Desired output is a DataFrame with the following structure
    # Division | Round | Hole | Average | Birdie+ | Birdie | Par | Bogey | Bogey+ 
    desired_columns = ['Division', 'Round', 'Hole', 'Average', 'Birdie+', 'Birdie', 'Par', 'Bogey', 'Bogey+'] 
    # Ignore difficulty as that can be added later given difficulty can be split for the division for the round...
    all_score_details = pd.DataFrame(columns=desired_columns)
    # Determine how many rounds there are
    stats_contents = get_html_body('https://www.pdga.com/apps/tournament/live/event?eventId={}&division=All&view=Stats&round={}'.format(eventID, 1))
    rounds = stats_contents.find_all('div', class_="base-control-text")
    # Get a list of all the divisions at the event
    divisions = stats_contents.find_all('a', class_="dropdown-item")
    for round in range(len(rounds)):
        for div in divisions:
            print(div['data-division'])
            actual_div = div['data-division']
            # For each division, and each round retrieve the stats and add them to this frame
            if actual_div != 'All':
                print(get_stats_for_round(eventID, actual_div, round))
    pass

def get_hole_details(event_id, division, round):
    stats_contents = get_html_body('https://www.pdga.com/apps/tournament/live/event?eventId={}&division={}&view=Stats&round={}'.format(event_id, division, str(round)))
    holes_played = len(stats_contents.find_all("div", {"class": "table-row"}))
    hole_details = stats_contents.find_all('div', class_="cell-wrapper")
    holes = []
    for i in range(holes_played):
        hole_name = hole_details[6*i].text
        hole_distance = int(hole_details[6*i + 1].text)
        hole_par = int(hole_details[6*i + 2].text)
        holes.append({'name': hole_name, 'par': hole_par, 'distance': hole_distance})
    return holes

def get_player_details(event_id, division, round):
    pass

def json_generator(event_id, division):
    # Rounds [Holes, Players] -> this is the initial format
    # I want this to take the event ID as input and generate a JSON object including n sub objects (n being the number of rounds) each also containing 2 sub objects
    # A Players Object -> storing the name, hole scores, round score and total score for each player
    # And a Holes Object -> storing the name of the hole, the par, the distance, the scoring details (array of 5) and the hole avg
    overall_object = {}

    # Determine the number of rounds and the list of all divisions
    stats_contents = get_html_body('https://www.pdga.com/apps/tournament/live/event?eventId={}&division=All&view=Stats&round={}'.format(eventID, 1))
    rounds = stats_contents.find_all('div', class_="base-control-text")

    # Get and write the hole details
    for round_num in range(len(rounds)):
        # Create the 'round' object
        round = {'players': []}
        # Get the hole details for each round
        holes = get_hole_details(event_id, division, round_num + 1)
        round['holes'] = holes
        # Get the player objects -> returns a list of json objects for each player in the given division -> broken up into name, starting_score, final_score, round_score, rating?, hole_scores []
        players = get_player_details(event_id, division, round_num + 1)


        # Append everything to the overall object
        overall_object['round' + str(round_num + 1)] = round

    print(overall_object)
    pass

def davinci_json(leaderboard_object):
    # Take a scoreboard object and convert it to a JSON object for Davinci to use
    leaderboard_json = list()
    for i, row in leaderboard_object.iterrows():
        player_row =[str(row['Position']), row['Name'], row['Partial Score'] if row['Partial Score'] < 0 else 'E' if row['Partial Score'] == 0 else '+' + str(row['Partial Score']), row['Current Score'] if row['Current Score'] < 0 else 'E' if row['Current Score'] == 0 else '+' + str(row['Current Score']), row['Hole Scores']]
        leaderboard_json.append(player_row)
    return leaderboard_json


if __name__ == "__main__":
    eventID = sys.argv[1]
    division = sys.argv[2]
    round_num = sys.argv[3]
    hole = sys.argv[4]

    # json_generator(eventID, division)

    # c = PDGAScoreProcessor(eventID)
    # print(c.pages)

    # get_all_scoring_distributions(eventID)
    # round_stats, overall_stats = get_scoring_distribution(eventID, division, 2)
    # # print(round_stats)
    # # print("\n")
    # print(overall_stats)
    # difficulty = hole_difficulty_rankings(overall_stats[-1])
    # print(difficulty)
    scores = get_scoreboard(eventID, division, int(round_num))
    partial_scores = get_partial_scoreboard(scores, int(hole))
    print(davinci_json(partial_scores))
