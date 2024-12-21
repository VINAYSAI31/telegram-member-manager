from flask import render_template, jsonify, session, redirect, url_for, request, send_file, abort
from app import app
from app.telegram_bot import run_bot, fetch_all_members
import asyncio
import os
from telethon.sync import TelegramClient  # Import TelegramClient


# Global variable for the new project location
PROJECT_DIR = "Your Project Directory"
api_id = 'YourAPI_ID'

api_hash = 'yourapi_hash'

bot_token = 'your bot token'

# Create a global event loop
loop = asyncio.get_event_loop()
print("Routes file loaded")


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        group_id = request.form['group_id']
        id_pattern = request.form['id_pattern']

        try:
            result = loop.run_until_complete(run_bot(group_id, id_pattern))

            session['result'] = result

            removed_users_csv = result.get('removed_users_csv')
            correct_usernames_csv = result.get('correct_usernames_csv')

            if removed_users_csv and os.path.exists(os.path.join(PROJECT_DIR, removed_users_csv)):
                print(f"Removed users CSV file created successfully: {removed_users_csv}")
            else:
                print("Error: Removed users CSV file not found.")

            if correct_usernames_csv and os.path.exists(os.path.join(PROJECT_DIR, correct_usernames_csv)):
                print(f"Correct usernames CSV file created successfully: {correct_usernames_csv}")
            else:
                print("Error: Correct usernames CSV file not found.")

            return redirect(url_for('results'))
        except Exception as e:
            print(f"Error running bot: {e}")
            return render_template('dashboard.html', error=str(e))

    return render_template('dashboard.html')


@app.route('/fetch_members', methods=['POST'])
def fetch_members():
    group_id = request.form.get('group_id')
    result = loop.run_until_complete(fetch_all_members(group_id))

    members = result.get('all_members', [])
    member_details = [
        {
            'first_name': member.get('first_name', 'Unknown'),
            'last_name': member.get('last_name', 'Unknown'),
            'username': member.get('username', 'Not provided')
        } for member in members
    ]

    session['fetch_members_result'] = {'all_members': member_details, 'all_members_csv': result.get('all_members_csv')}
    num_members = len(members)
    return render_template('fetch_members.html', members=member_details, group_id=group_id, num_members=num_members)


@app.route('/download_all_members')
def download_all_members():
    fetch_members_result = session.get('fetch_members_result')
    print(f"Fetch members result: {fetch_members_result}")

    if fetch_members_result and 'all_members_csv' in fetch_members_result:
        file_path = os.path.join(PROJECT_DIR, fetch_members_result['all_members_csv'])
        print(f"Attempting to send file from path: {file_path}")

        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            abort(404, description="File not found")
    else:
        abort(404, description="No file available for download")


@app.route('/results')
def results():
    result = session.get('result', None)
    if result is None:
        return redirect(url_for('dashboard'))
    return render_template('results.html', result=result)


@app.route('/download_removed_users')
def download_removed_users():
    result = session.get('result')
    if result and 'removed_users_csv' in result:
        file_path = os.path.join(PROJECT_DIR, result['removed_users_csv'])
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            abort(404, description="File not found")
    else:
        abort(404, description="No file available for download")


@app.route('/download_correct_usernames')
def download_correct_usernames():
    result = session.get('result')
    if result and 'correct_usernames_csv' in result:
        file_path = os.path.join(PROJECT_DIR, result['correct_usernames_csv'])
        print(f"Attempting to send file from path: {file_path}")
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            abort(404, description="File not found")
    else:
        abort(404, description="No file available for download")

@app.route('/get_groups', methods=['GET'])
async def get_groups():
    async with TelegramClient('my_session', api_id, api_hash) as client:
        # Fetch all group chats
        groups = await client.get_dialogs()
        group_ids = [{'id': dialog.id, 'title': dialog.name} for dialog in groups if dialog.is_group]

    return jsonify(group_ids)
