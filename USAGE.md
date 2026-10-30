# Flyerize_gui usage

The controls, one by one.  For installing and starting Flyerize_gui, the quick start and the save buttons, see the [README](README.md).

## The corner panel

Select a corner and its panel opens over the photo, titled with the corner's name, such as Top left corner.  The picture in it is the photo enlarged around that corner, with the corner at the crosshair.  Click anywhere in it to put the corner there.  Under the picture:

- **X and Y** are the corner's position in pixels.  Type a number, or use the little arrows.
- **Zoom** sets the enlargement, and **Expand** opens a large version of the same panel that takes most of the window.
- The other three corners are listed with their positions, in the order of the keys 1 to 4.  Click one to switch to that corner, the same as pressing its key.
- The **pad of eight arrows** nudges the corner a pixel at a time, the diagonals included.  Hold Shift for 10 and Ctrl for 100, the same as the keys.  The pad's buttons change color while you hold either key, and the step shows under the pad.  Hold a button down to keep going.
- The ✕ at the top right closes the panel, and so does Esc.

**Corner moves or sides move.**  The button in the middle of the pad, and the L key, switch between two ways to move a corner:

- **Corner moves** (red dots, the default): only the corner you move changes.
- **Sides move** (blue squares): the corner takes the two corners next to it along, the way you resize a rectangle by dragging one corner.  Move the top left corner down and to the right, and the top right corner follows the downward part, the bottom left corner follows the sideways part, and the bottom right corner stays where it is.  It stays a red dot, and the others are blue squares.

It applies to every way of moving a corner: dragging it, clicking in the panel, the X and Y boxes, the pad, and the arrow keys and W A S D.  Press L even with no corner selected, and you will see all four dots turn into squares.  The mode stays until you press L again, also from one photo to the next.  Settings chooses which way Flyerize_gui starts: rectangles all day, or freeform shapes and oval logos.

## Undo

Ctrl+Z undoes your edits to the photo on screen, one step at a time, with no limit.  A step is one drag, or one run of keypresses on the same corner (a pause of a few seconds, picking another corner or clicking away starts a new one), or one press of Zero, 5%, Reset, an applied gesture, a bend straightened, or a recent crop.  Reset also brings back the rotation and mirror it cleared.  The history starts over when you leave the photo or exit.  It covers the corners and sides, not saves and deletes.  If a gesture is waiting for Apply or Cancel, Ctrl+Z cancels it first.


## Moving through a folder

- **Back** and **Skip to Next** step through the list.  Files you made with Save New join the list right after their photo, so Back can take you to them, while Skip to Next and Auto go straight to the next original.  Back from the first photo wraps around to the last, but finishing a long list does not make you start over.
- **Move ±nnn** jumps ahead by a number of photos.  A negative number goes back.
- **Auto** moves to the next photo after each save.  While it is on, the save buttons show an arrow and turn pale green, and the navigation buttons turn gray (they still work).
- The **thumbnail row** at the bottom shows the photos around the current one, with the current photo framed in cyan and a green bar under each result made by Save New in this session.  Click a thumbnail to go to that photo.  With only one original photo open there is no row at all.  Settings can turn the row off and set its height, and the row is the first thing to give way when the window is short.
- The **Recent crops** list on the right remembers corner positions you have used.  Click one to apply those corners to the current photo, which is handy for a series shot from the same spot.
- Leaving a photo with unsaved changes (including a file name you typed but never used) asks first.  Settings has a checkbox to switch that question off.

## Cheat sheet

### Mouse

- Click a corner to select it, and drag to move it.  With sides moving, the neighboring corners move with it.
- Drag a purple dot to bend a side.  Right-click a purple dot to straighten that side.
- Drag a yellow side line to move the whole side.
- Wheel zooms about the pointer.  When zoomed in, drag empty space to pan.
- With the whole photo in view, drag across empty space to draw a start gesture: a closed rectangle, a Z, or a slash from corner to corner.

### Keyboard

- 1, 2, 3, 4 select the corner at top left, top right, bottom left, bottom right.
- Arrow keys or W A S D nudge the selected corner 1 pixel.  Hold Shift for 10 and Ctrl for 100.
- Plus and minus (keypad or main row) move all four sides out or in at once, with the same steps.
- 0 puts the corners at the photo's border. 5 puts them 5 percent in.  Ctrl-R finds the corners again.  The number pad's digits work like the top row's.
- L switches between corner moves and sides move.
- Ctrl+Z undoes the last edit to the corners and sides.
- Alt+S is Save New, Alt+A is Replace, Alt+D is Overwrite!, Alt+R is Rename, and the Delete key does what Delete does.
- Alt+B (or Ctrl+B) is Back, Alt+N (or Ctrl+N) is Skip to Next, and Alt+M is Move ±nnn.  Ctrl+Shift+Alt with B or N jumps 100 photos back or ahead.
- Alt+V shows or hides the preview.
- Ctrl with W A S D or the arrows is the times 100 step, so those letters are not used with Ctrl.
- G cycles the grid: off, then 1, 2, 4 or 9 lines each way (a crosshair, thirds, fifths, tenths).  Shift+G goes back.
- Esc closes the preview, settings or a corner panel, cancels a proposal, or deselects a corner.
- F1 shows the Help panel.

### The top row

- The **zoom box** and **Fit** control the main view.
- **Reset** finds the corners again and clears bends, rotation and mirror.  **Zero** and **5%** put the corners at the border or just inside it.
- **Grid** is the little box that shows how many grid lines are on.  Click it, or press G.
- **Crop to lines** cuts the result at your four sides.  Off keeps the whole photo, straightened.
- **Rotate CCW** turns the result in 90 degree steps.  **Mirror** flips it left to right.  These two change only the preview and the saved result, not the main view.
- **DBG** writes a picture of the original with your lines drawn on it, named with `~dbg`, next to the photo.  If the grid is on, its lines are drawn too.  Pressing it again replaces that file.  It does not save a result.

### Settings

The Settings button opens and closes the panel, and so do the ✕ at its top right and Esc.  Settings is where you choose where backups go, how new files are numbered (`name~1`, or a timestamp whose seconds count up), JPEG quality, whether the Recent crops list shows, whether Flyerize_gui asks before applying a gesture or leaving a photo with unsaved changes, whether it starts with sides moving, and whether the thumbnail row shows when two or more photos are open and how tall it is (32 pixels up to half the screen height).  A dropdown there also chooses what fills an empty corner when you pull a corner past the photo's edge: mirror the edge (the default), repeat the edge, or black.  There is also a checkbox for the occasional coffee reminder.  If Flyerize_gui has saved you time, a $5 coffee through [PayPal](https://www.paypal.com/qrcodes/managed/33ecc1cb-c786-4fba-ad4a-17242f92e108?utm_source=consapp_onscreen) is very welcome, and ticking that box, once you have sent one, turns the reminders off.
