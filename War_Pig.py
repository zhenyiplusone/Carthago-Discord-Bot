'''
This is a bot that allows for the users to create coordination channels
for war purposes. It can either do that through bulk creating channels
with a CSV as input or create a single one.

:Date: 7/4/2020
:Versions: 1
:Author:
    -Piggy
'''

import csv
import re
import discord
import requests
#import excel2img
import time
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import math
import gspread
from scipy import stats
from bs4 import BeautifulSoup
from discord.ext import commands
from openpyxl.styles import Font
from openpyxl.styles import colors
from API import get_pnw_name
from API import get_pnw_mil
from API import get_war_info
from API import get_all_war_info
from API import get_leader
from API import get_cities
from API import req_info
from openpyxl import load_workbook

client = commands.Bot(command_prefix = '!')


gaccount = gspread.service_account(filename = 'war pig-9478580af5de.json')

gsheet = gaccount.open("Discord Tracking Sheet").sheet1
member_names = gsheet.col_values(1)
member_names.pop(0)
nation_id = gsheet.col_values(2)
nation_id.pop(0)
dis_id = gsheet.col_values(4)
dis_id.pop(0)
nation_id = list(map(int, nation_id))
dis_id = list(map(int, dis_id))
member_dict = dict(zip(member_names, dis_id))
nation_dict = dict(zip(dis_id, nation_id))  
rev_nation_dict = dict(zip(nation_id, dis_id))   


'''member_names = ['Azrael','New Suleiman','Daveth','Locinii','Lothair of Acre','GrandmasterBee','Bmber',
'Aaron Comneno','Asierith','Auto Von Bismarck','Ragnarok8085','Tamasith','Velium','Thibaud Brent',
'Billy','Petko Vidmar','Roach','Al Sahina','Patro','Yuri B Molotov','Miyamoto Musashi',
'Ion Constantinescu','Zeannon','Uhsnadev','Shawn Washington','the Rising Sun',
'Wilhelm-Augustus','NotCool','Cthulhu The Devourer','Strett','Antonio','Tyras Calidan',
'Waldo','KingDracula','Leigh','Gust','CaN','Madder Red','Germania','El Chach','Solomoriah',
'Zegrath the Black', 'EvilPiggyFooFoo', 'Romanov', 'Novorossiya', 'Filedsome','Karl the not Blessed',
'Shamadruu','Misha Polikarpov']

dis_id = [203472925737746432,252246017725038593,285413989658263552,305437895538507780,537421144731549707,
323631619456106507,401403136171835415,401145199310667783,369554334431838208,616473001189441541,398868908724977675,
254609285957419018,231148725618081792,354759477196488704,175719252995604480,350791629570965504,236630567561592832,
434341682507415552,489408350459789314,445347365969199135,448650823375912970,312373154884616222,364957447988969472,
294156214454190083,367273586102239234,315607812149608458,380826721634746388,582844188760997908,197031131093139465,
456554347963088909,154719217558618113,111543344521302016,441584968838152192,415335544541937665,458799865271418892,
339330441603710977,328153663984107521,174116297951412225,400787601503682597,465869010936922112,669983109986385965,
404132209692508160, 236978935538122754,274757222528057344, 720666834562711554, 594794583204823041, 711090812439756833,
181502175476711425, 208495718376275968]

nation_id = [90038,36823,60766,205677,174178,207627,105773,207541,123779,206764,127170,
68432,93798,211650,92845,146455,192256,203465,208360,117448,112098,116152,84969,194419,
205543,118419,215354,163576,217361,125354,109837,21196,117241,125702,196166,76312,134372,
148081,99210,128633,195412,204729, 48730,195344,207245, 212190, 213815, 234558, 231415]'''

@client.event
async def on_ready():
    '''
    Lets user know bot is ready
    '''
    print('Ready to go')




