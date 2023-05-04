# This script calculates the scoring distribution for each hole over the course of the tournament
# It takes event id and division as input
import re
import sys
import pandas as pd
from operator import add
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

score_indexing = {'Birdie+': 0, 'Birdie': 1, 'Par': 2, 'Bogey': 3, 'Bogey+': 4}

def get_div_text(lst, to=None):
    new_list = []
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
    # Set up the Chrome driver service
    chrome_service = Service('C:\\Users\\Kalyke\\Downloads\\chromedriver_win32 (1)\\chromedriver.exe')
    # Start the Chrome driver
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
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

def get_scoreboard(round):
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
    leaderboard['Total'] = leaderboard.sum(axis=1)
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
    for i in range(hole):
        # Get the par for the hole
        par = int(cols[4 + i])
        hole_scores = pd.DataFrame(full_round_scoreboard.iloc[:, 4 + i])
        scores_to_par = hole_scores - par
        starting_scores['Partial Score'] = starting_scores['Partial Score'] + scores_to_par.iloc[:,0]
    # Create a new column with the starting score and partial score
    starting_scores['Current Score'] = starting_scores['Starting Score'] + starting_scores['Partial Score']
    # Take the subset of the leaderboard that is relevant
    starting_scores = starting_scores[['Name', 'Current Score', 'Partial Score']]
    starting_scores['Position'] = starting_scores['Current Score'].rank(method='min').astype(int)
    starting_scores = starting_scores.sort_values(by=['Position'])
    return starting_scores


def get_scoring_distribution(eventID, division, rounds):
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


if __name__ == "__main__":
    eventID = sys.argv[1]
    division = sys.argv[2]
    round_num = sys.argv[3]
    # round_stats, overall_stats = get_scoring_distribution(eventID, division, 4)
    # print(round_stats)
    # print("\n")
    # print(overall_stats)
    # difficulty = hole_difficulty_rankings(overall_stats[-1])
    # print(difficulty)
    scores = get_scoreboard(int(round_num))
    partial_scores = get_partial_scoreboard(scores, 9)
    print(scores)
    print(partial_scores)
