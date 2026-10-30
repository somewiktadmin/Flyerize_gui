# Flyerize_gui v0.2.0 2026-10-29
Windows tool to fix the perspective and curl in photos of flyers and banners: set four corners, bend the sides, save a clean rectangle.

*Straighten the flyer.  Flatten the banner.  Keep the wall out of it.*

Somewhere in your photos there is a flyer pinned to a corkboard, a banner sagging along a fence, a sheet of paper taped a little crooked to a door.  You stood off to one side, the camera leaned, and the wind had its say about the corners.  Flyerize_gui takes that photo and hands back what you were really looking at: a flat, upright, readable rectangle.

It starts by guessing where the edges are.  You nudge four corners until they sit just right, bend any side that curves the way the paper hangs, glance at a preview, and save.  One photo at a time, or a whole folder of them, at whatever pace suits you.

## What you need

- Windows 10 (that is where it was built and tested).  It also runs in the Linux environment of an Intel Chromebook: install `python3-tk`, `python3-pil.imagetk`, `python3-numpy` and `python3-opencv` with apt, and start it with `python3 Flyerize_gui.py`.  Send To, the Windows registry and the Recycle Bin are Windows only, and the program quietly does without them elsewhere.
- Python 3 from python.org.  On the first installer screen, tick "Add python.exe to PATH".  The default options also include Tkinter, the window toolkit.
- Three packages: OpenCV, NumPy and Pillow, plus a fourth, pi-heif-decoder, only if you want to open iPhone HEIC photos

Install the packages once, from a command prompt:

    pip install opencv-python numpy pillow pi-heif-decoder

Prefer not to install Python at all?  Download `Flyerize_gui.exe` from the Releases page of this repository (the link is in the right-hand sidebar).  It runs on its own, and wherever this page says `python Flyerize_gui.py`, the .exe works the same way.  The .exe is not code signed, so Windows may show a "Windows protected your PC" screen the first time.  Click More info, then Run anyway.  Some antivirus programs are also suspicious of programs packaged this way.  The full source is in this repository, so you can read it or build the .exe yourself (see the end of this page).

## Starting it

Give it a photo, or a folder, or nothing at all:

    python Flyerize_gui.py "C:\Photos\flyer.jpg"
    python Flyerize_gui.py "C:\Photos\Fence Banners"
    python Flyerize_gui.py

With a photo, it opens that photo.  With a folder, it lines up every image in it.  With nothing, it asks you to choose a photo.  It reads JPG, PNG, BMP, GIF, TIFF and WebP, and it saves JPEG (or PNG and BMP when the original was one of those). iPhone HEIC photos are read too when pi-heif-decoder is installed (the .exe includes it), and the result is saved as a JPEG.

A gentle reminder: before you point it at a whole folder, make a backup copy of that folder, for example all of `C:\Photos`.  Single photos are well tested, the whole-folder mode much less so, and irreplaceable photos and screenshots deserve a backup of their own whatever any program promises.

If Flyerize_gui is already open and you start it again with more files, for example from the Send To menu, the new files join the open window's list.

### Adding Flyerize_gui to the Send To menu

Send To is the fastest way to use it: select photos (or a whole folder) in Explorer, right-click, and send them straight to Flyerize_gui.

1. Press Win+R, type `shell:sendto`, and press Enter.  A folder opens.
2. In Explorer, right-click `Flyerize_gui.bat` (or the packaged .exe) and choose Create shortcut.
3. Move that shortcut into the folder from step 1, and rename it Flyerize_gui.

From then on, right-click any photo or folder, choose Send to, then Flyerize_gui.

`Flyerize_gui.bat` starts the script with `pythonw`, so no black console window stays open.  It finds the script through its own folder, so it works wherever you put the Flyerize_gui folder.  Make a shortcut to the batch file, as in the steps above, and do not copy the batch file itself into the Send To folder, because a copy would look for the script in the wrong place.  One catch: `pythonw` hides error messages, so if Flyerize_gui ever fails to start without a word, open a command prompt in its folder and run `python Flyerize_gui.py` to see what went wrong.

## Quick start

