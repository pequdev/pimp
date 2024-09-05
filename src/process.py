
import pandas as pd

async def process_results(dataframe):
    for index, row in dataframe.iterrows():
        name = row['Name']
        location = row['Location']
        query = f"{name} {location}"
        
        # Wyszukaj profile społecznościowe
        social_links = await search_google(query, verbose=True)

        # Zaktualizuj odpowiednie kolumny w DataFrame
        dataframe.at[index, 'Instagram'] = social_links['instagram']
        dataframe.at[index, 'TikTok'] = social_links['tiktok']
        dataframe.at[index, 'Facebook'] = social_links['facebook']
        dataframe.at[index, 'YouTube'] = social_links['youtube']
        dataframe.at[index, 'TripAdvisor'] = social_links['tripadvisor']
        dataframe.at[index, 'TheFork'] = social_links['thefork']

    # Zapisz zaktualizowane dane do pliku CSV
    dataframe.to_csv('output.csv', index=False)