@client.command()
async def bulk_create(ctx):
    '''
    Creates a list of channels based on csv target list
    '''
    category = discord.utils.get(ctx.guild.categories, name = '[CANNAE BUT COUNTER]')

    #Sees if the user has permissions to manage channels in the category and access bot
    if category.permissions_for(ctx.author).manage_channels:
        
        #for loop to get attachment
        for attachment in ctx.message.attachments:
            await attachment.save(f'csv/{attachment.filename}')
            await ctx.send('Creating war channels...')
            break
        #If no attachment is found
        else:
            await ctx.send('No Attachment Found')

        #Access attachment and creates channels with it
        with open(f'csv/{attachment.filename}') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line = 0
            update_dict()
            #Goes through each row to create channels
            for row in csv_reader:
                #Makes sure this is not the heading and it isn't an invalid row before creating a channel
                if line != 0 and row[1] != '#ERROR!':
                    print(f'{row[1]} is the target. Attacker 1 is {row[4]}, attacker 2 is {row[6]},\
                     and attacker 3 is {row[8]}')
                    target_name = row[1]
                    target_id = row[2]
                    attackers = [row[4], row[6], row[8]]
                    defenders = [row[11],row[13],row[15],row[17],row[19]]
                    channel_name = target_name.replace(' ', '-') + '-' + target_id

                    #Creates the channel and edits the topic
                    channel = await ctx.guild.create_text_channel(channel_name, category = category, topic = f'War on {row[0]}')
                    

                    war_embed = discord.Embed(title= f"⚔️ __Target: {channel_name.split('-')[0]}__", 
                        description= f"Please declare war on {row[0]}", color=0xcb2400,
                        url = f'https://politicsandwar.com/nation/war/declare/id={row[0].split("=")[1]}')


                    mil_count = get_pnw_mil(f'https://politicsandwar.com/nation/id={row[0].split("=")[1]}')

                    war_embed.add_field(name = '__Military Information:__', value = f'{channel_name.split("-")[0]} has {mil_count["Soldiers"]} soldiers, {mil_count["Tanks"]} tanks, {mil_count["Planes"]} planes, and {mil_count["Ships"]} ships', inline = False)

                    ping_list = await coord_perms(attackers, channel, channel_name, ctx)
                    for index, member in enumerate(ping_list): 
                        link = f'https://politicsandwar.com/nation/id={nation_dict.get(member, "N/A")}'
                        war_embed.add_field(name= f"__Attacker {index + 1}:__", value=f"[{client.get_user(member).display_name}]({link})", inline=True)

                    def_ping_list = await coord_perms(defenders, channel, channel_name, ctx)
                    for index, member in enumerate(def_ping_list): 
                        link = f'https://politicsandwar.com/nation/id={nation_dict.get(member, "N/A")}'
                        war_embed.add_field(name= f"__Defender {index + 1}:__", value=f"[{client.get_user(member).display_name}]({link})", inline=True)

                    war_embed.add_field(name="__Reminder__", value="1.) Make sure you have enough resources including food and uranium, ping gov if you need more\
                            \n 2.) Look over their military before going in and plan out the best move\
                            \n 3.) Talk and coordinate with fellow members, declare at the same time and help each other\
                            \n Good luck!", inline=False)

                    await channel.send(f'{ping(ping_list)}{ping(def_ping_list)}',embed = war_embed)

                    #Gets the permissions for the members set up and pings them

                line += 1

            await ctx.send('Channels are finished being create, good luck in the wars to come!')
    #If they don't have permission, tell them
    else:
        await ctx.send('You do not have permissions to create war channels')




