import os
import subprocess
from pathlib import Path
from datetime import datetime
import requests

global server_dir

# MODIFY SERVER LOCATION HERE:
SERVER_LOCATION ="C:/Users/Mate/Documents/Minecraft_Server/kucko_minecraft"


def check_server_location():

    global server_dir
    server_dir = Path(SERVER_LOCATION)

    if not server_dir.exists():
        print(f"Error: Server directory {server_dir} does not exist.")
        return False

    server_jar = server_dir / "server.jar"
    if not server_jar.exists():
        print(f"Error: server.jar file not found in {server_dir}.")
        return False

    print("\nServer directory and server.jar file found!")
    return True


def start_server():
    success = check_server_location()
    if success:
        print(f"\nStarting server at {server_dir}")
        os.chdir(server_dir)
        command = ["java", "-jar", "server.jar"]
        send_dc_message(1)
        subprocess.run(command)
        send_dc_message(0)
        suc = commit_and_push_changes()
        if not suc:
            return -1
    else:
        return -1


def get_public_ipv6():
    try:
        # ipify API for IPv6
        response = requests.get('https://api64.ipify.org', params={'format': 'json'})
        data = response.json()
        return data['ip']
    except requests.RequestException as e:
        raise f"An error occurred: {e}"


def send_dc_message(state, message_title="", message_content=""):
    url = "https://discord.com/api/webhooks/1288792241925525525/DfB2tCK6mX1oRRkKDgjZnbRBV0sF84gYkkdCFO24hievGQhcMA2m6gbe_rls-Y2F0l3K"
    ipv6 = get_public_ipv6()

    if state == 1:
        content = "Server is up and running"
        embeds = [{"title": f"[{ipv6}]:25565"}]
    elif state == 0:
        content = "Server is shut down"
        embeds = [{"title": "Thank you for playing, Gamers :heart:"}]
    elif state == 2:
        content = message_title
        embeds = [{"title": f"{message_content}"}]
    else:
        raise ValueError("Invalid state")

    data = {
        "avatar_url": "https://crafty.gg/bot/bot.png",
        "username": "Minecraft Server Bot",
        "content": content,
        "embeds": embeds
    }

    x = requests.post(url, json=data)
    # print(x)

def commit_and_push_changes():
    try:
        os.chdir(SERVER_LOCATION)

        subprocess.run(['git', 'add', '--all'], check=True)
        print("\n\ngit add success\n\n")

        commit_message = datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '_server_save'
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        print("\n\ngit commit success\n\n")

        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        print("\n\ngit push success\n\n")
        print(f"Changes committed and pushed with message: {commit_message}")
        send_dc_message(2, message_title="Server Backed Up Successfully.",
                        message_content=f":confetti_ball: :confetti_ball: :confetti_ball:\n\n"
                                        f"changes commited under commit {commit_message}")

    except subprocess.CalledProcessError as e:
        print(f"Error occurred during Git operation: {e}")
        send_dc_message(2, message_title="Server Backup to GitHub failed.",
                        message_content=f"Error: {e}")
        return False

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        send_dc_message(2, message_title="Server Backup to GitHub failed.",
                        message_content=f"Error: {e}")
        return False

    return True

s = start_server()
if s == -1:
    print("\nSomething went wrong. Check server location.")
