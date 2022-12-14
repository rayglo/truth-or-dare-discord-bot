import os
import random
import interactions
import mysql.connector

bot = interactions.Client(token=os.getenv("token"))

@bot.command(name="truth",
             description="A cool question for you",
             options=[
                 interactions.Option(
                     name="question_type",
                     description="You can choose either a chill or reflective question",
                     type=interactions.OptionType.STRING,
                     required=False,
                     choices=[
                         interactions.Choice(name="chill", value="chill"),
                         interactions.Choice(name="reflective", value="reflective")
                     ]
                 ),
             ])
async def truth(ctx: interactions.CommandContext, question_type: str = None):
    db = mysql.connector.connect(host=os.getenv("db_host"),
                                 user=os.getenv("db_user"),
                                 password=os.getenv("db_pass"),
                                 database=os.getenv("db_name"))
    print(f"Question requested. Type: {question_type}")
    if question_type is None or (question_type != "chill" and question_type != "reflective"):
        question_type = random.choice(["chill", "reflective"])
        print(f"Type assigned: {question_type}")
    if question_type == "chill":
        query1 = "SELECT chill_latest FROM servers WHERE server_id=%s"
        query2 = "SELECT id, truth_text FROM chill_truths ORDER BY RAND() LIMIT 1;"
        query3 = "UPDATE servers SET chill_latest = %s WHERE server_id=%s"

    if question_type == "reflective":
        query1 = "SELECT reflective_latest FROM servers WHERE server_id=%s"
        query2 = "SELECT id, truth_text FROM reflective_truths ORDER BY RAND() LIMIT 1;"
        query3 = "UPDATE servers SET reflective_latest = %s WHERE server_id=%s"

    c = db.cursor()
    c.execute(query1, (str(ctx.guild_id),))
    recent_questions_1 = (c.fetchone()[0]).split(',')
    recent_questions_2 = [int(x) for x in recent_questions_1]
    c.close()

    c = db.cursor()
    c.execute(query2),
    (id, response) = c.fetchone()
    c.close()
    while id in recent_questions_2:
        c = db.cursor()
        c.execute(query2),
        (id, response) = c.fetchone()
        c.close()

    print(f"picked question {id} from {question_type}_truths")
    if len(recent_questions_2) >= 10:
        recent_questions_2.pop()
    recent_questions_2.insert(0, id)
    converted_questions = [str(x) for x in recent_questions_2]

    c = db.cursor()
    c.execute(query3, (",".join(converted_questions), str(ctx.guild_id)))
    db.commit()
    c.close()
    db.close()
    await ctx.send(embeds=interactions.Embed(title=response, description=f"type: {question_type} | id: {id}"))

@bot.command(name="help",
             description="How to use Truth or Dare!")
async def help(ctx: interactions.CommandContext):
    await ctx.send(embeds=interactions.Embed(title="Help", description='Use the truth slash command to get a question. '
                                                                 'Questions can be of two types:\n\n'
                                                                 '-chill: Simple questions about everyday stuff\n'
                                                                 '-reflective: Questions about more personal and deep topics\n\n'
                                                                 'You can specify as an optional argument the type of question '
                                                                 '(chill or reflective).\nAt the moment only "truths" are available.\n\n'
                                                                 'Credits - Programming: rayglo - Questions: Sock'))

@bot.event()
async def on_guild_create(ctx: interactions.api.Guild):
    db = mysql.connector.connect(host=os.getenv("db_host"),
                                 user=os.getenv("db_user"),
                                 password=os.getenv("db_pass"),
                                 database=os.getenv("db_name"))
    query1 = "SELECT COUNT(*) FROM servers WHERE server_id=%s"
    c = db.cursor()
    c.execute(query1, (int(ctx.id),))
    result = c.fetchone()[0]
    c.close()
    c = db.cursor()
    if result == 0:
        query2 = "INSERT INTO servers(server_id,server_name,chill_latest,reflective_latest)" \
                 "VALUES (%s,%s,'0,0,0,0,0,0,0,0,0,0','0,0,0,0,0,0,0,0,0,0');"
        c.execute(query2, (str(ctx.id), str(ctx.name)))
        print(f"Inserting id: {ctx.id}, name: {ctx.name}")
    else:
        query2 = "UPDATE servers SET server_name = %s WHERE server_id=%s;"
        c.execute(query2, (str(ctx.name), str(ctx.id)))
        print(f"Updating id: {ctx.id}, name: {ctx.name}")
    db.commit()
    c.close()
    db.close()

print("Bot is starting")
bot.start()