"""
@client.command()
async def run_test_sheet(ctx):
    with open(f'csv/Blitz_Sheet_1_-_Sheet1.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line = 0
        for row in csv_reader:
            if line != 0:
                print(f'{row[1]} is the target. Attacker 1 is {row[4]}, attacker 2 is {row[6]}, and attacker 3 is {row[8]}')
                target_name = row[1]
                target_id = row[2]
                attackers = [row[4], row[6], row[8]]
                defenders = [row[11],row[13],row[15],row[17],row[19]]

                category = discord.utils.get(ctx.guild.categories, name = 'War-Test')
                channel_name = target_name.replace(' ', '-') + '-' + target_id

                await ctx.guild.create_text_channel(channel_name, category = category)

                channel = discord.utils.get(ctx.guild.text_channels, name = channel_name.lower())

                await channel.edit(topic = f'War on {row[0]}')
                

                ping_list = await coord_perms(attackers, channel, channel_name, ctx)
                await channel.send(f'{ping(ping_list)}please declare war on {row[0]}\
                    \n 1.) Make sure you have enough resources including food and uranium, ping gov if you need more\
                    \n 2.) Look over their military before going in and plan out the best move\
                    \n 3.) Talk and coordinate with fellow members, declare at the same time and help each other\
                    \n Good luck!') 

                ping_list = await coord_perms(defenders, channel, channel_name, ctx)
                await channel.send(f'{ping(ping_list)}is/are defending against {target_name}') 

            line += 1
"""



@client.command()
async def create_chan(ctx, nation_link, reason = None, *members: discord.Member):
    ''' 
    Creates a channel using nation link and the list of members to add to it

    :param nation_link: PnW link of nation that is the target
    :param *members: Discord members to add to the channel
    '''
    category = discord.utils.get(ctx.guild.categories, name = '[CANNAE BUT COUNTER]')

    #Checks if they have the permission to create these channels
    if category.permissions_for(ctx.author).manage_channels:

        #Makes sure that the nation_link is in the right format
        if(re.search(r'politicsandwar.com/nation/id=\d{1,7}', nation_link)):
            channel_name = get_pnw_name(nation_link).replace(' ', '-') + '-' + nation_link.split('=')[1]

            channel = await ctx.guild.create_text_channel(channel_name, category = category, topic = f'War on {nation_link}')
            update_dict()

            if re.match(r'<@!\d{18}\>', reason):
                id = int(reason.split('!')[1].split('>')[0])
                print(id)
                print(client.get_user(int(reason.split('!')[1].split('>')[0])))
                members += (client.get_user(id),)
                reason = ''
            #For loop to set permissions for members
            ping = ''
            for member in members:
                await channel.set_permissions(member, read_messages=True, send_messages=True)
                ping = ping + f'<@{member.id}> '
            
            if reason != '':
                reason = reason.replace('-', ' ')
                reason = f', war reason: {reason}'
            war_embed = discord.Embed(title= f"⚔️ __Target: {channel_name.split('-')[0]}__", 
                description= f"Please declare war on {nation_link}{reason}", color=0xcb2400,
                url = f'https://politicsandwar.com/nation/war/declare/id={nation_link.split("=")[1]}')


            mil_count = get_pnw_mil(f'https://politicsandwar.com/nation/id={nation_link.split("=")[1]}')

            war_embed.add_field(name = '__Military Information:__', value = f'{channel_name.split("-")[0]} has {mil_count["Soldiers"]} soldiers, {mil_count["Tanks"]} tanks, {mil_count["Planes"]} planes, and {mil_count["Ships"]} ships', inline = False)

            for index, member in enumerate(members): 
                link = f'https://politicsandwar.com/nation/id={nation_dict.get(member.id, "N/A")}'
                war_embed.add_field(name= f"__Attacker {index + 1}:__", value=f"[{member.display_name}]({link})", inline=True)
           
            war_embed.add_field(name="__Reminder__", value="1.) Make sure you have enough resources including food and uranium, ping gov if you need more\
                    \n 2.) Look over their military before going in and plan out the best move\
                    \n 3.) Talk and coordinate with fellow members, declare at the same time and help each other\
                    \n Good luck!", inline=False)

            await channel.send(f'{ping}',embed = war_embed)

        #Lets user know that nation_link is in wring format
        else:
            await ctx.send('Nation link format is wrong, must be politicsandwar.com/nation/id=xxxxx')
    #Tells them if they don't have the permission to create the channel
    else:
        await ctx.send('You do not have permissions to create war channels')




