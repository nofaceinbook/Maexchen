import discord
import random
from random import shuffle

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


class WhoAmI:
    filename = "known_persons.txt"
    unassigned_known_persons = []
    user_assignments = dict()

    def __init__(self):
        self.unassigned_known_persons = open(self.filename).read().splitlines()
        print("Read following known persons: {}".format(self.unassigned_known_persons))

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
        if member_name in self.user_assignments:
            return "{} knows now the role of {}  :smiley:".format(message.author,
                                                                  whois_message[1]), "{} is acting as {}".format(
                whois_message[1], self.user_assignments[member_name])
        if not len(self.unassigned_known_persons):
            return "Sorry, {} is playing no role (all roles are assigned)".format(whois_message[1]), ""
        new_role = random.choice(self.unassigned_known_persons)
        self.user_assignments[member_name] = new_role
        self.unassigned_known_persons.remove(new_role)
        return "{} knows now the role of {}  :smiley:".format(message.author,
                                                              whois_message[1]), "{} is acting as {}".format(
            whois_message[1], self.user_assignments[member_name])


class Quiz:
    filename = "questions.txt"
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

    def get_question(self, message):
        if message.author not in self.user_current_question:
            self.user_current_question[message.author] = 0
            self.user_current_points[message.author] = 0
        if self.user_current_question[message.author] < 0:  # negative position indicates that current question was not yet read
            self.user_current_question[message.author] *= -1
        if self.user_current_question[message.author] >= len(self.questions):
            return "Du hast das Quiz schon durchgespielt. Aktuell gibt es keine weiteren Fragen."
        cq = self.user_current_question[message.author]
        quest = self.questions[cq] + '\n'
        for a in range(len(self.answers[cq])):
            quest += "{}: {}\n".format(a + 1, self.answers[cq][a])  # show 1 as first possible answer
        return quest

    def give_answer(self, message):
        if message.author not in self.user_current_question:
            return "Soll {} eine Antwort fürs Quizz sein? Dann musst Du Dir aber erst mal mit 'q' die Frage durchlesen.".format(message.content)
        if self.user_current_question[message.author] < 0:
            return "Du musst Dir doch mit 'q' erst mal die neue Frage durchlesen, bevor Du antwortest."
        if self.user_current_question[message.author] >= len(self.questions):
            return "Du hast das Quiz schon durchgespielt. Aktuell gibt es keine weiteren Fragen."
        if int(message.content) == self.correct_answer_ids[self.user_current_question[message.author]]:
            self.user_current_points[message.author] += 1
            self.user_current_question[message.author] = -self.user_current_question[message.author] - 1
            return "Super. Stimmt genau."
        else:
            self.user_current_question[message.author] = -self.user_current_question[message.author] - 1
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


print("Bot is ready!")
client.run(TOKEN)
