################################################################################
#                            User editable varables                            #
################################################################################
minimum_prob_required_item_drop_from_relic=0.90                                 #Set these values to some sort of string ('N/A') for example to use expected value probiblities instead of confidence probiblities (not reccomended, will sugest less farming time across the board)
minimum_prob_required_relic_drop_from_missions=0.90                             #Set these values to some sort of string ('N/A') for example to use expected value probiblities instead of confidence probiblities (not reccomended, will sugest less farming time across the board)
assume_full_squad_for_relic_missions=True                                       #This var allows you to assume you are running your relic farm with a full squad. If this is set to False then the program will assume you are solo farming
make_full_report=True                                                           #This var allows you to generate a report for all items in the game. This is good if you simply want to maximize your plat/hour farm on any item.
make_item_report=True                                                           #This var allows you to make a full report for a single item listed in the item_to_report var shown below
make_items_report=True                                                          #This var allows you to make a simplified report of a set of items. This is good if you are trying to get a particular item and you want to figure out the most efficent path
item_to_report='Nekros Prime Neuroptics Blueprint'                              #This is the item that you want to generate a full report on including all the posible ways to get it
items_list_path='items_list.csv'                                                #This is the path to the list of items you want to generate an abreviated report on
path_to_csv_file_with_relic_item_drop_rates_based_on_rarity=(
                                                         "Relic Drop table.csv")#This var is the path to the relationship table between rarity of an item and likelyhood of it droping from a particular relic. This must be defined before any function can run
path_to_csv_file_with_relic_refinement_costs='Relic refinement table.csv'       #This var is the path to the relationship table between the number of void traces you need to refine a relic for an improved rare drop rate
path_to_csv_file_with_mission_speeds='Mission speeds.csv'                       #This var is the path to the mission speed table. This table needs to be filled out to get an idea of how quickly you can get relic drops
void_traces_per_round=18                                                        #This is a guess of how many void traces you get per void trace farming run.
time_per_trace_run=5                                                            #This is a guess of how long in mins it takes to run a void mission. Void mission runs both generate void traces and crack relics.
nexux_stats_URL='https://api.nexushub.co/warframe/v1/items'                     #This is the API key for getting nexus stat prices
what_plat_price_to_use='buying'                                                 #This key can be set to buying or selling to do calculations based on buying or selling prices

################################################################################
#                             Defineing my objects                             #
################################################################################
class item:
    def __init__(self,name):
        self.name=name
        self.relic_rarities=[]
        
    def add_relic(self,relic_obj,rarity):
        assert isinstance(relic_obj, relic)
        assert [relic_obj,relic_obj.name,rarity] not in self.relic_rarities
        self.relic_rarities.append([relic_obj,relic_obj.name,rarity])
        if [self,self.name, rarity] not in relic_obj.item_rarities:
            relic_obj.add_item(self,rarity)
        assert [self, self.name, rarity] in relic_obj.item_rarities
    def find_rarity_from_relic(self,relic_obj):
        for row in self.relic_rarities:
            if row[0]==relic_obj:
                return row[-1]
        return ('We did not find that relic in your item object. '
                'make sure that '+self.name+' drops from the '+relic_obj.name+
                ' relic.')
    def vaulted(self):
        for relic_line in self.relic_rarities:
            relic_obj=relic_line[0]
            if not relic_obj.vaulted:
                return False
            return True
            

class relic:
    def __init__(self,name):
        self.name=name
        self.item_rarities=[]
        self.missions=[]

    def add_item(self,item_obj,rarity):
        assert isinstance(item_obj, item)
        assert [item_obj,item_obj.name,rarity] not in self.item_rarities
        self.item_rarities.append([item_obj, item_obj.name, rarity])
        if [self, self.name,rarity] not in item_obj.relic_rarities:
            item_obj.add_relic(self,rarity)
        assert [self, self.name, rarity] in item_obj.relic_rarities
    def find_rarity_from_item(self,item_obj):
        for row in self.item_rarities:
            if row[0]==item_obj:
                return row[-1]
        return ('We did not find that item in your relic object.'
                'make sure that '+item_obj.name+' drops from the '+self.name+
                ' relic.')

    def add_mission(self,mission_obj, rotation, prob):
        assert isinstance(mission_obj, mission)
        assert [mission_obj,rotation, prob] not in self.missions
        self.missions.append([mission_obj,rotation, prob])
        if (rotation not in mission_obj.rotations_table or 'drop_table' 
            not in mission_obj.rotations_table[rotation] or [self,prob] 
            not in mission_obj.rotations_table[rotation]['drop_table']):
            mission_obj.add_drop_rotation_prob(self,rotation,prob)
    def make_vaulted(self):
        self.vaulted=True
    def make_unvaulted(self):
        self.vaulted=False
        
