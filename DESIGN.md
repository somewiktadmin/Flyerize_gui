# Flyerize_gui design notes

These notes explain why Flyerize_gui behaves the way it does, so the less obvious choices make sense.  For how to use it, see the README and USAGE.md.

## Scope

- Flyerize_gui straightens one flyer, banner or sheet of paper in one photo, hanging on a wall, fence or door.  That is the job it is built for, and it does it well.
- It is not a media editor.  It does not remove backgrounds, retouch, resize or compress.  Feature requests that drift toward a full editing suite are out of scope.
- It is interactive first.  Folder mode exists for convenience, but the design assumes a person looking at each photo.
- Heavier automatic detection (edge refinement, corner voting) was tried early and set aside.  Lowering its thresholds only produced distorted results.  The first guess is deliberately simple, and the person fixes it.

## Principles

- **Non-destructive by default.**  The first save never touches the original.  Every save button except one keeps a way back.  The one other thing replaced silently is the throwaway `~dbg` picture.
- **Overwrite! is the only button that can lose something for good.**  It is named with an exclamation point on purpose, and the README explains it in detail.
- **No snapping and no automatic border measuring.**  Corners land exactly where you put them, in whole pixels.  Even a one-pixel snap feels wrong when you are trying to hit an edge, and measuring borders automatically would be slow.
- **No resampling for size.**  The result has about as many pixels as the area you selected, so Overwrite! is not a compressor and the docs never promise space savings.
- **Nothing is hidden.**  The default backups are ordinary files with a dot-prefixed name (.trashed_ before the file name), or files in a visible .originals folder.  The program sets no hidden attribute and makes no special system calls for them, so they sit beside the photo as obvious candidates for manual deletion.  Settings also offers the Recycle Bin, which has been tested on local drives and falls back to the .trashed_ method on drives that report no bin (that case is still untested).  The method is always the user's choice in Settings.  If the .originals folder cannot be created, the save stops with an error and does not switch methods on its own.

## Corners, sides and gestures

- Corners drag like every other handle.  Early testing showed people instinctively try to drag them, and click-only red corners next to draggable purple dots was inconsistent.
- X and Y stay visible and editable in a corner panel that remains up after a drag.  The docked panel and the large one are the same panel, with the same controls, differing only in the size of the picture.  The panel also lists the other three corners, and a click on one switches to it (the large panel can cover the other corners on the picture).  The rows show a thin border under the pointer, not a hand cursor, because a hand suggests touching a display-only screen, and has a pad of eight arrows so a corner can be nudged with the mouse as well as the keys.  Shift and Ctrl change the pad's step (10 and 100) and tint its buttons while held, because a tint alone is easy to miss, so the step is also written under the pad.
- **Corner moves or sides move.**  Moving only one corner is right for freeform artwork and oval logos.  Moving a corner together with its two neighbors, as when resizing a rectangle by a corner, is right for the many days that are all rectangles, and it was the preferred mode of the author's earlier Java tool (Scissor).  Both are essential, so both are one key away (L), and the difference is visible: red dots for corner moves, blue squares for sides move, with the opposite corner staying a red dot as the anchor.  The shape carries the meaning and the color only backs it up.  The same glyphs appear on the pad's center button and beside the other corners in the panel.
- Sides move splits a move into its sideways part and its up-and-down part.  The corner that shares a left or right side follows the sideways part, and the corner that shares a top or bottom side follows the other, so the opposite corner never moves.  The rule is the same for a drag, a click in the panel, the X and Y boxes, the pad and the keys, because a lock that only some controls obey would be a trap.  Shift is not used as a momentary override for it, since Shift already means a bigger step everywhere else.
- The mode belongs to the session, not to a panel, and it is visible all the time in the handles, so it cannot be forgotten without being noticed.  Settings sets which mode the program starts in, because some days are all rectangles and some are not.
- Each side bends with one purple dot, which slides along its line.  Right-click straightens that side.  One curve per side was judged enough, and two dots per side was rejected as overkill.
- Side drags lock to the perpendicular direction, because missing by a few pixels in the wrong direction leaves a sliver of border on one corner.  Shift unlocks the drag.  Sides move (above) is the same idea for corners: the freedom to swing one side alone invariably costs several more corner edits afterward.
- Start gestures are valid only while the whole photo is in view, never while zoomed in.  They are a closed rectangle, a Z, or a corner-to-corner slash, and they set straight sides and clear any bends.
- Two validation rules decide whether a stroke counts.  The stroke should be at least about 30 screen pixels across, which stops accidental clicks.  The shape it proposes should also cover at least about 1 percent of the photo's area.  Both are floors chosen for now and open to change if feedback says so.  The 1 percent floor is deliberate.  For a small flyer in a big photo, the intended workflow is to draw a larger box first, then zoom with the mouse wheel and drag the sides and corners into place.
- A gesture shows a ghost of the proposed corners with Apply and Cancel, rather than applying silently and offering undo afterward.  The Confirm setting turns these prompts off for people who want speed.

