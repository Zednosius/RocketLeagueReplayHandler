The Rocket League Replay Handler (or RLRH for short) is an application for the purpose of making it easier to keep track of you rocket league replay.
This project is in an functional alpha state. It might not be the prettiest but it works!

**Before running check out Usage further down**

# Features #
### Tracking replays which gives you the ability to ###

* Give them a custom name.
* View information such as players participating, goals made etc.
* Add tags to them, for example marking when a cool save happened.
* Add them to groups.
* Add notes to them.
* Staging, no more scrolling through dozens of replays!

### View information ###

Simply select a replay in one of the lists to view information about it, such as which players were in it, scores, goals, your tags and the groups it belongs to.

### Filtering ###

Filter amongst your replays on various conditions such as a replay having a certain player, played in a certain map or belonging to one of your created groups.

### Staging ###

Having a long list of replays ingame is not very helpful when you are looking for a specific one.
The RLRH adds "Staging" which is simply means that you can select and stage your replays and only those you have staged will show up ingame!
Filtering comes in handy in narrowing down your options and then you can inspect the remaining ones and stage the ones you want to look at ingame.

### Parsing ###

Thanks to [Daniel Samuels](https://github.com/danielsamuels/rocket-league-replay-parser) and his parser, a lot of basic information about your new replays will be automatically added.
Keep in mind that due to the replays format not all information might be added, you can however manually add this if you feel it neccessary.

### Planned features ###

An export and import system to enable sharing of replays together with your data about them.


# Important #
**Make sure to backup your replays before running. It is unlikely that something would permanently delete them and the RLRH does back them up on its own, but there might be some odd combination of permissions that will delete them without any form of backup. Remember, better safe than sorry!**

**The RLRH will shuffle around your replays in the rocket league replay folder, this makes steam cloud very confused when it tries to start rocket league and it finds a mismatch between the cloud and your local folder and subsequently redownloads every moved replay. To avoid this make sure to start rocket league before starting the RLRH. Having the replays redownloaded won't disturb the RLRHs operation, it is simply annoying having to wait for the download.**

If you want to reset your replay folder to its original state open a terminal window in the RLRH folder (Hold Shift and right click somewhere in the folder then select open command prompt) then run
>RocketLeagueReplayHandler.exe reset

Or if you prefer the manual way you can go to your replay folder (%user%\Documents\My Games\Rocket League\TAGame\Demos) and copy everything in the backup folder to the Demos folder and then delete the folders.


# Installation #

Simply download the zip under releases and extract it to a folder of your choice. The run the RocketLeagueReplayHandler.exe inside it and it should hopefully work (I have not been able to test it on very many computers). The first startup may be a bit slow since it has a couple of things to do first time around.

You could also clone this repository and run the `RocketLeagueReplayhandler.py` if you prefer that. Make sure that you have installed the parser from [Daniel Samuels](https://github.com/danielsamuels/rocket-league-replay-parser).

# Usage #

## Add Tab ##
The first time you open the RLRH you will land in the **add** tab. This is where all new replays and the ones you haven't tracked yet end up, together they are referred to as "untracked" replays. The replays are given names based on the date they were created and are sorted from newest to oldest.  
If you've saved a new replay whilst the RLRH was running you can click the **rescan button** underneath the list to poll the replay directory for new replays.

To view a replay simply select it in the list. The parser will do its best to display information about it to you.
If you notice any missing information in a row you can click it to edit it, or if you feel that information is not neccessary you can simply leave it.  
If an entire player is missing you can add a row by clicking the **add row button** underneath and then click the row to add information.
Keep in mind that if you switch to another replay before clicking track *your changes will not be saved*.

When you are satisfied with the information display click the **track button** at the bottom to add it to the database.

## Browse Tab ##
When a replay has been tracked it will end up in the list of the **browse** tab. 
Clicking it will display information about it in the middle window.

### Add tag ###
Add a tag to your selected replay by pressing the *add tag* button and writing into the dialog that pops up.

### Add to group ###
Add the replay to a group by pressing the *add group" button and then either selecting an existing group in the dropdown or by writing directly into the field.


### Filtering ###
Press the filter button underneath the to display the filter popup. Enter that which you want to filter on then press apply. To go back to the list of all replays simply click apply with all filters left empty. Keep in mind that it currently searches for exact matches, eg. "Group" and "group" are seen as different, so if you do not find any results make sure to double check that there are no misspellings or similar.

### Staging ###
To stage a replay for viewing ingame simply select the replay you want and press the Enter key on your keyboard.

### Unstaging ###
To unstage a replay, select it in the staged list and press the Delete key on your keyboard. 
If you want to unstage all replays you can press the button underneath the list.

### Untracking ###
To untrack a replay, e.g. delete it from the database, select it in the list and press the Delete key on your keyboard and then select yes in the confirmation popup. This will throw it back to the list of untracked replays.

### Deleting ###
To fully delete a replay, select in the untracked replay list and press the delete. Selecting yes in the confirmation box will permanently delete your replay, including the backup of it.



# License #
See LICENSE