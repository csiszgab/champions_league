import json
import pymysql
import os

# Database connection parameters (replace with your actual values)
host = os.environ['RDS_HOST']
user = os.environ['RDS_USER']
password = os.environ['RDS_PASSWORD']
database = os.environ['RDS_DB']

def lambda_handler(event, context):
    # Get query parameters (round and match number)
    round_number = int(event['queryStringParameters']['round'])
    match_number = int(event['queryStringParameters']['matchNumber'])

    # Connect to the RDS MySQL database
    connection = pymysql.connect(host=host, user=user, password=password, database=database)
    
    try:
        with connection.cursor() as cursor:
            # Query to get teams for the selected match
            match_query = f"""
                SELECT team_1, team_2 FROM edw_sport.sport_cl_matches 
                WHERE round_number = {round_number} AND match_number = {match_number};
            """
            cursor.execute(match_query)
            match_data = cursor.fetchone()

            if match_data:
                team1 = match_data[0]
                team2 = match_data[1]

                # Query to get team statistics for both teams
                team_stats_query = f"""
                    SELECT * FROM edw_sport.sport_cl_teams WHERE team_name IN ('{team1}', '{team2}');
                """
                cursor.execute(team_stats_query)
                team_stats = cursor.fetchall()

                team1_stats = {}
                team2_stats = {}

                for row in team_stats:
                    team_name = row[0]
                    stats = {
                        'Team Value': row[3],
                        'Trainer': row[4],
                        'Trainer Since': row[5],
                        'Most Valuable Player': row[6],
                        'Value': row[7],
                        'Best Purchase': row[8],
                        'Best Purchase Value': row[9],
                        'Tactic': row[10],
                    }
                    if team_name == team1:
                        team1_stats = stats
                    else:
                        team2_stats = stats

                # Fetch round matches
                round_matches_query = f"""
                    SELECT match_number, team_1, team_2, result FROM edw_sport.sport_cl_matches 
                    WHERE round_number = {round_number};
                """
                cursor.execute(round_matches_query)
                round_matches = cursor.fetchall()

                # Prepare data for frontend
                response_data = {
                    'team1Name': team1,
                    'team2Name': team2,
                    'team1Stats': team1_stats,
                    'team2Stats': team2_stats,
                    'roundMatches': [{'match_number': match[0], 'team_1': match[1], 'team_2': match[2], 'result': match[3]} for match in round_matches]
                }

                return {
                    'statusCode': 200,
                    'body': json.dumps(response_data)
                }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': str(e)})
        }
    finally:
        connection.close()