class mission:
    def __init__(self,name):
        self.name=name
        self.rotations_table={}

    def add_mission_type(self, mission_type):
        self.mission_type=mission_type
    def add_mission_tier(self, mission_tier):
        self.mission_tier=mission_tier
    def add_rotation_timeing(self, rotation, time, drops_per_time):
        if rotation not in self.rotations_table:
            self.rotations_table[rotation]={}
        if 'timeings' not in self.rotations_table[rotation]:
            self.rotations_table[rotation]['timeings']=[['Number of Drops',
                                                        'Time']]
        self.rotations_table[rotation]['timeings'].append([drops_per_time,
                                                          time])
    def add_drop_rotation_prob(self,relic_obj,rotation,prob):
        assert isinstance(relic_obj, relic)
        if rotation not in self.rotations_table:
            missions_timeing_table.append([self.name,rotation,'',''])
            the_saver(path_to_csv_file_with_mission_speeds,
                      missions_timeing_table)
            self.add_rotation_timeing(rotation,'','')
        if 'drop_table' not in self.rotations_table[rotation]:
            self.rotations_table[rotation]['drop_table']=[]
        if [relic_obj,prob] not in (
                                  self.rotations_table[rotation]['drop_table']):
            self.rotations_table[rotation]['drop_table'].append(
                                                               [relic_obj,prob])
        if [self,rotation, prob] not in relic_obj.missions:
            relic_obj.add_mission(self, rotation, prob)
        assert [self,rotation, prob] in relic_obj.missions
    def get_times(self,rotation):
        return self.rotations_table[rotation]['timeings']

################################################################################
#                    Defineing my data collection functions                    #
################################################################################
import urllib2, csv, os, math
from operator import itemgetter
from bs4 import BeautifulSoup

def the_opener(file_path):
    if '.csv' in file_path:
        return_list=[]
        with open(file_path, 'rb') as csvfile:
            for row in csv.reader(csvfile, dialect='excel'):
                return_list.append(row)
    elif '.tsv' in file_path or '.txt' in file_path:
        return_list=[]
        fixed_file='\n'.join(open(file_path).read().split('\r'))
        for row in fixed_file.split('\n'):
            if row != '':
                return_list.append(row.split('\t'))
    return return_list
    
def the_saver(output_path, list_of_lists):
    with open(output_path,'wb') as csvfile:
        for row in list_of_lists:
            csv.writer(csvfile, dialect='excel').writerow(row)

def get_HTML_table(URL,table_class,table_count=0):
    html=urllib2.urlopen(URL).read()
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", attrs={"class":table_class})
    headings = [th.get_text() for th in table.find("tr").find_all("th")]
    headings_simplified=[]
    datasets = []
    for row in table.find_all("tr")[1:]:
        dataset = zip(headings, (td.get_text() for td in row.find_all("td")))
        datasets.append(dataset)
    headings_simplified=[]
    for row in headings:
        headings_simplified.append(str(row).strip())
    simp_table=[headings_simplified]
    for row in datasets:
        next_line=[]
        for col in row:
            value=str(col[1]).strip()
            next_line.append(value)
        simp_table.append(next_line)
    return simp_table

def is_number(value):
    try:
        if not math.isnan(float(value)):
            return True
        else:
            return False
    except:
        return False

