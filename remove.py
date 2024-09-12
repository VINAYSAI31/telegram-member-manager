import os

def clean_up_sessions():
    session_files = ['UniqueBotSession.session', 'UniqueTempBotSession.session']
    for file in session_files:
        if os.path.exists(file):
            os.remove(file)