@client.command()
async def clear_expired(ctx):
    ''' 
    Deletes all the channels that have expired wars and have become usless

    '''
    category = discord.utils.get(ctx.guild.categories, name = '[CANNAE BUT COUNTER]')

    #Checks if they have the permission to create these channels
    if category.permissions_for(ctx.author).manage_channels:
        #Runs for loop thru all the channels to find obsolete ones
        for channel in category.channels:
            active_war = False
            topic = channel.topic
            try:
                nation_link = topic.split()[2]
                #Goes through a nation's wars and see if they still have wars with Carthago
                for war in get_war_info(nation_link):
                    print(war)
                    if war['Aggressor Alliance'] == 'Carthago' or war['Defender Alliance'] == 'Carthago':
                        active_war = True
                        break

                if active_war == False:
                    await ctx.send(f'The war channel {channel.name} has been deleted.')
                    await channel.delete(reason="No existing Carthago wars with this nation")
            except AttributeError:
                await ctx.send(f"The war channel {channel.name} does not have a topic, thus we are unable to determine if war has been expired")

            except: 
                await ctx.send(f'Unexpected error has occured with {channel.name}, get piggy on it.')
    #Tells them if they don't have the permission to create the channel
    else:
        await ctx.send('You do not have permissions to create war channels')



@client.command()
@commands.cooldown(1, 60, commands.BucketType.channel)
async def war_info(ctx):
    '''
    Gets the all war information about the target nation

    '''
    message = await ctx.send('Gathering information... please wait a few moments')
    book = load_workbook('spreadsheet/War.xlsx')
    sheet = book.active #active means last opened sheet
    try:
        nation_link = ctx.channel.topic.split()[2]
        target_id = nation_link.split('=')[1]
        sheet[f'B3'] = get_pnw_name(nation_link)

        #clears all old cells
        for row in sheet['B3:S3']:
          for cell in row:
            cell.value = None

        for row in sheet['B6:S8']:
          for cell in row:
            cell.value = None

        for row in sheet['B10:S14']:
          for cell in row:
            cell.value = None

        #gets their basic military information and fills it in
        nation_info = req_info(nation_link)
        sheet[f'B3'] = nation_info['name']
        sheet[f'C3'] = nation_info['alliance']
        sheet[f'F3'] = nation_info['offensivewars']
        sheet[f'H3'] = nation_info['nationid']
        sheet[f'K3'] = nation_info['cities']
        sheet[f'L3'] = nation_info['soldiers']
        sheet[f'M3'] = nation_info['tanks']
        sheet[f'N3'] = nation_info['aircraft']
        sheet[f'O3'] = nation_info['ships']

        #Function to fill in war information for offensive and defensive wars@
        def war_fill(row, war, ID):
            sheet[f'D{row}'] = war['turns_left']

            #Basic control
            if war['ground_control'] == ID:
                sheet[f'P{row}'] = '✔'
            elif war['ground_control'] == target_id:
                sheet[f'P{row}'] = '✖'

            if war['air_superiority'] == ID:
                sheet[f'Q{row}'] = '✔'
            elif war['air_superiority'] == target_id:
                sheet[f'Q{row}'] = '✖'

            if war['blockade'] == ID:
                sheet[f'R{row}'] = '✔'
            elif war['blockade'] == target_id:
                sheet[f'R{row}'] = '✖'
            
            req = req_info(f'https://politicsandwar.com/nation/id={ID}')
            sheet[f'B{row}'] = req['leadername']
            sheet[f'K{row}'] = req['cities']
            sheet[f'E{row}'] = req['defensivewars']
            sheet[f'F{row}'] = req['offensivewars']
            sheet[f'L{row}'] = req["soldiers"]
            sheet[f'M{row}'] = req["tanks"]
            sheet[f'N{row}'] = req["aircraft"]
            sheet[f'O{row}'] = req["ships"]

        #Fils in offensive war unique attributes
        off_wars = get_all_war_info(nation_link, True)
        for index, war in enumerate(off_wars):
            row = index + 10
            sheet[f'C{row}'] = war['defender_alliance_name']
            sheet[f'G{row}'] = war['defender_military_action_points']
            sheet[f'H{row}'] = int(war['defender_resistance'])
            sheet[f'I{row}'] = int(war['aggressor_resistance'])
            sheet[f'J{row}'] = war['aggressor_military_action_points']
            war_fill(row, war, war['defender_id'])

        #Fills in defensive war unique attributes
        def_wars = get_all_war_info(nation_link, False)
        for index, war in enumerate(def_wars):
            row = index + 6
            sheet[f'C{row}'] = war['aggressor_alliance_name']
            sheet[f'G{row}'] = war['aggressor_military_action_points']
            sheet[f'H{row}'] = int(war['aggressor_resistance'])
            sheet[f'I{row}'] = int(war['defender_resistance'])
            sheet[f'J{row}'] = war['defender_military_action_points']
            war_fill(row, war, war['aggressor_id'])


        book.save('spreadsheet/War.xlsx')

        #excel2img.export_img("spreadsheet/War.xlsx","spreadsheet/image.png","War Scenario Sheet")
        #image = discord.File("spreadsheet/image.png", filename="war_screen.png")
        sheet = discord.File('spreadsheet/War.xlsx', filename="war_sheet.xlsx")
        await message.delete()
        await ctx.send(file = sheet)
    
    #Except block
    except AttributeError:
        await ctx.send(f"The war channel {ctx.channel.name} does not have the correct topic format. We can not grab information for the war.")

    except: 
        await ctx.send(f'Unexpected error has occured with {ctx.channel.name}, get piggy on it.')