def sort_data_by_ID(ID,data,header_size=1,reverse=False):
    sort_column=ID
    sorting_data=[]
    headder=data[0:header_size]
    for row in data[header_size:]:
        next_line=[]
        for col in row:
            if is_number(col):
                next_line.append(float(col))
            else:
                next_line.append(col)
        if next_line != []:
            sorting_data.append(next_line)
    return_data_float=sorted(sorting_data,key=itemgetter(sort_column),
                             reverse=True)
    return_data_string=[]
    for row in return_data_float:
        next_line=[]
        for col in row:
            if str(col)[::-1][0:2][::-1]=='.0':
                next_line.append(str(col).split('.')[0])
            else:
                next_line.append(str(col))
        return_data_string.append(next_line)
    return_data_string_processed=[]
    hold_blanks=[]
    for row in return_data_string:
        if row[sort_column] == '':
            hold_blanks.append(row)
        else:
            return_data_string_processed.append(row)
    if reverse:
        return_data_string_processed=(return_data_string_processed[::-1]+
                                      hold_blanks)
    else:
        return_data_string_processed=return_data_string_processed+hold_blanks
    return_data_string_processed=headder+return_data_string_processed
    return return_data_string_processed

################################################################################
#                          importing mission speed data                        #
################################################################################
import sys
mission_timeing_dic={}
mission_dic={}
if os.path.isfile(path_to_csv_file_with_mission_speeds):
    missions_timeing_table=the_opener(path_to_csv_file_with_mission_speeds)
else:
    missions_timeing_table=[['Simple Mission Name','Rotation','Time',
                            'Drops Per Time']]
for row in missions_timeing_table[1:]:
    simple_mission_name=row[0]
    rotation=row[1]
    time=row[2]
    drops_per_time=row[3]
    mission_timeing_dic[simple_mission_name]=[rotation,time,drops_per_time]
    if simple_mission_name not in mission_dic:
        mission_dic[simple_mission_name]=mission(simple_mission_name)
    mission_dic[simple_mission_name].add_rotation_timeing(rotation, time,
                                                          drops_per_time)

################################################################################
#                           importing refinement data                          #
################################################################################
relic_rarity_drop_rates=the_opener(
                    path_to_csv_file_with_relic_item_drop_rates_based_on_rarity)
relic_refinement_cost_table=the_opener(
                                   path_to_csv_file_with_relic_refinement_costs)

refinement_dic={}
refinement_order=[]
for row in relic_rarity_drop_rates[1:]:
    refinement=row[0]
    assert refinement not in refinement_order
    refinement_order.append(refinement)
    refinement_dic[refinement]={}
    for col_ID in range(1,len(row)):
        rarity=relic_rarity_drop_rates[0][col_ID]
        refinement_dic[refinement][rarity]=float(row[col_ID])
for row in relic_refinement_cost_table[1:]:
    refinement_dic[row[0]]['cost']=int(row[1])


################################################################################
#                      building item <-> relic relationships                   #
################################################################################
URL_void_table='http://warframe.wikia.com/wiki/Void_Relic/ByRewards/SimpleTable'
table_class_void_table="article-table"
pre_procesed_item_relic_table=get_HTML_table(URL_void_table,
                                             table_class_void_table,
                                             table_count=0)

item_dic={}
relic_dic={}
for row in pre_procesed_item_relic_table[1:]:
    simple_item_name=row[0]+' '+row[1]
    simple_relic_name=row[2]+' '+row[3]
    if simple_item_name not in item_dic:
        item_dic[simple_item_name]=item(simple_item_name)
    if simple_relic_name not in relic_dic:
        relic_dic[simple_relic_name]=relic(simple_relic_name)
    item_dic[simple_item_name].add_relic(relic_dic[simple_relic_name],row[4])
    if row[5].lower()=='yes':
        relic_dic[simple_relic_name].make_vaulted()
    else:
        relic_dic[simple_relic_name].make_unvaulted()

