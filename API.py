"""
This script gets information from PnW API
"""
import requests
import json

api_key = '69e9cc72114cd2'

def get_pnw_name(link):
    """
    Uses a link from PnW and gets the name of the nation
    :param link: is the nation link of the nation
    :returns: name of the nation
    """
    req = req_info(link)
    return req['name']



def get_leader(id):
    """
    Uses an id from PnW and gets the name of the nation
    :param link: is the ID of the nation
    :returns: leader of the nation
    """
    req = ID_info(id)
    return req['leadername']



def get_cities(id):
    """
    Uses an id from PnW and gets the number of cities of the nation
    :param link: is the ID of the nation
    :returns: the number of cities of a nation
    """
    req = ID_info(id)
    return req.get('cities')



def req_info(link):
    """
    Uses a link from PnW and gets all the information from nation
    :param link: is the nation link of the nation
    :returns: Json information from PnW nation
    """
    nation_id = link.split('=')[1]
    return requests.get(f'https://politicsandwar.com/api/nation/id={nation_id}&key={api_key}').json()



def get_pnw_mil(link):
    '''
    Gets information about the military of a nation
    :param link: is the nation link
    :returns: the amount of military in a dictionary
    '''
    req = req_info(link)
    print(link)
    mil_count = {"Soldiers": req['soldiers'], "Tanks":req['tanks'],\
    "Planes":req['aircraft'], "Ships": req['ships']}
    return mil_count



def get_war_IDs(link):
    '''
    Gets the war IDs of all the wars of a nation
    :param link: is the target nation link
    :returns: war IDs of both offensive and defensive wars
    '''
    req = req_info(link)
    war_ids = req['offensivewar_ids'] + req['defensivewar_ids']
    return war_ids



def get_war_info(link):
    '''
    Gets the resistance and MAP of all of the wars of a nation
    :param link: is the nation link
    :returns: the amount of military in a dictionary
    '''
    for war in get_war_IDs(link):
        req = requests.get(f'https://politicsandwar.com/api/war/{war}&key={api_key}').json()
        war_info = {"Aggressor": ID_info(req["war"][0]['aggressor_id'])['name'],
        "Aggressor Alliance": req["war"][0]['aggressor_alliance_name'],
        "Defender": ID_info(req["war"][0]['defender_id'])['name'],
        "Defender Alliance": req["war"][0]['defender_alliance_name'],
        "Aggressor Resistance": req["war"][0]['aggressor_resistance'],
        "Defender Resistance": req["war"][0]['defender_resistance'],
        "Aggressor MAP": req["war"][0]['aggressor_military_action_points'],
        "Defender MAP": req["war"][0]['defender_military_action_points']
        }
        yield war_info



def get_all_war_info(link, off):
    '''
    Similar to get_war_info except it gets all info instead of selective ones
    :param id: is the nation id
    :returns: the war info of that nation
    '''
    if off:
        off_ID = req_info(link)['offensivewar_ids']
        for war in off_ID:
            req = requests.get(f'https://politicsandwar.com/api/war/{war}&key={api_key}').json()
            war_info = req["war"][0]
            yield war_info
    else:
        def_ID = req_info(link)['defensivewar_ids']
        for war in def_ID:
            req = requests.get(f'https://politicsandwar.com/api/war/{war}&key={api_key}').json()
            war_info = req["war"][0]
            yield war_info


def ID_info(id):
    '''
    Uses nation ID to get nation info
    :param link: is nation ID
    :returns: nation information in json format
    '''
    return requests.get(f'https://politicsandwar.com/api/nation/id={id}&key={api_key}').json()

def alliance_nation_info(id):
    return requests.get(f'https://politicsandwar.com/api/nation/id={id}&key={api_key}').json()
if __name__ == '__main__':
    member_info = {'score': 2500.0}
    nations = requests.get(f'http://160.2.143.37:8080/nations/?key=davethsmellskrampuswhales&limit=50&alliance_name=carthago&defensivewars={{"$ne":3}}&color={{"$ne":"beige"}}&sort_key=score&sort_dir=-1&project={{"name":1,"score":1,"solders":1,"tanks":1,"aircraft":1,"ships":1}}').json()
    alliance_nations_in_range = [nation for nation in nations if (member_info['score'] * 0.75 <= nation['score'] <= member_info['score'] * 1.75 )]
    print(alliance_nations_in_range)

    #print(get_pnw_info('https://politicsandwar.com/nation/id=48730'))