@client.command()
@commands.cooldown(1, 30, commands.BucketType.user)
async def graph(ctx, type, *alliances): 
    '''
    Graphs specific information for alliances
    :param type: is the type of graph
    :param alliances: is the list of alliances to graph

    '''
    message = await ctx.send('Generating graph... please wait a few moments')

    #graphs histogram 
    if re.search('hist', type):
        alliances_data = []
        label = []

        #Makes it in the right format to be entered in url
        for name in alliances:
            label.append(name.replace('+', ' ').title())

        #Runs through alliances and sees the number of nations
        for ally in alliances:
            await message.edit(content = f'Gathering information from {ally.replace("+", " ").title()}')
            print(ally)
            res = requests.get(f'https://politicsandwar.com/index.php?id=15&keyword={ally}&cat=alliance&ob=score&od=DESC&maximum=15&minimum=0&search=Go&memberview=true')
            soup_data = BeautifulSoup(res.text, 'html.parser')
            data = soup_data.find(text = re.compile('Showing'))
            num_nations = float(data.split()[3])
            
            #Error handling for if the number of nations for the alliance is 0
            if num_nations == 0:
                await ctx.send(f'Could not find any nations in the alliance {ally.replace("+", " ").title()}, make sure it is spelled correctly')
                label.remove(ally)
                continue
            alliance_city_data = []

            #Grabs data for every nation in the alliance
            for nations in range(0, math.ceil(num_nations/50)):
                res = requests.get(f'https://politicsandwar.com/index.php?id=15&keyword={ally}&cat=alliance&ob=score&od=DESC&maximum={50*(nations+1)}&minimum={50*nations}&search=Go&memberview=true')
                soup_data = BeautifulSoup(res.text, 'html.parser')
                data = soup_data.find_all("td", attrs={"class": "right"}, text = re.compile(r'^[1-9]\d*$'))

                for city in data:
                    alliance_city_data.append(float(city.contents[0]))
                    #alliance_city_data[city.contents[0]] += 1
            alliance_city_data = np.array(alliance_city_data)
            alliances_data.append(alliance_city_data)

        #Creates graph
        fig, axes = plt.subplots(nrows=1, ncols=2)
        ax0, ax1 = axes.flatten()
        fig.set_figheight(10)
        fig.set_figwidth(20)

        #Comparison histogram
        n_bins = max(list(map(lambda x: np.amax(x), alliances_data))).astype(np.int64)+1
        if type == 'hist-static' or type == 'hist-static':
            n_bins = 45
            ax0.set_ylim(0, 100)
            ax1.set_ylim(0, 100)
        ax0.hist(alliances_data, range(n_bins+1), histtype='bar', label=label)
        ax0.legend(loc = 0)
        ax0.set_title('Comparison Graph')
        ax0.xaxis.set_ticks(np.arange(0, n_bins, 3))
        plt.setp(ax0.get_xticklabels(), rotation=30, horizontalalignment='right')

        #Stacked histogram
        ax1.hist(alliances_data, range(n_bins+1), histtype='bar', stacked=True)
        ax1.set_title('Stacked Histogram')
        ax1.xaxis.set_ticks(np.arange(0, n_bins, 1))
        plt.setp(ax1.get_xticklabels(), rotation=30, horizontalalignment='right')
        fig.savefig('graph.png', dpi = 300)

        #Sends file onto Discord
        pic = discord.File('graph.png', filename="graph.png")
        await message.delete()
        await ctx.send(file = pic)

    #Graphs for scatter plot with military informationS
    elif re.search('scat', type):
        milplot_array = np.array([['Alliance', 'Leader Name', 'Age', 'Cities', 'Soldiers Killed', 'Soldier Casualties'\
        , 'Tanks Killed', 'Tank Casualties', 'Planes Killed', 'Plane Casualties'\
        , 'Ships Killed', 'Ship Casualties', 'Infra Destroyed', 'Infra Lost', 'Money Looted']], dtype = object)

        html = []
        #Gets it in the right format for html
        for alliance in alliances: 
            html.append(alliance.replace(' ', '+'))

        alliances_data = []

        #Goes through each alliance and gets the nation links
        for ally in html:
            await message.edit(content = f'Gathering information from {ally.replace("+", " ").title()}')
            res = requests.get(f'https://politicsandwar.com/index.php?id=15&keyword={ally}&cat=alliance&ob=score&od=DESC&maximum=15&minimum=0&search=Go&memberview=true')
            soup_data = BeautifulSoup(res.text, 'html.parser')
            data = soup_data.find(text = re.compile('Showing'))
            num_nations = float(data.split()[3])
            #Error handling if alliance has no nations
            if num_nations == 0:
                await ctx.send(f'Could not find any nations in the alliance {ally.replace("+", " ").title()}, make sure it is spelled correctly')
                label.remove(ally)
                continue

            alliance_city_data = []
            #alliance_city_data = defaultdict(lambda: 0, alliance_city_data)

            #Goes to every nation in the alliance to grab military information
            for nations in range(0, math.ceil(num_nations/50)):
                res = requests.get(f'https://politicsandwar.com/index.php?id=15&keyword={ally}&cat=alliance&ob=score&od=DESC&maximum={50*(nations+1)}&minimum={50*nations}&search=Go&memberview=true')
                soup_data = BeautifulSoup(res.text, 'html.parser')
                data = soup_data.find_all("a", href=re.compile("politicsandwar.com/nation/id="))
                links = []

                for nation_link in data:
                    links.append(nation_link['href'])

                for nation_link in links:
                    mil = req_info(nation_link)

                    #Creates dataframe
                    member_info = [mil['alliance'], mil['leadername'], int(mil['daysold']), mil['cities'],\
                        int(mil['soldierskilled']), int(mil['soldiercasualties']),int(mil['tankskilled']),int(mil['tankcasualties']),\
                        int(mil['aircraftkilled']),int(mil['aircraftcasualties']),int(mil['shipskilled']),int(mil['shipcasualties']),\
                        float(mil['infdesttot']),int(mil['infraLost']),float(mil['moneyLooted'])]

                    temp_arr = np.array([member_info], dtype = object)

                    milplot_array = np.append(milplot_array, temp_arr, axis=0)
       

        await message.edit(content = f'Creating Graph')
        mil = pd.DataFrame(milplot_array[1:], range(len(milplot_array)-1), milplot_array[0])
        mil.to_excel('Excel_Sample.xlsx', sheet_name = 'Sheet1')
        df = pd.read_excel('Excel_Sample.xlsx', sheet_name = 'Sheet1')
        print(mil.head())

        stuff_to_graph = ['Money Looted', 'Infra Destroyed', 'Planes Killed']

        await message.delete()

        #Creates graph
        for image in stuff_to_graph:
            scattered0 = sns.lmplot(x = 'Age', y = image, data = df, hue = 'Alliance')
            ann(df, image)
            scattered0.savefig(f"Scatter Plot Of {image}.png")

            pic = discord.File(f"Scatter Plot Of {image}.png", filename=f"Scatter Plot Of {image}.png")
            await ctx.send(file = pic)
   #If type is something weird
    else:
        await ctx.send(f'We are unable to identify graph type: {type}. The valid graph types are hist/hist-static and scatter.')




