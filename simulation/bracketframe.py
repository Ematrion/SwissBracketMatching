import pandas as pd


def game_format(game):
    score1 = None
    score2 = None
    if game.player1() == game.winner():
        score1 = 'win'
        score2 = 'lose'
    elif game.player2() == game.winner():
        score1 = 'lose'
        score2 = 'win'
    else:
        msg = f"game (\'{game}\') as no winner"
        raise ValueError(msg)
    
    result1 = (game.player1().name(), f'{game.player2().name()} - {score1}')
    result2 = (game.player2().name(), f'{game.player1().name()} - {score2}')
    return result1, result2

def bracketFrame(stage):
    teams = stage.seeding
    data = pd.DataFrame(index=[team.name() for team in teams])
    data['Team'] = [team.name() for team in teams]
    data['Seed'] = [stage.seeding[team]+1 for team in teams]
    games = stage.games()
    rounds = [games[:8], games[8:16], games[16:24], games[24:30], games[30:]]
    
    data.astype(str)
    
    for i, round in enumerate(rounds):
        col = f'Round {i+1}'
        data[col] = ""
        
        for game in round:
            (team1, result1), (team2, result2) = game_format(game)
            data.at[team1, col] = result1
            data.at[team2, col] = result2

    return data