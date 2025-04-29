# This repo has been migrated to [Codeberg](https://codeberg.org/BBarker/CurveRigger)

CurveRigger
===========

A tool to rig curves in Maya, including a simple UI. Creates a rigged joint chain (and optionally binds in several ways), with a flexible rig that works for cables, snakes, spines, etc.

This tool was originally created to rig complex cables on robotic surgical tools, part of some promotional material for the DaVinci Xi Surgical System. The models had polygon cable geometry winding through a series of wheels and bumpers, and they were textured in a way that stretching wasn't desirable. Fortunately the modeler on the project was able to also provide a curve passing through the center of each cable.

I wasn't the primary rigger on the project, in fact several of the instruments had been rigged already sans cables. So the tool needed to:

* Be easily used by others
* Attach to existing rigs
* Be flexible enough to rig 30 odd instruments of different kinds
* Be clear enough that if issues came up and I wasn't available another TD could easily adjust the code.

To keep things simple the code contains one class, RigCurveTool, with its members handling UI and the actual rigging. Most class members are UI based, with all needed info fetched and stored from two dictionaries: widgets and defaults.

`widgets` stores the names of the created widgets, since these are very important to any Maya UI command.
`defaults` stores desired default values for the various options the tool has. It also stores them as optionVars in Maya so they are preserved between launches. This ended up being really nice.

The main rigging is all done in the method `rigFromCurve`, however the tool also has a `wireOnly` method used for when a curve was already rigged. This was added because some wire geo had to be uprezed when it was discovered that it couldn't handle being deformed. Since these assets had already been rigged by hand we needed a solution to manually update them without the luxury of rebuilding from script. `wireOnly` made it easy to simply delete the old geo, bring in the new, and click one button. The code is overcommented so that other TDs could quickly see what some of the more esoteric NURBS rigging nodes are doing. 

The main guts of the rig is a NURBS strip, from which a live curve is extracted. Various nodes measure the length of the curve and allow length preservation or stretching as the user needs. The NURBS strip is skin weighted to an arbitrary number of controls. An arbitrary number of joints is generated and attached to the surface in a long chain. The cable geometry is then bound to these joints. This allowed maximum flexibility as I could paint weights not just for the chain itself but for the controls as well, although it turned out that the default weights worked 90% of the time.

The remaining methods, `attachObjToSurf`, `makeCubeCtrl`, and `hideChannels` are extremely generic rigging functions, but since this show had no central tools libraries it was necessary to add them to the tool.