@client.command()
async def add(ctx, type, reason = None, *nations): 
    reason = reason.replace('-', ' ')
    reason = f'The war reason is: {reason}'
    if re.search(r'\d{1,7}', reason):
        nations += (reason,)
        reason = ''

    if type == 'attacker' or type == 'attackers' or type == 'atker' or type == 'atkers' or type == 'atk' or type == 'atks' or type == 'attack' or type == 'attacks':
        ping = await add_to_chan(ctx, nations)
        if len(ping) != 0:
            ping_list = ' '.join([f'<@{member}>' for member in ping])
            await ctx.send(f'{ping_list} please read above and declare war on {ctx.channel.topic.split()[2]}. {reason}')

    elif type == 'defender' or type == 'defenders' or type == 'def' or type == 'defs' or type == 'defend' or type == 'defense':
        ping = await add_to_chan(ctx, nations)
        if len(ping) != 0:
            ping_list = ' '.join([f'<@{member}>' for member in ping])
            target = " ".join(ctx.channel.name.split('-')[:-1])
            await ctx.send(f'{ping_list} is defending. Please coordinate with the other Carthago members here for the war against {target.title()}.')
    else:
        await ctx.send('Invalid command format. Please do !add <atk/def> <nation link/id> <nation link/id> etc.')



