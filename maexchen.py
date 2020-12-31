import discord
import random
from random import shuffle
import os
from time import sleep
## import PyNaCl

info = "The Discord Bot Maexchen is offering commands to roll dices for the known game (Mia in English).\n"
info += "Type 'r' for rolling the dices. Result is just shown to user who entered the command.\n"
info += "Anyone can enter 's' for showing the last result for all in the channel.\n"
info += "'h' will show this info message in the channel.\n"


def represents_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


class Dices:
    value = "no dices rolled yet"  # values of the last roll

    def __init__(self):
        random.seed(a=None)
        print("Dices: Random generator seeded with system time.")

    def roll(self):
        self.value = random.choice([":one:", ":two:", ":three:", ":four:", ":five:", ":six:"])
        self.value += " "
        self.value += random.choice([":one:", ":two:", ":three:", ":four:", ":five:", ":six:"])
        return self.value


class Sounds:
    names = ""  # names of sounds (just filenames)
    files = []  # full file names of sounds for playing in subdir sounds

    def __init__(self):
        c_path = os.path.join(os.getcwd(), "sounds")
        for i, f in enumerate(os.listdir(c_path)):
            self.files.append(os.path.join(c_path, f))
            self.names += "p{} : {}\n".format(i, f[:f.find('.')])
            print("Assigned sound files:\n{}".format(self.names))
        if self.names == "":
            self.names = "no sounds defined"


class WhoAmI:
    filename = "known_persons.txt"
    status_file = "known_persons_status.txt"  # here are values stored in case re-start is required
    # remove this file if you want to start from scratch
    unassigned_known_persons = []
    user_assignments = dict()

    def __init__(self):
        self.unassigned_known_persons = open(self.filename).read().splitlines()
        print("Read following known persons: {}".format(self.unassigned_known_persons))
        if os.path.isfile(self.status_file):
            with open(self.status_file) as f:
                for line in f:
                    role, user = line.split('+')
                    self.user_assignments[user.strip()] = role.strip()
                    self.unassigned_known_persons.remove(role.strip())
                    print("{} assigned to: {}".format(role, user))

    def who_is(self, message):
        if not message.guild:
            return "You need to ask 'whois x' in a text-channel and not e.g. via direct message.", ""
        whois_message = message.content.split()
        if len(whois_message) != 2:
            return "You need to give one name after whois like 'whois max' or 'whois max#1234'", ""
        print("Checking now whois {} for guild: {}".format(whois_message[1], message.guild))
        member_name = message.guild.get_member_named(whois_message[1])
        if message.author == member_name:
            return "", "Sorry, you need to ask others to find out who you are :face_with_raised_eyebrow:"
        if not member_name:
            return "User name '{}' not found!".format(whois_message[1]), ""
        if str(member_name) in self.user_assignments:
            return "{} knows now the role of {}  :smiley:".format(message.author,
                                                                  whois_message[1]), "{} is acting as {}".format(
                whois_message[1], self.user_assignments[str(member_name)])
        if not len(self.unassigned_known_persons):
            return "Sorry, {} is playing no role (all roles are assigned)".format(whois_message[1]), ""
        new_role = random.choice(self.unassigned_known_persons)
        self.user_assignments[str(member_name)] = new_role
        self.unassigned_known_persons.remove(new_role)
        with open(self.status_file, 'a') as f:
            f.write("{} + {}\n".format(new_role, member_name))
        return "{} knows now the role of {}  :smiley:".format(message.author,
                                                              whois_message[1]), "{} is acting as {}".format(
            whois_message[1], self.user_assignments[str(member_name)])


