import os
import random
import interactions
import mysql.connector

bot = interactions.Client(token=os.getenv("token"))
db = mysql.connector.connect(host=os.getenv("db_host"),
                             user=os.getenv("db_user"),
                             password=os.getenv("db_pass"),
                             database=os.getenv("db_name"))

c = db.cursor()
c.execute("SELECT COUNT(*) FROM truths")
n_truths = c.fetchone()[0]
print(f"rows in truths: {n_truths}")
c.close()


@bot.command(name="truth",
             description="comando di prova",
             scope=840200870359466004)
async def truth(ctx: interactions.CommandContext):
    query1 = "SELECT array_latest FROM servers WHERE server_id=%s"
    c = db.cursor()
    c.execute(query1, (str(ctx.guild_id),))
    recent_questions_1 = (c.fetchone()[0]).split(',')
    recent_questions_2 = [int(x) for x in recent_questions_1]
    c.close()
    n_rand = random.randrange(1, ((n_truths-1)*10)+2,10)
    while n_rand in recent_questions_2:
        n_rand = random.randrange(1, ((n_truths-1)*10)+2, 10)
    print(f"picked question: {n_rand}")
    if len(recent_questions_2) >= 10:
        recent_questions_2.pop()
    recent_questions_2.insert(0, n_rand)
    converted_questions = [str(x) for x in recent_questions_2]

    query2 = "UPDATE servers SET array_latest = %s WHERE server_id=%s"
    c = db.cursor()
    c.execute(query2, (",".join(converted_questions), str(ctx.guild_id)))
    db.commit()
    c.close()

    query3 = "SELECT truth_text FROM truths WHERE id=%s"
    c = db.cursor()
    c.execute(query3, (n_rand,))
    response = c.fetchone()[0]
    await ctx.send(response)
    c.close()


@bot.event()
async def on_guild_create(ctx: interactions.api.Guild):
    query1 = "SELECT COUNT(*) FROM servers WHERE server_id=%s"
    c = db.cursor()
    c.execute(query1, (int(ctx.id),))
    result = c.fetchone()[0]
    c.close()
    c = db.cursor()
    if result == 0:
        query2 = "INSERT INTO servers(server_id,server_name,array_latest) VALUES (%s,%s,'0,0,0,0,0,0,0,0,0,0');"
        c.execute(query2, (str(ctx.id), str(ctx.name)))
        print(f"Inserting id: {ctx.id}, name: {ctx.name}")
    else:
        query2 = "UPDATE servers SET server_name = %s, array_latest = '0,0,0,0,0,0,0,0,0,0' WHERE server_id=%s;"
        c.execute(query2, (str(ctx.name), str(ctx.id)))
        print(f"Updating id: {ctx.id}, name: {ctx.name}")
    db.commit()
    c.close()


bot.start()
