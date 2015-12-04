# Rocket League Replay Handler (RLRH) #
Tired of [scrolling forever](https://gfycat.com/RadiantShortAnole)?  
Tired of not finding that particular replay where you did that amazing thing?

The Rocket League Replay Handler is the solution to your problems!  
**Features**  
[Name your replays, Put tags on them, Group them together!](http://i.imgur.com/DPlMENU.png)  
[Filter amongst your replays!](http://i.imgur.com/Y0QahFD.png)  
[Select which replays should be viewable ingame with staging!](http://i.imgur.com/6IjIts7.png)


**How do i install it?**  
First make a backup of your replays, just to be extra safe. You find them under `<User>\Documents\My Games\Rocket League\TAGame\Demos`.  
[Download the zip](https://github.com/Zednosius/RocketLeagueReplayHandler/releases/download/v1.1.0-alpha/RLRH_v1.1.0-alpha.zip), extract it to a folder of your choice eg. `<user>\RLRH`.  
Start Rocket League to [avoid confusing steam cloud](https://github.com/Zednosius/RocketLeagueReplayHandler#important) or you can disable steam cloud for rocket league if you prefer a more permanent solution.  
Run the RocketLeagueReplayhandler executable inside the folder you extracted to and you should be up and running!

If it is unclear how to perform an action you can read a short description of how to do it [in this section.](https://github.com/Zednosius/RocketLeagueReplayHandler#Usage)


### About ###
The Rocket League Replay Handler (or RLRH for short) is an application for the purpose of making it easier to keep track of you rocket league replays.
This project is in an functional alpha state. It might not be the prettiest but it works!  
The RLRH is developed by me, a compsci student and a big rocket league fan.

# Feature List #
### Tracking replays which gives you the ability to ###

* Give them a custom name.
* View information such as players participating, goals made etc.
* Add tags to them, for example marking when a cool save happened.
* Add them to groups.
* Add notes to them.
* Staging, no more scrolling through dozens of replays!

### New in version 1.1.0 ###
* Export and import replays! Exports end up in the same folder as the executable.
* Removed add-tab for streamlining the process.
* Threaded large parts which does away with unresponsive/laggy ui.

### New in Version 1.1.1 ###
* Added ctrl+a, select all, to all text fields.
* Navigate up/down amongst replays with k/j
* Ctrl+e to edit the replay visible.
* 't' and 'g' popups window for adding tag and group respectively for active replay.
* Delete groups from replays
* Delete tags from replays
* Can scan replay folder for new replays with 'Rescan' menu option.
* If replay folder is not in the default location you will be asked to provide the actual location.

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
Keep in mind that due to the replays format, not all information might be added. You can however manually add this if you feel it neccessary.

### Planned features ###
General improvements to UI.  
I'm willing to take suggestions!


# Important #
**Make sure to backup your replays before running. It is unlikely that something would permanently delete them and the RLRH does back them up on its own, but there might be some odd combination of permissions that will delete them without any form of backup.**  
**Remember, better safe than sorry!**

**Steam Cloud** 
**The RLRH will shuffle around your replays in the rocket league replay folder, this makes steam cloud very confused when it tries to start rocket league and it finds a mismatch between the cloud and your local folder and subsequently redownloads every moved replay. To avoid this make sure to start rocket league before starting the RLRH. Having the replays redownloaded won't disturb the RLRHs operation, it is simply annoying having to wait for the download.**    
**You could also disable steam cloud for rocket league to avoid this entirely.**

If you want to reset your replay folder to its original state open a terminal window in the RLRH folder (Hold Shift and right click somewhere in the folder then select open command prompt) then run
>RocketLeagueReplayHandler.exe reset

Or if you prefer the manual way you can go to your replay folder (%user%\Documents\My Games\Rocket League\TAGame\Demos) and copy everything in the backup folder to the Demos folder and then delete the folders.


# Installation #

Simply download the [zip under releases](https://github.com/Zednosius/RocketLeagueReplayHandler/releases) and extract it to a folder of your choice.  
Then run the RocketLeagueReplayHandler.exe inside it and it should hopefully work (I have not been able to test it on very many computers).  
The first startup may be a bit slow since it has a couple of things to do first time around.

You could also clone this repository and run the `RocketLeagueReplayhandler.py` if you prefer that. Make sure that you have installed the parser from [Daniel Samuels](https://github.com/danielsamuels/rocket-league-replay-parser).

# Usage #


## Replay list ##
Your replays will be seen to  list of the **browse** tab. 
Clicking it will display information about it in the middle window.

### Add tag ###
Add a tag to your selected replay by pressing the *add tag* button and writing into the dialog that pops up.

### Add to group ###
Add the replay to a group by pressing the *add group* button and then either selecting an existing group in the dropdown or by writing directly into the field.

### Filtering ###
Press the filter button underneath the to display the filter popup. Enter that which you want to filter on then press apply. To go back to the list of all replays simply click apply with all filters left empty. Keep in mind that it currently searches for exact matches, eg. "Group" and "group" are seen as different, so if you do not find any results make sure to double check that there are no misspellings or similar.

### Staging ###
To stage a replay for viewing ingame simply select the replay you want and press the Enter key on your keyboard.

### Deleting ###
To fully delete a replay, select in the replay list and press the delete. Selecting yes in the confirmation box will permanently delete your replay. The backup folder will not be touched however.

### Importing ###
To import a replay, click *Import* in the menu and select the zipfile with the filedialog.

### Exporting ###
To export a replay either select it in the list and then click *Export Selected* in the menu.
To export multiple replays click *Export Multiple* in the menu and select the ones you want to export. Note that it only shows replays in your list so it is possible to filter your replays before picking which to export.

# License #
See LICENSE