## Saving and naming

- **Save New** writes a new file and leaves the original alone.  **Replace** backs up first.  **Overwrite!** does not.  **Rename** renames the file without rewriting the picture and keeps its extension.  **Delete** moves the photo aside as a backup, with no question asked, because nothing is destroyed.
- The name box starts at the original's name and always shows the name just written.  The program never rewrites it after a save, so repeated saves can produce names like `name~1~1`.  That is accepted, since every save is a separate file and nothing is lost.
- The box only names the new result.  Replace, Overwrite! and Delete always act on the file on screen, which a Source line above the box names.  Replace backs it up first, and Overwrite! removes it.  A name that is the photo's own simply lets the result take its place.
- If the name belongs to a different file, Save New, Replace and Overwrite! add a number, so no other file is touched.  On a result's own entry the name is its own, so a second click rewrites the same file.
- Overwrite! on an original in another format, a HEIC photo included, removes that original and leaves the `.jpg`.  It is never grayed out, because when it is wanted it must really do it.
- Numbering: any `~nn` counts as one of the program's own numbers, and several are summed (`name~1~4~7~2` starts as `name~14`).  For timestamp-style names (YYYY-MM-DD_HH-MM-SS), the sum is added to the seconds instead, and only the seconds ever change.  A taken name gets a number up to `~99`, and backups go up to `~999`.
- Typing in the name box counts as an unsaved change when you leave a photo.
- A save writes the result to a temporary file first, so a failure such as a full disk or a read-only folder or share stops before anything is changed.  The system's message appears in a dialog and the program stays open.
- The Overwrite! question lives in a persistent Settings checkbox, not a once-per-session warning.  The dialog stays terse, because a crisis moment is the wrong place for a lecture.  The longer note sits at the top of Settings.

## Navigation and Auto

- Results made by Save New are inserted into the list right after their photo.  Back and Move can land on them.  Skip to Next and Auto go straight to the next original.  Back from the first photo wraps around to the last, and so does jumping back 100.  Going ahead never wraps; 	finishing a long list does not make you start over.
- Skip to Next is the most pressed button, since nearly every save is followed by it, so it sits close to the save buttons.
- Auto advances after each save.  While it is on, the four save buttons show an arrow on pale green, and the navigation buttons keep their normal look because they stay fully valid.  Auto is kept away from Delete and Overwrite!.
- Leaving a photo with unsaved changes asks first if the Confirm setting is on.  If it is off, the corners are quietly added to the Recents list instead.
- Recents are corners only, newest first, de-duplicated, up to 500.  One click applies them, which suits a series shot from the same spot.

## Keyboard

- Alt is the main modifier.  A, S and D are Replace (Amend), Save New and Overwrite! (Destructive).  B, N and M are Back, Skip to Next and Move.  R renames and V toggles the preview.  Ctrl+B and Ctrl+N are alternates, and Ctrl+Shift+Alt with B or N jumps 100.
- Ctrl is the times-100 step for the arrow keys, WASD and plus and minus, so Ctrl letter shortcuts are avoided.  Ctrl+R stays Reset.
- F2 is deliberately untouched, because it means rename in Explorer.  Ctrl+Z is undo (see Undo).  There is no redo, and none was wanted.
- L switches between corner moves and sides move.  The number pad's digits are treated like the top row's.
- F1 opens the Help panel, which also appears once on the first run.
- Shortcuts that would clash with typing are ignored while a text box has the keyboard.
- There are no extra safety bumpers on the shortcuts.  Over-protection was explicitly declined, repeatedly.

## First run, reminders and the log

- The Help panel shows once, on the first run, and F1 brings it back.  The "already shown" flag is kept in the settings file and in the Windows registry, and both are read back before the panel appears.  If either cannot be confirmed, the panel is skipped.  Showing something twice is worse than not showing it, so every doubt means fewer messages.
- A running count of saves, renames, deletes and DBG pictures is kept in the same two places, and the larger number wins.  A coffee reminder appears at fixed counts, once each, and never in the same session as the first-run help.  It is an honor system: ticking the box, in the reminder or in Settings, turns it off for good.
- `Flyerize_gui.log` records each save, backup, rename, delete and DBG picture with a readable timestamp and full paths, plus a START line for each run and a line when files are handed to a running window and when that window picks them up.  It starts a fresh file at about 1 MB and keeps one `.old` file.  If Windows redirects the settings folder (Microsoft Store Python), the script and the .exe may each keep their own log.