async def coord_perms(members, channel, channel_name, ctx):
    ''' 
    Sets the permissions of the members by adding them to the coordination channel

    :param members: leader name of members to add to the channel
    :param channel: Channel object to add members to
    :param channel_name: Name of the channel
    :returns: String list of people to ping
    ''' 
    people_to_ping = []
    #Goes through every member in the list of members
    for member in members:
        #Only adds them if they're valid values
        if member != '#ERROR!' and member != '' and member != '#VALUE!':
            discord_name = member_list(member)
            print(ctx.guild.get_member(discord_name))
            #Makes sure that it adds valid users
            if discord_name != '':
                await channel.set_permissions(ctx.guild.get_member(discord_name), read_messages=True, send_messages=True)
                people_to_ping.append(discord_name)
            #Tells gov to manually add users if they're invalid
            else:
                await ctx.send(f"Couldn't find the Discord for {member}, please add them manually to {channel_name}")
        #Stops the loop if invalid users come up because that means the end of the list
        else:
            return people_to_ping
            break
    #Returns it if there were no invalid users and the loop has reached its end
    else:
        return people_to_ping




async def add_to_chan(ctx, nations):
    update_dict()
    members = []
    for nation in nations:
        if(re.search(r'politicsandwar.com/nation/id=\d{1,7}', nation)) and int(nation.split('=')[1]) in rev_nation_dict:
            member = ctx.guild.get_member(rev_nation_dict[int(nation.split('=')[1])])
            await ctx.channel.set_permissions(member, read_messages=True, send_messages=True)
            members.append(rev_nation_dict[int(nation.split('=')[1])])

        elif(re.match(r'\d{1,7}', nation)) and int(nation) in rev_nation_dict:
            member = ctx.guild.get_member(rev_nation_dict[int(nation)])
            await ctx.channel.set_permissions(member, read_messages=True, send_messages=True)
            members.append(rev_nation_dict[int(nation)])
            
        else:
            await ctx.send(f"Couldn't find member {nation}, either the member sheet is not updated or it is not a nation link/nation ID.")
    return members

