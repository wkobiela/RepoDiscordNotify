# !/usr/bin/python
import os
import time
import sys
import getopt
import re
import requests
from datetime import datetime

counter = 0  # Counter if you want to run script with finite number of loops. Leave it 0!
latest_commit_hash = ""

def get_files():
    if os.path.isfile('discord.sh'):
        print("File 'discord.sh' already exists. Proceeding...")
    else:
        filename = "discord.sh"
        url = 'https://raw.githubusercontent.com/ChaoticWeg/discord.sh/master/discord.sh'
        f = requests.get(url)
        open(filename, 'wb').write(f.content)
        os.popen('chmod +x discord.sh').read()
        print("File 'discord.sh' downloaded. Proceeding...")
    return


def clone(repo, branch, dir_name):
    if os.path.isdir('../' + dir_name):
        actual_branch = os.popen('cd ../' + dir_name + '; git branch').read()[2:]
        filtered_branch = os.linesep.join([s for s in actual_branch.splitlines() if s])

        if filtered_branch == branch:
            print("Repository already cloned with selected branch.")
        else:
            print("Repository cloned, but with wrong branch. Removing old, cloning proper one.")
            os.popen('cd ../; rm -rf ' + dir_name + '; git clone \
                     --single-branch --branch ' + branch + " " + repo).read()
    else:
        os.popen('cd ../; git clone --single-branch --branch ' + branch + ' ' + repo).read()

    # take second latest commit and create commit.txt file. Just to make sure, that script would catch next
    # newer commit and send message using Discord bot
    global latest_commit_hash
    latest_commit_hash = os.popen('cd ../' + dir_name + '; git log -1 --skip 1 --pretty=format:%H').read()
    print(f'Latest commit hash: {latest_commit_hash}')
    # file = open("commit.txt", "w")
    # file.write(latest_commit_to_file)
    # file.close()
    return


def pull(dir_name):
    os.popen('cd ../' + dir_name + '; git pull').read()
    return


def job(dir_name):
    file = open("commit.txt", "r+")
    previous_checked1 = file.read()
    previous_checked = os.linesep.join([s for s in previous_checked1.splitlines() if s])

    # time.sleep(1)
    count = 0

    while True:
        output = os.popen('cd ../' + dir_name + '; git log -1 --skip ' + str(count) + ' --pretty=format:%s').read()
        commit_hash = os.popen('cd ../' + dir_name + '; git log -1 --skip ' + str(count) + ' --pretty=format:%H').read()
        commit_link = f"{repo[:-4]}/commit/"
        sleep_time = 10  # Sleep timer in seconds. Change to customize repo refresh rate

        if previous_checked == output:
            print(f"No new updates. Sleeping for {sleep_time}s now.")
            latest_commit = os.popen('cd ../' + dir_name + '; git log -1 --pretty=format:%s').read()
            file.seek(0)
            file.truncate()
            file.write(latest_commit)
            file.close()
            print("-----------------------------------------------")
            time.sleep(sleep_time)  # Set sleep time after no new commits found to ?seconds
            break

        else:
            print("New commit! -> " + output)
            # EXAMPLE DISCORD BOT MESSAGE
            # command = f'./discord.sh \
            #             --username "NotificationBot" \
            #             --avatar "https://i.imgur.com/12jyR5Q.png" \
            #             --text "Hello, world!"'
            # DOCKERFILES DISCORD BOT MESSAGE
            command = f'./discord.sh \
                        --username "OpenVisualCloud" \
                        --avatar "https://avatars3.githubusercontent.com/u/46843401?s=90&v=4" \
                        --text "🐳 NEW COMMIT: **{output}** \\n path: <{commit_link}{commit_hash}>"'

            os.popen(command)
            count = count + 1  # to move to next new commit
            # time.sleep(1)
            print("-----------------------------------------------")


def usage():
    print("====================================== DISPLAYING HELP ======================================")
    print("python3 notify.py --repo <link_to_repository> --branch <branch_to_be_observed>")
    print("--repo: Link to cloned repo, with .git at the end.")
    print("--branch: Branch name, that will be cloned. Default is master.")
    print("In code: setup sleep timer and Discord Bot message.")
    print("e.g. of usage:")
    print("python3 notify.py --repo https://github.com/OpenVisualCloud/Dockerfiles.git --branch v21.3")
    print("=============================================================================================")
    sys.exit()


def getarguments(argv):
    global opts
    repo = None
    branch = "master" # Default master, if not given otherwise
    short_opts = 'hr:b:'
    long_opts = ["help", "repo=", "branch="]
    try:
        opts, _ = getopt.getopt(argv, short_opts, long_opts)
        if not opts:
            print("Error: No options supplied")
            usage()
    except getopt.GetoptError:
        print(f"Error in options or options not specified.\n")
        usage()

    for opt, arg in opts:
        if opt in ("-r", "--repo"):
            repo = arg
            if re.match(r"^(([A-Za-z0-9]+@|http(|s)\:\/\/)|(http(|s)\:\/\/[A-Za-z0-9]+@))([A-Za-z0-9.]+(:\d+)?)(?::|\/)([\d\/\w.-]+?)(\.git){1}$", repo):
                print("Valid git repository url. Proceeding...")
            else:
                print("Invalid git repository url.\n")
                usage()
        elif opt in ("-b", "--branch"):
            branch = arg
            print("Chosen branch: " + branch)
        elif opt in ("-h", "--help"):
            usage()
        else:
            print(f"Unsupported option {opt}")
            usage()
    return repo, branch


if __name__ == '__main__':
    loop_time = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    # sys.stdout = open('log.txt', 'a+')  # Comment this, to enable live logging in terminal
    repo, branch = getarguments(sys.argv[1:])
    print("Program started: " + loop_time)
    dir_name = re.search(r"(([^/]+).{4})$", repo).group(2)
    get_files()
    clone(repo, branch, dir_name)
    # while True:  # Or while counter < given_number, to get finite number of loops
    #     pull(dir_name)
    #     job(dir_name)
      # counter += 1

    print("Program exited.")

    # sys.stdout.close()  # Comment this, to enable live logging in terminal
    # exit()  # Uncomment, if using finite number of loops