1. **Open a photo.**  It fits the window with four red corner dots and yellow lines along the edges.  That is the program's first guess.
2. **Fix the corners.**  Click a corner and drag it.  The corner panel opens with a zoomed view so you can place it precisely (see the next section).  Or press 1, 2, 3 or 4 to pick a corner and nudge it with the arrow keys.
3. **Or start with a flourish.**  While the whole photo is in view, drag across empty space to draw a rectangle around the flyer, a Z, or a slash from corner to corner.  The program proposes corners, and you press Apply or Cancel.  Start the stroke away from the red dots and yellow lines, because pressing on one of them grabs it instead of drawing.  If the first guess sits right where you want to begin, press Zero first.
4. **Bend the sides.**  If the paper curves, drag the purple dot on that side.  Right-click a purple dot to make its side straight again.
5. **Look at the result.**  Press PREVIEW.  Press it again, or press Esc, to go back.  Press G to lay alignment grid lines over the picture.
6. **Save.**  Press Save New.  The straightened picture is written next to the original, and the original is left alone.
7. **Move on.**  Press Skip to Next (Alt+N), or turn on Auto and let each save carry you to the next photo.

Under the picture, the line with the place in the list also shows `Started: 1440x810`, the size of your photo, and `Saving: 360x270`, the size the result will have.  The result is never scaled, so the second number is simply the area your four corners enclose (with Crop to lines off, the whole straightened photo), turned if you rotate it.

The first time Flyerize_gui starts, a short Help panel appears.  Press F1 any time to see it again.

## The corner panel

Select a corner and its panel opens over the photo, titled with the corner's name, such as Top left corner.  The picture in it is the photo enlarged around that corner, with the corner at the crosshair.  Click anywhere in it to put the corner there.  Under the picture:

- **X and Y** are the corner's position in pixels.  Type a number, or use the little arrows.
- **Zoom** sets the enlargement, and **Expand** opens a large version of the same panel that takes most of the window.
- The other three corners are listed with their positions, in the order of the keys 1 to 4.  They are only a display.
- The **pad of eight arrows** nudges the corner a pixel at a time, the diagonals included.  Hold Shift for 10 and Ctrl for 100, the same as the keys.  The pad's buttons change color while you hold either key, and the step shows under the pad.  Hold a button down to keep going.
- The ✕ at the top right closes the panel, and so does Esc.

**Corner moves or sides move.**  The button in the middle of the pad, and the L key, switch between two ways to move a corner:

- **Corner moves** (red dots, the default): only the corner you move changes.
- **Sides move** (blue squares): the corner takes the two corners next to it along, the way you resize a rectangle by dragging one corner.  Move the top left corner down and to the right, and the top right corner follows the downward part, the bottom left corner follows the sideways part, and the bottom right corner stays where it is.  It stays a red dot, and the others are blue squares.

It applies to every way of moving a corner: dragging it, clicking in the panel, the X and Y boxes, the pad, and the arrow keys and W A S D.  Press L even with no corner selected, and you will see all four dots turn into squares.  The mode stays until you press L again, also from one photo to the next.  Settings chooses which way Flyerize_gui starts: rectangles all day, or freeform shapes and oval logos.

## Undo

Ctrl+Z undoes your edits to the photo on screen, one step at a time, with no limit.  A step is one drag, or one run of keypresses on the same corner (a pause of a few seconds, picking another corner or clicking away starts a new one), or one press of Zero, 5%, Reset, an applied gesture, a bend straightened, or a recent crop.  Reset also brings back the rotation and mirror it cleared.  The history starts over when you leave the photo or exit.  It covers the corners and sides, not saves and deletes.  If a gesture is waiting for Apply or Cancel, Ctrl+Z cancels it first.


## The save buttons

The box labeled New name always shows the name the next save will use, and the Source line above it shows which file is on screen.  Replace, Overwrite! and Delete always act on that file, and the box only names the result.  You can edit it before pressing any of these:

- **Save New** (Alt+S) writes the result as a new file and leaves the original alone.  If the name is taken, a number is added (`name~1`, `name~2`, and so on).
- **Replace** (Alt+A) backs up the photo on screen, then writes the result under the name in the box.  If that name belongs to a different file, the result gets a number, as Save New does.
- **Overwrite!** (Alt+D) does the same with no backup, and asks first.  It cannot be undone, and it saves space only when the crop is small (see the next section).
- **Rename** (Alt+R) renames the photo's file to the name in the box without rewriting the picture.  The file keeps its own extension.
- **Delete** (the Delete key) moves the photo aside as a backup and goes to the next one.  Nothing is asked, and nothing is destroyed.  Backups are normally dot-prefixed copies (.trashed_name.jpg) next to the photo, and Settings can send them to a folder or the Recycle Bin instead.

Every file Flyerize_gui writes is a separate file with its own name.  It rarely overwrites one without telling you.  The result keeps the original photo's color profile when it has one.

### About Overwrite!

Overwrite! is the one button that can lose something for good, so here is exactly what it does and does not do.