################################################################################
#                   building relic <-> mission relationships                   #
################################################################################
URL_void_relic_drops=(
'http://warframe.wikia.com/wiki/Void_Relic/DropLocationsByRelic')
table_class="sortable"
html=urllib2.urlopen(URL_void_relic_drops).read()
soup = BeautifulSoup(html, 'lxml')
table_class="article-table"
tables = soup.find_all("table", attrs={"class":table_class})                    #At this point, I have grabbed the relic tables based on type (Lith, meso, neo, axi, exe). Theste tables will be parsed in the following for loops
relic_drop_dic={}
for table in tables:                                                           #Itterate over the relic type tables
    for relic_itter in table.find_all('tr',recursive=False)[1:]:               #itterate over the spicific relics in the table
        relic_name=str(relic_itter.find('td').get_text().split('\n')[0]).strip()
        if relic_name != '':
            assert relic_name in relic_dic
            assert len(relic_itter.find_all('td',recursive=False))==2
            assert len(relic_itter.find_all('td',recursive=False)[1].find_all(
                                                    'table', recursive=False))==1
            relic_table=relic_itter.find_all('td',recursive=False)[1].find_all(
                                                        'table', recursive=False)[0]
            table_head=[str(th.get_text()).strip() for th in 
                                            relic_table.find("tr").find_all("th")]
            table_body=relic_table.find_all('tr')[1:]
            drop_options=[table_head]
            for row in table_body:
                Type=str(row.find_all('td')[0].get_text()).strip()
                Category=str(row.find_all('td')[1].get_text()).strip()
                Rotation=str(row.find_all('td')[2].get_text()).strip()
                Chance=float(str(row.find_all('td')[
                                            3].get_text()).strip()[0:-1])/float(100)
                next_line=[Type,Category,Rotation,Chance]
                drop_options.append(next_line)
                
                simple_mission_name=Type+', '+Category
                if simple_mission_name not in mission_dic:
                    mission_dic[simple_mission_name]=mission(simple_mission_name)
                mission_dic[simple_mission_name].add_mission_type(Type)
                mission_dic[simple_mission_name].add_mission_tier(Category)
                mission_dic[simple_mission_name].add_drop_rotation_prob(
                                                            relic_dic[relic_name],
                                                            Rotation,
                                                            Chance)
            relic_drop_dic[relic_name]=drop_options
################################################################################
#                          definining probibility functions                    #
################################################################################
from scipy.stats import binom
def calc_number_of_rounds_expected(prob, events):                               #This function will calculate the expected number of rounds you will need to obtain [events] worth of sucessful events
    return round(float(events)/float(prob)+0.5,0)
def calc_number_of_rounds_with_confidence(prob, events, confidence):            #This function will calculate the expected number of rounds you will need to obtain [events] worth of sucessful events with [confidence]% confidence
    prb_of_getting_drops=0
    rounds=0
    while prb_of_getting_drops < confidence:
        prb_of_getting_drops=1-binom.cdf(events,rounds,prob)
        rounds+=1
    return rounds, prb_of_getting_drops
def get_confidence_from_probs_and_rounds(prob, events, rounds):
    return 1-binom.cdf(events,rounds,prob)

