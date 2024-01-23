#!/usr/bin/python3

import datetime 

import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound



class Heure:
    def __init__(self, titre, matiere, prof, salle, date, debut, fin):
        self.titre = titre
        self.matiere = matiere
        self.prof = prof
        self.salle = salle
        self.date = date
        self.debut = debut
        self.fin = fin

    def __str__(self):
        return f"{self.debut} - {self.fin} : [{self.matiere}]\n{self.salle} - {self.prof}"

def affichage(liste):
    for i in range (len(liste)):
        print(liste[i])

def convert_heure(plage):
    tmp = []
    test = plage.split("\\n")
    for i in range (len(test)):
        if test[i] != '':
            tmp.append(test[i])
    title = ""
    matiere = ""
    prof = tmp[2]
    classes = tmp[3]
    salle = ""
    date = ""
    debut = ""
    fin = ""

    for i in range(len(tmp)):
        for j in range(len(tmp[i])):
            if tmp[i][j:j+8] == 'title: "':
                titre = tmp[i][j+8:]
            elif tmp[i][j:j+10] == 'Matière : ':
                matiere = tmp[i][j+10:]
            elif tmp[i][j:j+8] == 'Salle : ':
                salle = tmp[i][j+8:]
            elif tmp[i][j:j+8] == 'start: "':
                date = tmp[i][j+8:j+18]
                debut = tmp[i][j+19:j+27]
                fin = tmp[i][j+47:j+55]

    return Heure(titre, matiere, prof, salle, date, debut, fin)

def get_debut(heure : Heure):
    time = heure.debut
    h = int(time[:2])
    m = int(time[3:5])
    s = int(time[6:])
    return h, m, s

def sort_day(plan):
    for day in list(plan.keys()):
        heures = plan[day]
        res = []
        # tri de heures dans l'ordre croissant selon l'heure de début
        # on utilise l'algorithme du tri par sélection
        while len(heures) > 0:
            # recherche d'un minimum
            mini = heures[0]
            index = 0
            if len(heures) > 1:
                for i in range(1, len(heures)):
                    # test des heures
                    if get_debut(heures[i])[0] < get_debut(mini)[0]:
                        mini = heures[i]
                        index = i
                    elif get_debut(heures[i])[0] == get_debut(mini)[0]:
                        # test des minutes
                        if get_debut(heures[i])[1] < get_debut(mini)[1]:
                            mini = heures[i]
                            index = i
                        elif get_debut(heures[i])[2] == get_debut(mini)[2]:
                            # test des secondes
                            if get_debut(heures[i])[2] < get_debut(mini)[2]:
                                mini = heures[i]
                                index = i
            # placer le minimum au début
            tmp = heures.pop(index)
            res.append(tmp)
        plan[day] = res

def get_week(day : str):
    date_obj = datetime.datetime.strptime(day, '%Y-%m-%d')

    monday = (date_obj - datetime.timedelta(days=date_obj.weekday()))  # Monday
    tuesday = (monday + datetime.timedelta(days=1))  # Sunday
    wednesday = (monday + datetime.timedelta(days=2))
    thursday = (monday + datetime.timedelta(days=3))
    friday = (monday + datetime.timedelta(days=4))
    return [str(monday.date()), str(tuesday.date()), str(wednesday.date()), str(thursday.date()), str(friday.date())]



class TimeTable(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=["!"], help_command=None, case_insensitive=True, intents=discord.Intents.all())
        self.news = self.getnews()

    async def on_ready(self):
        global dico
        # lire la page
        path = open("./internet.html")
        file = path.readlines()
        path.close
        # récupérer les plages horaires
        table = []
        i = 0
        while i < len(file):
            if 'title: ' in file[i]:
                table.append(file[i])
            i+=1
        # transformer les plages horaires en heure
        liste_heures = []
        for i in range(len(table)):
            liste_heures.append(convert_heure(table[i]))

        dico = {}

        for i in range(len(liste_heures)):
            dico[liste_heures[i].date]=[]
        for i in range(len(liste_heures)):
            dico[liste_heures[i].date].append(liste_heures[i])
        sort_day(dico)

        print('TimeTable has loaded and connected successfully to Discord!')

    def getnews(self):
        res = []
        file = open("./news").readlines()
        for line in file:
            line = line.split("~|~")
            res.append(line)
        return res


bot = TimeTable()


@bot.command(name="edt")
async def edt(ctx, date=(str(datetime.datetime.now()).split(" ")[0])):
    if not date in list(dico.keys()):
        await ctx.send(f"Aucun cours pour le {date} à ma connaissance.")
        return
    if len(dico[date]) <= 2:
        color=0x41EE9E
    elif len(dico[date]) <= 3:
        color=0xFFC043
    else:
        color=0xFF4343
    embed=discord.Embed(title=f"Emploi du temps du {date}", color=color)
    for heure in (dico[date]):
        embed.add_field(name=f"{heure.debut[:-3]} - {heure.fin[:-3]} - [{heure.matiere}]", value=f"{heure.salle} - {heure.prof}", inline=False)
    embed.set_footer(text="Les informations viennent de l'ENT de l'USPN. C'est l'emploi du temps de VIENNE Mathys (@vienne_mathys), L1 Math./Info. Gr. A\nJe décline toute responsabilité en cas d'incident. Privilégiez les canaux officiels.\nDernière mise à jour des données : 18 janv. 2023.")
    await ctx.channel.send(embed=embed)