**What it does.**  It deletes the photo on screen and saves the result under the name in the box.  When the name is the photo's own, the result simply takes its place.  When the original is not a JPEG, the box starts with a `.jpg` name, so Overwrite! deletes the original and leaves the `.jpg`, and that includes a HEIC photo.  If the name belongs to a different file, the result gets a number and that file is left alone.  There is no backup and no undo.  Flyerize_gui asks first.  You can turn the question off, either with the checkbox in the dialog or in Settings.
 
**What it does not do: shrink a picture by itself.**  It is not a compressor.

- Flyerize_gui never shrinks or resamples a picture.  The result has about as many pixels as the area you selected, and it is saved at high JPEG quality (95 by default).  A crop that covers most of the photo can come out the same size as the original, or even bigger.
- Space is saved only when the crop is small.  Cut a 64 by 64 corner out of a huge picture and the file really is tiny, which can be enough to get a full phone unstuck.
- It cannot touch copies that are not in the folder.  Pictures already uploaded to a cloud account stay there, and a recently deleted folder usually keeps the old picture for a while.
- If you simply want smaller files, lower the JPEG quality in Settings, or use a program that resizes pictures.

When in doubt, use Save New, which keeps both files, or Replace, which keeps the original as a backup.

## Moving through a folder

- **Back** and **Skip to Next** step through the list.  Files you made with Save New join the list right after their photo, so Back can take you to them, while Skip to Next and Auto go straight to the next original.  Back from the first photo wraps around to the last, but finishing a long list does not make you start over.
- **Move ±nnn** jumps ahead by a number of photos.  A negative number goes back.
- **Auto** moves to the next photo after each save.  While it is on, the save buttons show an arrow and turn pale green, and the navigation buttons turn gray (they still work).
- The **thumbnail row** at the bottom shows the photos around the current one, with the current photo framed in cyan and a green bar under each result made by Save New in this session.  Click a thumbnail to go to that photo.  Settings can turn the row off and set its height, and the row is the first thing to give way when the window is short.
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

The Settings button opens and closes the panel, and so do the ✕ at its top right and Esc.  Settings is where you choose where backups go, how new files are numbered (`name~1`, or a timestamp whose seconds count up), JPEG quality, whether the Recent crops list shows, whether Flyerize_gui asks before applying a gesture or leaving a photo with unsaved changes, whether it starts with sides moving, and whether the thumbnail row shows and how tall it is (32 pixels up to half the screen height).  A dropdown there also chooses what fills an empty corner when you pull a corner past the photo's edge: mirror the edge (the default), repeat the edge, or black.  There is also a checkbox for the occasional coffee reminder.  If Flyerize_gui has saved you time, a $5 coffee through [PayPal](https://www.paypal.com/qrcodes/managed/33ecc1cb-c786-4fba-ad4a-17242f92e108?utm_source=consapp_onscreen) is very welcome, and ticking that box, once you have sent one, turns the reminders off.

### Where Flyerize_gui keeps its files

Settings, and a log of what Flyerize_gui has done (`Flyerize_gui.log`), live in `%APPDATA%\Flyerize_gui\`.  The log starts a fresh file at about 1 MB and keeps the previous one as `Flyerize_gui.log.old`.  If your Python came from the Microsoft Store, Windows quietly keeps these in a private copy of that folder, under `%LOCALAPPDATA%\Packages\` in a folder whose name starts with `PythonSoftwareFoundation`, so you will not find them in the usual place.

## Good to know

- Every control has a tooltip.  Hover for a moment.
- Curious why it behaves a certain way?  The reasoning behind the design is in DESIGN.md.
- The Exit button sits off on its own at the right, and the window's close button works the same way.
- This is early software.  It has been used on hundreds of photos by one person.  If something confuses you, breaks, or just feels wrong, please tell me.  That is exactly the feedback I am hoping for.

## Building the .exe yourself

Run `Build_Flyerize_gui.bat` from the folder that contains `Flyerize_gui.py`.  It installs the packages it needs, uses PyInstaller to build `dist\Flyerize_gui.exe`, and adds a Send To shortcut for it.  The .exe is a snapshot of the script at the moment you build it, so build again after you change the script.

## License

Flyerize_gui is free software, released under the GNU General Public License, version 3 or, at your option, any later version (GPL-3.0-or-later).  You may use it, study it, share it and change it.  If you pass it on, changed or not, the same freedoms must come along with it.  The full text is in the LICENSE file that comes with the program.

It comes with no warranty of any kind.  That includes Overwrite!, so keep a copy of any photo you cannot replace.