################################################################################
#                                  main function                               #
################################################################################
def get_path_table(item_name, item_count_needed=1):
    working_item=item_dic[item_name]
    report_header=['Item Name',
                   'Total Time (min)',
                   'Relic Refinement',
                   'Void Traces Needed',
                   'Void Trace Missions Run',
                   'Void Trace time spent',
                   'Relics farmed',
                   'Number of Relics needed',
                   'Item drop from relic base prob',
                   'Item drop from relic effective prob',
                   'Item drop from relics confidence',
                   'Time spent cracking relics','Mission run',
                   'number of missions run',
                   'relic drop from mission prob',
                   'Relic drop from mission confidence',
                   'mission rotation needed',
                   'Time spent farming relics']
    report=[report_header]
    if working_item.vaulted():
        return_data=[item_name]
        for col in report_header[1:]:
            return_data.append('vaulted')
        return [report_header,return_data]
    for relic_line in working_item.relic_rarities:
        working_relic=relic_line[0]
        relic_name=working_relic.name
        rarity=relic_line[-1]
        for refinement in refinement_order:
            prob_item_from_relic=refinement_dic[refinement][rarity]
            number_of_void_traces_needed_per_relic=refinement_dic[
                                                             refinement]['cost']
            if assume_full_squad_for_relic_missions:
                effective_prob_item_from_relic=1-(1-prob_item_from_relic)**4
            else:
                effective_prob_item_from_relic=prob_item_from_relic
            if not isinstance(minimum_prob_required_item_drop_from_relic, 
                              basestring):
                relic_count_needed,confidence_item=(
                    calc_number_of_rounds_with_confidence(
                        effective_prob_item_from_relic,
                        item_count_needed,
                        minimum_prob_required_item_drop_from_relic))
            else:
                relic_count_needed=calc_number_of_rounds_expected(
                    effective_prob_item_from_relic,
                    item_count_needed)
                confidence_item=get_confidence_from_probs_and_rounds(
                    effective_prob_item_from_relic,
                    item_count_needed,
                    relic_count_needed)
            total_void_traces_needed=(
                    relic_count_needed*
                    number_of_void_traces_needed_per_relic)
            void_trace_missions_run=int(
                round(
                    float(total_void_traces_needed)/
                    float(void_traces_per_round)+0.5,0))
            void_trace_time_spent=void_trace_missions_run*time_per_trace_run
            time_spent_cracking_relics=(relic_count_needed*
                                        time_per_trace_run)
            if len(working_relic.missions)>0:
                for mission_line in working_relic.missions:
                    working_mission=mission_line[0]
                    working_mission_name=working_mission.name
                    rotation=mission_line[1]
                    prob_relic_from_rotation=mission_line[-1]
                    if not isinstance(
                        minimum_prob_required_relic_drop_from_missions, 
                        basestring):
                        #seeing that this var is a string, we continue:
                        mission_count_needed,confidence_relics=(
                        calc_number_of_rounds_with_confidence(
                            prob_relic_from_rotation,
                            relic_count_needed,
                            minimum_prob_required_relic_drop_from_missions))
                    else:
                        mission_count_needed=calc_number_of_rounds_expected(
                            prob_relic_from_rotation,
                            relic_count_needed)
                        confidence_relics=get_confidence_from_probs_and_rounds(
                            prob_relic_from_rotation,
                            relic_count_needed,
                            mission_count_needed)
                    time_spent_per_rotation_table=(
                        working_mission.get_times(rotation))
                    try:
                        time_spent_per_rotation=float(
                                time_spent_per_rotation_table[1][1])
                    except:
                        print('Looks like you have not filled out your Mission '
                              'speeds.csv tabel. Pleas fill this out so we can '
                              'calculate estimated farm times')
                        sys.exit()
                    time_spent_farming_relics=(
                        time_spent_per_rotation*
                        mission_count_needed)
                    total_time=(
                        void_trace_time_spent+
                        time_spent_cracking_relics+
                        time_spent_farming_relics)
                    next_line=[item_name,
                               total_time,
                               refinement,
                               total_void_traces_needed,
                               void_trace_missions_run,
                               void_trace_time_spent,
                               relic_name,
                               relic_count_needed,
                               prob_item_from_relic,
                               effective_prob_item_from_relic,
                               confidence_item,
                               time_spent_cracking_relics,
                               working_mission_name,
                               mission_count_needed,
                               prob_relic_from_rotation,
                               confidence_relics,
                               rotation,
                               time_spent_farming_relics]
                    report.append(next_line)
            else:
                next_line=[item_name,
                           'No relic farm location found, assumed vaulted',
                           refinement,
                           total_void_traces_needed,
                           void_trace_missions_run,
                           void_trace_time_spent,
                           relic_name,
                           relic_count_needed,
                           prob_item_from_relic,
                           effective_prob_item_from_relic,
                           confidence_item,
                           time_spent_cracking_relics,
                           'No relic farm location found, assumed vaulted',
                           'No relic farm location found, assumed vaulted',
                           'No relic farm location found, assumed vaulted',
                           'No relic farm location found, assumed vaulted',
                           'No relic farm location found, assumed vaulted',
                           'No relic farm location found, assumed vaulted']
                report.append(next_line)
    return sort_data_by_ID(1,report,reverse=True)

################################################################################
#                      get plat prices from nexus-stats                        #
################################################################################
import json
import requests

item_name='Loki Prime Systems Blueprint'
nexus_stats_URL=nexux_stats_URL

response =requests.get(nexus_stats_URL)
json_data=json.loads(response.text)
prices_dictionary={}
for json_object in json_data:
    overall_name=json_object['name']
    components_list=json_object['components']
    for compoment in components_list:
        component_name=' '+compoment['name']
        if str(component_name).lower()==' set':
            component_name=''
        object_name=overall_name+component_name
        if 'selling' in compoment:
            selling_price=compoment['selling']['avg']
            buying_price=compoment['buying']['avg']
            combined_price=compoment['combined']['avg']
            prices_dictionary[object_name]={}
            prices_dictionary[object_name]['buying']=selling_price
            prices_dictionary[object_name]['selling']=buying_price
            prices_dictionary[object_name]['combined']=combined_price