'''
@client.command()
async def find_members(ctx):
    member_dis = ['Kraмpus','Kebab','Daveth','Tumatauenga','michaelborg','Grandmaster Bee',
    'CoolPerson125','bmber','Cyr_0nos','Asierith','KaiserLuch','Rag',
    'Tamasith','velium','Rohan Nair','Billy','Petko | Kosi |' 
    'Estival','Hans','ᴛʜᴇᴋɪᴅᴍᴀᴅᴇɪᴛ!','Duckman','Yuri Molotov','Cyrus' ,
    'NapoleonIII','Zeannon','Vedanshu','Gladiator Greyman','JayC',
    'GM (Noah)','NotCool','CthulhuTDOW','Strett',
    'Gallant Aegis','DyNasty','Waldo','Kingdracula','Leigh','Gust','Can','Madder Red#']

    member_ids = list(map(lambda member: discord.utils.get(ctx.guild.members, name = member).id if discord.utils.get(ctx.guild.members, name = member)!= None else None,member_dis))
    print(member_ids)'''




def member_list(leader_name):
    '''
    Find the discord ID of the member given their leader name

    :returns: The Discord ID of the member
    '''
    print(member_dict)
    return member_dict.get(leader_name, '')





def ping(ping_list):
    '''
    Creates a string in which the bot can then ping all the members

    :returns: The string in which the bot can ping all the members to declare war
    '''
    ping_str = ''
    for member in ping_list:
        ping_str += f'<@{str(member)}> '
    return ping_str



def ann(df, value):
    '''
    Annotates the graph with the outliers
    :param df: is the dataframe
    :param value: Is the value to find outliers in

    '''
    slope, intercept, r_value, p_value, std_err = stats.linregress(df['Age'],df[value])
    std_resid = math.sqrt((sum((df[value] - slope * df['Age'])**2))/(len(df.index)-2))
    print(f'slope - {slope}, intercept - {intercept} std_resid - {std_resid}')
    outliers = df[df[value] > (slope * df['Age'] + 0.8 * std_resid)]
    plt.ylim(0, None)
    plt.title(f'Scatter Plot of Nation Age Vs {value}')
    for row in outliers.iterrows():
        r = row[1]
        plt.gca().annotate(f'{r["Leader Name"]}, {r["Cities"]}', xy=(r['Age'], r[value]), xytext=(2,2) , textcoords ="offset points", )



def update_dict():
        member_names = gsheet.col_values(1)
        member_names.pop(0)
        nation_id = gsheet.col_values(2)
        nation_id.pop(0)
        dis_id = gsheet.col_values(4)
        dis_id.pop(0)
        nation_id = list(map(int, nation_id))
        dis_id = list(map(int, dis_id))
        member_dict = dict(zip(member_names, dis_id))
        nation_dict = dict(zip(dis_id, nation_id))    





@create_chan.error
async def create_chan_error(ctx, error):
    '''
    Function to catch any errors in create_chan
    '''
    #If the member given is invalid
    if isinstance(error, commands.BadArgument):
        await ctx.send('I could not find the member(s)')
    #If the user forgets to input in members or the nation link
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Missing required argument, the correct format is:\
            !create_chan [nation_link] @member @member ... etc')
    else:
        await ctx.send(error)

#If the command is on cooldown
@war_info.error
async def war_info_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'The command is on cooldown for this channel, please try again in {error.retry_after:.3g} seconds')

@graph.error
async def graph_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'The command is on cooldown for you, please try again in {error.retry_after:.3g} seconds')




client.run('Mzk4MTk4ODQwNjA1NTQwMzUy.Xv6yug.fFWMqpyqJAYX0nFKYiBIsSEiUYk')
#things to do tommorow, make all defender and attacker nation links avaliable so less scrolling and display the target
#make it so war_info only accessible in canea but counter