class Quiz:
    filename = "questions.txt"
    status_file = "questions_status.txt"  # here are values stored in case re-start is required
    questions = []
    answers = []
    correct_answer_ids = []
    user_current_question = dict()
    user_current_points = dict()

    def __init__(self):
        q_and_a = open(self.filename).read().splitlines()
        print("Read following questions and answers: {}".format(q_and_a))
        for line in q_and_a:
            line = line.split('+')
            self.questions.append(line[0])  # the question is the first string between '+' in the line
            self.answers.append(line[1:])
            correct_answer = line[1]  # the first answer = second string in the list is the correct one
            shuffle(self.answers[-1])
            self.correct_answer_ids.append(self.answers[-1].index(correct_answer)+1)  # start possible answers at 1
        print(self.questions)
        print(self.answers)
        print(self.correct_answer_ids)
        if os.path.isfile(self.status_file):
            with open(self.status_file) as f:
                for line in f:
                    user, cquest, cpoints = line.split('+')
                    self.user_current_question[user.strip()] = int(cquest.strip())
                    self.user_current_points[user.strip()] = int(cpoints.strip())
        print("Users are at questions: {}".format(self.user_current_question))
        print("Users have points: {}" .format(self.user_current_points))

    def get_question(self, message):
        if str(message.author) not in self.user_current_question:
            self.user_current_question[str(message.author)] = 0
            self.user_current_points[str(message.author)] = 0
        if self.user_current_question[str(message.author)] < 0:  # negative position indicates that current question was not yet read
            self.user_current_question[str(message.author)] *= -1
        if self.user_current_question[str(message.author)] >= len(self.questions):
            return "Du hast das Quiz schon durchgespielt. Aktuell gibt es keine weiteren Fragen."
        cq = self.user_current_question[str(message.author)]
        quest = self.questions[cq] + '\n'
        for a in range(len(self.answers[cq])):
            quest += "{}: {}\n".format(a + 1, self.answers[cq][a])  # show 1 as first possible answer
        return quest

    def give_answer(self, message):
        if str(message.author) not in self.user_current_question:
            return "Soll {} eine Antwort fürs Quizz sein? Dann musst Du Dir aber erst mal mit 'q' die Frage durchlesen.".format(message.content)
        if self.user_current_question[str(message.author)] < 0:
            return "Du musst Dir doch mit 'q' erst mal die neue Frage durchlesen, bevor Du antwortest."
        if self.user_current_question[str(message.author)] >= len(self.questions):
            return "Du hast das Quiz schon durchgespielt. Aktuell gibt es keine weiteren Fragen."
        # Okay, now we can log and evaluate the answer
        if int(message.content) == self.correct_answer_ids[self.user_current_question[str(message.author)]]:
            self.user_current_question[str(message.author)] = -self.user_current_question[str(message.author)] - 1
            self.user_current_points[str(message.author)] += 1
            with open(self.status_file, 'a') as f:
                f.write("{} + {} + {}\n".format(message.author, self.user_current_question[str(message.author)],
                                                self.user_current_points[str(message.author)]))
            return "Super. Stimmt genau."
        else:
            self.user_current_question[str(message.author)] = -self.user_current_question[str(message.author)] - 1
            with open(self.status_file, 'a') as f:
                f.write("{} + {} + {}\n".format(message.author, self.user_current_question[str(message.author)],
                                                self.user_current_points[str(message.author)]))
            return "Leider falsch...."

    def show_points(self, message):
        point_list = ""
        for user in self.user_current_points:
            point_list += "{} has {} points".format(user, self.user_current_points[user])
        return point_list



print("Starting bot...")

TOKEN = open("token.txt", "r").readline()

intents = discord.Intents.all()
client = discord.Client(intents=intents)
dices = Dices()
whoami = WhoAmI()
quiz = Quiz()
sounds = Sounds()
vc = None  # voice client of bot when connected to voice channel


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    print(client.guilds)
    print(client.users)
    for c in client.get_all_channels():
        print(c.name)
    for m in client.get_all_members():
        print(m.name, m.status)


@client.event
async def on_message(message):
    global vc
    print("Received message: {} from user: {}".format(message.content, message.author))
    if message.author == client.user:
        return

    if message.content == "h":
        await message.channel.send(info)

    if message.content == 'r':
        await message.author.send(dices.roll())

    if message.content == 's':
        await message.channel.send(dices.value)

    if message.content == 'q':
        if not str(message.channel).startswith("Direct Message"):
            await message.channel.send("Um mit mir das Quiz zu spielen kommunziere bitte direkt mit mir.\nKlicke dazu links oben auf 'Maexchen'")
        await message.author.send(quiz.get_question(message))

    if str(message.channel) == "Direct Message with {}".format(message.author) and represents_int(message.content):
        await message.author.send(quiz.give_answer(message))

    if message.content == 'qp':
        await message.channel.send(quiz.show_points(message))

    if message.content.startswith('whois'):
        print("Guild: {}".format(message.guild))
        response_channel, response_dm = whoami.who_is(message)
        if response_dm:
            await message.author.send(response_dm)
        if response_channel:
            await message.channel.send(response_channel)

    if message.content == 'pl':
        await message.channel.send(sounds.names)
    if message.content[0] == 'p' and represents_int(message.content[1:]):
        sound_number = int(message.content[1:])
        # Gets voice channel of message author
        author_voice = message.author.voice
        print("user has voice: {}".format(author_voice))
        if author_voice is not None:
            voice_channel = author_voice.channel
            if not vc or client.user not in voice_channel.members:
                if vc:
                    await vc.disconnect()
                print("Bot is connecting to voice channel: {}".format(voice_channel))
                vc = await voice_channel.connect()
            vc.play(discord.FFmpegPCMAudio(executable="D:/Programme/ffmpeg/bin/ffmpeg.exe", source=sounds.files[sound_number]))
            # Sleep while audio is playing.
            #while vc.is_playing():
            #    sleep(.1)
            #await vc.disconnect()
        else:
            await message.channel.send("You need to join an audio channel first ...")



print("Bot is ready!")
client.run(TOKEN)