def get_price(junk_item_name,what_plat_price_to_use):
    try:
        return prices_dictionary[junk_item_name][what_plat_price_to_use]
    except:
        pass
    try:
        processed_item_name=junk_item_name.split(' Blueprint')[0]
        return prices_dictionary[processed_item_name][what_plat_price_to_use]
    except:
        pass
    try:
        processed_item_name=junk_item_name.split(' Blueprint')[0]+' Set'
        return prices_dictionary[processed_item_name][what_plat_price_to_use]
    except:
        return 'can not find price on Nexus stats'
    
################################################################################
#                                 simplify options                             #
################################################################################
def simple_report(item_name,
                  included_things=['Item Name',
                                   'Total Time (min)',
                                   'Relic Refinement',
                                   'Void Traces Needed',
                                   'Relics farmed',
                                   'Number of Relics needed',
                                   'Item drop from relics confidence',
                                   'Mission run',
                                   'number of missions run',
                                   'Relic drop from mission confidence',
                                   'mission rotation needed']):
    full_report=get_path_table(item_name)
    cols_used=[]
    for col_ID in range(0,len(full_report[0])):
        if full_report[0][col_ID] in included_things:
            cols_used.append(col_ID)
    return_headder=['plat per hour','plat price ('+what_plat_price_to_use+')']
    top_hit=full_report[1]
    price=get_price(item_name,what_plat_price_to_use)
    total_time=top_hit[1]
    if is_number(total_time) and is_number(price):
        plat_per_hour=price/float(total_time)*60
    else:
        plat_per_hour=''
    return_data=[plat_per_hour,price]
    for col_ID in cols_used:
        return_headder.append(full_report[0][col_ID])
        return_data.append(top_hit[col_ID])
    return return_data, return_headder

################################################################################
#                                  loop over a set                             #
################################################################################
def make_set_report(list_of_item_names):
    return_report=[]
    for item_name in list_of_item_names:
        print(item_name)
        simple_data,simple_header=simple_report(item_name)
        if return_report == []:
            return_report.append(simple_header)
        return_report.append(simple_data)
    return sort_data_by_ID(0,return_report)

################################################################################
#                                     test cases                               #
################################################################################
#item_name='Loki Prime Systems Blueprint'
#return_table=get_path_table(item_name)
#the_saver('report.csv',return_table)

#simple_data,simple_header=simple_report(item_name)
#simple_report_table=[simple_header,simple_data]
#the_saver('simple_report.csv',simple_report_table)

#list_of_item_names=['Loki Prime Blueprint',
#                   'Loki Prime Neuroptics Blueprint',
#                   'Loki Prime Chassis Blueprint',
#                   'Loki Prime Systems Blueprint']
#set_report=make_set_report(list_of_item_names)
#the_saver('set_report.csv',set_report)
################################################################################
#                                   full report                                #
################################################################################
if make_full_report:
    full_list_of_item_names=item_dic.keys()
    full_set_report=make_set_report(full_list_of_item_names)
    the_saver('full_report.csv',full_set_report)
################################################################################
#                                  item report                                 #
################################################################################
if make_item_report:
    return_table=get_path_table(item_to_report)
    the_saver('item_report.csv',return_table)
    
################################################################################
#                                 items report                                 #
################################################################################
if make_items_report:
    list_of_items_name_file=the_opener(items_list_path)
    list_of_items_name=[]
    for row in list_of_items_name_file[1:]:
        item_name=row[0]
        if item_name[-10:].lower() != ' prime set':
            list_of_items_name.append(item_name)
        else:
            warframe_name=item_name[0:-10]
            list_of_items_name.append(warframe_name+
                                     ' Prime Blueprint')
            list_of_items_name.append(warframe_name+
                                     ' Prime Neuroptics Blueprint')
            list_of_items_name.append(warframe_name+
                                     ' Prime Chassis Blueprint')
            list_of_items_name.append(warframe_name+
                                     ' Prime Systems Blueprint')
    list_set=make_set_report(list_of_items_name)
    the_saver('items_report.csv',list_set)
