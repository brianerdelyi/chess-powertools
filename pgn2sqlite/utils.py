
# Extracts all games from the pgn file
def extract_games_pgn(filename: str) -> list[dict]:
    if not filename.endswith('.pgn'):
        raise('Error: File extension must be PGN')

    games_data = [] # For holding RawPGN games data
    games = [] # For holding filtered games data

    with open(filename, 'r') as f:
        # Split the PGN data into individual games
        games_data = f.read().strip('\n').split("\n\n")
    
    # Iterate over each raw games data
    for i in range(len(games_data)):
        game_dict = {}

        # Each even-indexed item holds moves for the previous index game
        if i % 2 == 0:
            game_lines = games_data[i].split('\n')

            for line in game_lines:
                line = line.strip('[]')
                if len(line) == 0:
                    continue
                key, value = line.split(' ', maxsplit=1)
                game_dict[key] = value.strip('"')

            games.append(game_dict)
        else:
            # Appending the filtered moves
            games[-1] |= {'Moves': games_data[i].strip('\n ')}

            # Appending the RawPGN game data
            games[-1] |= {'RawPGN': games_data[i-1] + '\n\n' + games_data[i]}

    return games


# Extracts the columns from first game in the pgn file
def extract_headers_pgn(filename: str) -> list[str]:
    if not filename.endswith('.pgn'):
        raise('Error: File extension must be PGN')

    raw_headers = ""
    headers = []

    with open(filename, 'r') as f:
        # Extracting the headers
        raw_headers = f.read().strip('\n').split("\n\n", maxsplit=1)[0]
        
        if not raw_headers:
            return []

        raw_headers = raw_headers.strip(' \n').split('\n')

    # Filtering the headers and appending to the headers list
    for header in raw_headers:
        header = header.strip('[]')

        if len(header) == 0:
            continue

        header = header.split(' ', maxsplit=1)[0]
        headers.append(header)

    # Appending extra required headers
    headers.append('Moves')
    headers.append('RawPGN')

    return headers

