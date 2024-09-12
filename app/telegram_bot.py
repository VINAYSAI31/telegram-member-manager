import nest_asyncio
import asyncio
from telethon import TelegramClient
import pandas as pd
import re
from telethon.tl.types import User

# Apply the patch to allow nested event loops
nest_asyncio.apply()

# Hardcoded values for API credentials
api_id = #YOUR API ID

api_hash = #YOUR API hash

bot_token = #YOUR bot token
client = TelegramClient('#sessionname', api_id, api_hash)

async def fetch_all_members(group_id):
    # Ensure group_id is an integer
    try:
        group_id = int(group_id)
    except ValueError:
        raise ValueError(f"Invalid group ID format: {group_id}. It should be an integer.")
    
    try:
        await client.start()
        
        # Fetch the group entity
        group = await client.get_entity(group_id)
        print(f"Group fetched: {group}")
        
        # Fetch all participants
        members = []
        async for member in client.iter_participants(group):
            if isinstance(member, User):
                members.append({
                    'first_name': member.first_name,
                    'last_name': member.last_name,
                    'id': member.id,
                })
        
        # Convert to DataFrame
        df = pd.DataFrame(members)
        print(f"Total members fetched: {len(df)}")
        
        if df.empty:
            print("No members found.")
        
        # Save to CSV
        all_members_csv = 'all_members.csv'
        df.to_csv(all_members_csv, index=False)
        
        # Prepare the result to be returned
        result = {
            "total_users": len(df),
            "total_human_users": len(df),
            "all_members": df.astype(str).to_dict(orient='records'),
            "all_members_csv": all_members_csv
        }
        
        return result

    except Exception as e:
        print(f"Error fetching members: {e}")
        raise

    finally:
        await client.disconnect()


def contains_id(name, pattern):
    if name is None:
        return False
    match = re.search(pattern, name)
    return match is not None

# Define the list of titles to skip
skip_titles = ['HoD', 'Dean', 'Admin', 'DyHoD', 'Prof', 'VC']

def has_skip_title(name):
    if name is None:
        return False
    return any(title in name for title in skip_titles)

async def run_bot(group_id, id_pattern):
    try:
        group_id = int(group_id)
    except ValueError:
        print(f"Invalid group ID format: {group_id}")
        return {'error': 'Invalid group ID format'}

    # Define the custom pattern based on the provided ID pattern
    custom_pattern = rf'{id_pattern}\d{{5}}'

    # Create a Telegram client instance for the bot
    bot = TelegramClient('TempBotSession', api_id, api_hash)

    try:
        await bot.start(bot_token=bot_token)

        # Fetch members
        members = []
        async for member in bot.iter_participants(group_id):
            members.append({
                'first_name': member.first_name,
                'last_name': member.last_name,
                'id': member.id,
                'is_bot': member.bot
            })

        df = pd.DataFrame(members)

        # Check the total number of members fetched
        print(f"Total members fetched: {len(df)}")
        print(df.head())  # Print first few rows to inspect the data

        # Separate members with specific titles
        titled_members_df = df[df['first_name'].apply(has_skip_title) | df['last_name'].apply(has_skip_title)]

        # Remove titled members from the original DataFrame
        df = df[~df['id'].isin(titled_members_df['id'])]

        # Apply filtering based on ID pattern
        df['valid_first_name'] = df['first_name'].apply(lambda x: contains_id(x, custom_pattern))
        df['valid_last_name'] = df['last_name'].apply(lambda x: contains_id(x, custom_pattern))

        # Check filtered data
        filtered_df = df[df['valid_first_name'] | df['valid_last_name']]
        print(f"Filtered members: {len(filtered_df)}")
        print(filtered_df)

        removed_users = []

        for _, row in df.iterrows():
            user_id = row['id']
            first_name = row['first_name']
            last_name = row['last_name']
            full_name = f"{first_name} {last_name}".strip()

            if row['is_bot']:
                print(f"Skipping bot {full_name} (ID: {user_id}).")
                continue

            if user_id not in filtered_df['id'].values:
                try:
                    # await bot.send_message(user_id, 'Your name does not follow the correct format.')
                    print(f"Message sent to {full_name} (ID: {user_id}).")
                except Exception as msg_error:
                    print(f"Failed to send message to {full_name} (ID: {user_id}). Error: {msg_error}")

                try:
                    await bot.kick_participant(group_id, user_id)
                    removed_users.append({'first_name': first_name, 'last_name': last_name, 'id': user_id})
                    print(f"User {full_name} (ID: {user_id}) removed from group.")
                except Exception as kick_error:
                    print(f"Failed to remove user {full_name} (ID: {user_id}) from group. Error: {kick_error}")

                await asyncio.sleep(1)

        removed_users_df = pd.DataFrame(removed_users)
        correct_usernames_df = filtered_df

        # Save CSV files for removed users and correct usernames
        removed_users_csv = 'removed_users.csv'
        correct_usernames_csv = 'correct_usernames.csv'
        removed_users_df.to_csv(removed_users_csv, index=False)
        correct_usernames_df.to_csv(correct_usernames_csv, index=False)

        total_users = len(df)
        total_bots = df['is_bot'].sum()
        total_users_not_bots = total_users - total_bots
        correct_usernames = len(filtered_df)
        incorrect_usernames = total_users_not_bots - correct_usernames
        removed_count = len(removed_users_df)

        removed_users_list = removed_users_df.astype(str).to_dict(orient='records')

        result = {
            "total_users": int(total_users_not_bots),
            "total_bots": int(total_bots),
            "correct_usernames": int(correct_usernames),
            "incorrect_usernames": int(incorrect_usernames),
            "removed_users": removed_users_list,
            "titled_members": titled_members_df.astype(str).to_dict(orient='records'),
            "removed_users_csv": removed_users_csv,
            "correct_usernames_csv": correct_usernames_csv
        }

        print(f"Total Users (excluding bots): {total_users_not_bots}")
        print(f"Total Bots: {total_bots}")
        print(f"Correct Usernames: {correct_usernames}")
        print(f"Incorrect Usernames: {incorrect_usernames}")
        print(f"Removed Users: {removed_users_list}")

        print("Members with special titles (HoD, Dean, Admin, DyHoD, Prof, VC):")
        print(titled_members_df)

        return result

    except Exception as e:
        print(f"Error running bot: {e}")
        return {'error': str(e)}
    finally:
        await bot.disconnect()
