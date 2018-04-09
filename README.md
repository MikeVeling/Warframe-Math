# Warframe math
This tool identifies the most efficient path for obtaining specific items in the game Warframe.

The game contains items called items called Void Relics, which are essentially a box that contains 1 of several possible in game items. To obtain void relics, players must play particular missions that have a random chance of providing a particular relic (defined on the game wiki here: http://warframe.wikia.com/wiki/Void_Relic/DropLocationsByRelic). Once the player obtains the relic, that relic has a particular chance to provide the player with the desired item (defined here: http://warframe.wikia.com/wiki/Void_Relic/ByRewards/SimpleTable). The player can then to choose to sell the item to other players for in-game currency. The prices of these items are constantly fluctuating so I pull live data from NexusStat for current going prices of the items.


## Public data accessed
If any of these public data repositories of data go down, the code will break

Nexus stat's platinum price API: https://api.nexus-stats.com/warframe/v1/items?data=prices <br>
Void relic table containing relics and where to get them: http://warframe.wikia.com/wiki/Void_Relic/DropLocationsByRelic<br>
Void relic table containing item drops from relics: http://warframe.wikia.com/wiki/Void_Relic/ByRewards/SimpleTable<br>

## Dependencies

This script is written in python 2.7 compatible code. The dependencies are beautifulsoup4, scipy and requests. To install simply run the following commands with your python 2.7 interpreter:

```
python2 -m pip install beautifulsoup4
python2 -m pip install --user numpy scipy matplotlib ipython jupyter pandas sympy nose
python2 -m pip install requests
```
## Inputs

This code also requires some user provided data. Example tables containing these data are included in the repository as well as a short explanation here

**items_list.csv**: this is a list of items you want to farm. <br>
**Mission speeds.csv**: This file contains a table with how long it takes you to run each mission in the game. The program uses this to figure out the shortest path to the item<br>
**Relic Drop table.csv**: This is a table building the relationship between the rarity of an item and the drop rates in a given relic.<br>
**Relic refinement table.csv**: This table contains the relationship between refinement and number of void traces the refinement needs.<br>

## Running the code
At this point, the code is simply run with no arguments from the command line. Within the code, there are user defined variables  that can be used to access its different functions independently. At this point, it runs all its functions together by default

```
python2 Find_easy_path.py
```

## Outputs
The code generates various outputs. These outputs are listed below

**Item_table.csv**: This table contains every possible way to get a specific item specified in the user editable variables<br>
**Items_table.csv**: This table contains the fastest possible way to get all items you listed in items_list.csv<br>
**full_report.csv**: This table contains a short report of the fastest way to get every item in the game. It also calculates how much platinum you are expected to earn based on the NexusStats API of current in game prices.<br>

Samples of all inputs and outputs are included in the repository
