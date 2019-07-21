# anim2cfg
Animation to model.cfg

Blender 2.80 Addon for exporting the location/rotation of an (animated/constrained) object to a format usable in Arma 3 model.cfg files.

## Features ##
* export of the (matrix_world) location/rotation of the active object
* the location/rotation of the object may be animated/constrained
* export relative to a parent object is possible

## Installation ##

Blender:
* 'Edit' -> 'Preferences'
* select the 'Add-ons' tab
* 'Install...'
* navigate to the 'anim2cfg.py' file and select it
* install it by pressing 'Install Add-on from File...'
* enable the addon by setting the checkmark in front of it

## Known Issues ##
* the export of n frames resulting in only n-1 animation pairs is not a bug but by design

please report any other issue at https://github.com/4d4a5852/anim2cfg/issues

## Usage ##
Blender:
* select the (single) object to be exported
* 'File' -> 'Export' -> 'Arma 3 model.cfg (.cfg/.hpp)'
* set the export options
    * 'Parent Object': Animations will be exported relative to this object. When not set the origin will be used.
    * 'Start Frame': Starting frame to export.
    * 'End Frame': End frame to export.
    * 'Selection Name': Selection name to be used in the model.cfg. Defaults to the name of the object.
    * 'Source Name': Source name to be used in the model.cfg.
    * 'minValue': minValue to be used in the model.cfg for the first animation.
    * 'maxValue': maxValue to be used in the model.cfg for the last animation.
    * 'Precision': Number of decimal places.
* navigate the directory tree and set/select the file name (existing files will be OVERWRITTEN)
* 'Export model.cfg'

In a text editor of your choice:
* prepare a basic model.cfg with all the necessary skeletonBones
* #include the exported file(s) within the Animations class of your model.cfg