## Undo

- Ctrl+Z undoes corner and side edits for the photo on screen, with no limit.  The history is dropped when you go to another photo or exit.
- A step is one drag, or one run of keypresses on the same corner (the run ends after a pause of a few seconds, or when another corner is picked or you click away), or one Zero, 5%, Reset, gesture, recent crop or straightening of a bend.  Reset's step also restores rotation and mirror, which only Reset clears.  A step that changed nothing is skipped, so no keypress is wasted.
- It does not cover saves, renames or deletes.  Bringing back a deleted photo (Undelete) was judged more trouble than it is worth, since the Recycle Bin, the `.originals` folder and the `.trashed_` files already hold the originals.  It will be reconsidered if anyone asks.

## The thumbnail row

- A row under the status lines shows the photos around the current one as wide as the window allows, with the current photo framed and the results of Save New marked with a green bar.  Clicking a thumbnail goes to that photo.  Results from earlier sessions cannot be told apart, so they look like originals.
- Thumbnails are made on a worker thread, nearest the current photo first, with a few beyond each end made ahead of time.  JPEGs are decoded at a fraction of their size, which is what makes it quick.
- Screen height is scarce, so the row has a Settings checkbox and a height setting (32 pixels up to half the screen height).  Turning it off also stops the thumbnail work.  It is shown only when two or more original photos are open.  Results made by Save New do not count, so a single photo does not get a row after its first save.  It is the last widget in the window, so when the window is short it is the first to disappear.

## Settings panel

- Settings is a panel over the picture, not a window, so it has no title bar.  The Settings button toggles it, and a flat ✕ at the top right and Esc close it.  There is no Close button.
- If the panel is taller than the window it is anchored at the top, so the heading is never cut off.

## Output options

- Crop to lines cuts the result at your four sides.  Off keeps the whole photo, straightened.
- Rotate and Mirror change only the preview and the saved result.  The experimental BW/WB option was removed in v0.2.0.
- The result keeps the source photo's ICC color profile when it has one.  The colors are not converted, so the profile still describes them.
- The line that gives the place in the list also shows the photo's size (`Started`) and the size the result will have (`Saving`).  Both come from the same code that writes the file, so they cannot disagree.  The size is never entered or scaled, because it follows from the four corners.  Spinners for width and height, as the author's earlier tool had, were judged not worth having, while seeing the size was needed.  Bends are not counted in it, only the straight distances between corners.
- DBG writes one `~dbg` picture of the original with your lines drawn on it, including the grid when it is on, and the start stroke if no corner or side has moved since.  It is a throwaway.  Pressing it again replaces the same file with no backup, and it is not a save.
- Empty corner fill decides what covers a corner that lies outside the photo when you pull a corner past the edge.  The choices are mirror the edge (the default), repeat the edge, or black.  It matters in perhaps one photo in fifty to a hundred, and no default suits every image, so it is a dropdown in Settings, inconvenient enough that it stays a rare choice.  The magnifier and main view keep showing black or gray outside the photo on purpose, so the real edge stays visible.
- The grid is curved to follow the bends in the main view, and straight in the preview when Crop to lines is on.

## Deliberately not built

- Background removal and batch-first workflows.
- A second-pass image comparison is a separate project.
- PDF input; a one-line batch file in the Send To folder can turn a PDF page into a JPEG first.  First attempt at integrating it, was crashy bloat.  Maybe someday.
- The naming of backups (dot prefix versus other schemes) is parked, and the dot prefix stays for now.

## Maybe in the future

- WinXP style "File, Edit, Help" menus at the top?  File open would select a new folder, file close, file save would save only _which_ file you left off at.  Edit would have jumptos for TL, TR, BL, BR merely opening that CornerEditor().  
- Undelete from `.trashed_` backups and from the `.originals` folder, renumbering the restored file if the name is taken.  Parked until someone asks.
- Free rotation by degrees (0 to 360) for the selection rectangle.  Rotation is 90, 180 and 270 only.  Free rotation was rejected at first but it will be reconsidered.
- Interface translation.  If it ever happens, the plan is to use standard interface terms so existing glossaries can be reused.
- Entering the output size, or fitting the result to a paper size.  Showing the size is enough.  Placing the picture on a page is probably a different program.
- Two purple dots per side.  One curve per side has been enough so far, the Bezier math is already unintuitive, and a second dot would add to that.  No flag-wave pattern has needed it yet.  It will be revisited someday.
-