@bot.command(name="update_database")
async def upd(ctx):
    path = open("./internet.html")
    file = path.readlines()
    path.close
    # récupérer les plages horaires
    table = []
    i = 0
    while i < len(file):
        if 'title: ' in file[i]:
            table.append(file[i])
        i+=1
    # transformer les plages horaires en heure
    liste_heures = []
    for i in range(len(table)):
        liste_heures.append(convert_heure(table[i]))

    dico = {}

    for i in range(len(liste_heures)):
        dico[liste_heures[i].date]=[]
    for i in range(len(liste_heures)):
        dico[liste_heures[i].date].append(liste_heures[i])
    sort_day(dico)
    await ctx.send("Done.")

@bot.command(name='help')
async def aide(ctx, command=None):
    if command == None:
        embed = discord.Embed(title="Comment utiliser TimeTable ?")
        embed.add_field(name="PRÉFIXE", value="Mon préfixe est `!`. Ne l'oubliez pas avant chaque commande !!!", inline=False)
        embed.add_field(name="EMPLOI DU TEMPS", value="`!edt [DATE]` : donne l'emploi du temps pour cette DATE.\n`!week [DATE]` : donne l'emploi du temps pour la semaine de cette DATE.", inline=False)
        embed.add_field(name="OBTENIR DE L'AIDE", value="`!help [COMMANDE]` : affiche une aide pour la COMMANDE.", inline=False)
        embed.set_footer(text="Ce bot est développé par VIENNE Mathys. (@vienne_mathys sur Discord). Version 1.0")
        await ctx.send(embed=embed)
    elif command == "edt":
        await ctx.send("`!edt [DATE]` : donne l'emploi du temps pour cette DATE.\nAttention au format de DATE : `YYYY-MM-JJ`")

    elif command == "week":
        await ctx.send("`!week [DATE]` : donne l'emploi du temps pour la semaine de cette DATE.\nSi aucune DATE donnée, prend la date du jour.\nAttention au format de DATE : YYYY-MM-JJ")

    elif command == "news":
        await ctx.send("`!news` : affiche le tableau d'affichage de TimeTable. Il contient des compléments d'information sur l'emploi du temps.")

@bot.command(name='week')
async def week(ctx, date=None):
    if date==None:
        # Renvoie une liste contenant tous les jours de la semaine en str
        week = (get_week(str(datetime.datetime.now().date())))
    else:
        week = (get_week(date)) 
    for day in week:
        if not day in list(dico.keys()):
            await ctx.send(f"Aucun cours pour le {day} à ma connaissance.")
            continue

        if len(dico[day]) <= 2:
            color=0x41EE9E
        elif len(dico[day]) <= 3:
            color=0xFFC043
        else:
            color=0xFF4343
        embed=discord.Embed(title=f"Emploi du temps du {day}", color=color)
        for heure in (dico[day]):
            embed.add_field(name=f"{heure.debut[:-3]} - {heure.fin[:-3]} - [{heure.matiere}]", value=f"{heure.salle} - {heure.prof}", inline=False)
        embed.set_footer(text="Les informations viennent de l'ENT de l'USPN. C'est l'emploi du temps de VIENNE Mathys (@vienne_mathys), L1 Math./Info. Gr. A\nJe décline toute responsabilité en cas d'incident. Privilégiez les canaux officiels.\nDernière mise à jour des données : 18 janv. 2023.")
        await ctx.channel.send(embed=embed)
        

@bot.command(name="news")
async def news(ctx):
    embed=discord.Embed(title="Les informations emploi du temps", description="Retrouvez ici les informations liées à l'emploi du temps, des erreurs en tout genre liées à la base de données et autres joyeusetés.")
    print(bot.news)
    for new in bot.news:
        embed.add_field(name=new[0], value=new[1], inline=False)
    await ctx.send(embed=embed)


@bot.command(name="add_new")
async def add_new(ctx):
    if not ctx.message.author.id == 1170981304637063225:
        await ctx.send("Accès refusé.")
        return

    def check(message: discord.Message):
        return message.channel == ctx.channel and message.author != ctx.me

    await ctx.send('Entrez le nom de la nouvelle')
    nom = await bot.wait_for('message', check=check)

    if nom.content == "cancel":
        await ctx.send("Opération annulée")
        return

    await ctx.send('Entrez le contenu de la nouvelle')
    contenu = await bot.wait_for('message', check=check)

    if contenu.content == "cancel":
        await ctx.send("Opération annulée")
        return

    # Ajout à la base de données
    with open('news', 'a') as file:
        file.write(f"{nom.content}~|~{contenu.content}\n")
    bot.news = bot.getnews()
    await ctx.send(f"{nom.content} ajouté.")

@bot.command(name="rm_new")
async def rm_new(ctx):
    if not ctx.message.author.id == 1170981304637063225:
        await ctx.send("Accès refusé.")
        return

    def check(message: discord.Message):
        return message.channel == ctx.channel and message.author != ctx.me

    await ctx.send('Entrez le nom de la nouvelle')
    nom = await bot.wait_for('message', check=check)
    nom_new = nom.content
    if nom_new == "cancel":
        await ctx.send("Opération annulée")
        return

    # Supprimer la new dans bot.news
    for new in bot.news:
        if new[0] == nom_new:
            bot.news.remove(new)



    # Inscrire bot.news dans le fichier texte externe

    # vider le fichier
    open("news", "w")

    # écrire dedans 
    with open("news", "a") as file:
        for new in bot.news:
            file.write(f"{new[0]}~|~{new[1]}\n")

    await ctx.send(f"{nom_new} supprimé.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.send("Erreur : Commande inconnue\nEssayez `!help` pour obtenir de l'aide.")
        return
    raise error

bot.run("token")

