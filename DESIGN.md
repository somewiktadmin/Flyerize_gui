# Flyerize design notes

These notes explain why Flyerize behaves the way it does, so the odd-looking choices make sense. For how to use it, see the README.

## Scope

- Flyerize straightens one flyer, banner or sheet of paper in one photo, hanging on a wall, fence or door. That is the job it is built for, and it does it well.
- It is not a media editor. It does not remove backgrounds, retouch, resize or compress. Feature requests that drift toward a full editing suite are out of scope.
- It is interactive first. Folder mode exists for convenience, but the design assumes a person looking at each photo.
- Heavier automatic detection (edge refinement, corner voting) was tried early and set aside. Lowering its thresholds only produced distorted results. The first guess is deliberately simple, and the person fixes it.

## Principles

- **Non-destructive by default.** The first save never touches the original. Every save button except one keeps a way back.
- **Overwrite! is the only button that can lose something for good.** It is named with an exclamation point on purpose, and the README explains it in detail.
- **No snapping and no automatic border measuring.** Corners land exactly where you put them, in whole pixels. Even a one-pixel snap feels wrong when you are trying to hit an edge, and measuring borders automatically would be slow.
- **No resampling for size.** The result has about as many pixels as the area you selected, so Overwrite! is not a compressor and the docs never promise space savings.
- **Nothing is hidden.** The default backups are ordinary files with a dot-prefixed name (.trashed_ before the file name), or files in a visible .originals folder. The program sets no hidden attribute and makes no special system calls for them, so they sit beside the photo as obvious candidates for manual deletion. Settings also offers the Recycle Bin, which is the least tested of the three methods and is meant to fall back to the .trashed_ method on drives that have no bin.

## Corners, sides and gestures

- Corners drag like every other handle. Early testing showed people instinctively try to drag them, and click-only red corners next to draggable purple dots was inconsistent.
- X and Y stay visible and editable in a docked magnifier that remains up after a drag. A larger magnifier view is one click away for fine work.
- Each side bends with one purple dot, which slides along its line. Right-click straightens that side. One curve per side was judged enough, and two dots per side was rejected as overkill.
- Side drags lock to the perpendicular direction, because missing by a few pixels in the wrong direction leaves a sliver of border on one corner. Shift unlocks the drag.
- Start gestures are valid only while the whole photo is in view, never while zoomed in. They are a closed rectangle, a Z, or a corner-to-corner slash, and they set straight sides and clear any bends.
- Two validation rules decide whether a stroke counts. The stroke must be at least 30 screen pixels across, which stops accidental clicks. The shape it proposes must also cover at least 1 percent of the photo's area. The 1 percent rule is deliberate. For a small flyer in a big photo, the intended workflow is to draw a larger box first, then zoom with the mouse wheel and drag the sides and corners into place.
- A gesture shows a ghost of the proposed corners with Apply and Cancel, rather than applying silently and offering undo afterward. The Confirm setting turns these prompts off for people who want speed.

## Saving and naming

- **Save New** writes a new file and leaves the original alone. **Replace** backs up first. **Overwrite!** does not. **Rename** renames the file without rewriting the picture and keeps its extension. **Delete** moves the photo aside as a backup, with no question asked, because nothing is destroyed.
- The name box starts at the original's name and always shows the name just written. The program never rewrites it after a save, so repeated saves can produce names like name~1~1. That is accepted, since every save is a separate file and nothing is lost.
- Replace and Overwrite! act on the file the box names. If it exists, it is backed up (Replace) or overwritten (Overwrite!). If the name is free, the original is backed up or removed and the result lands under the new name.
- Overwrite! never adds a number, so a second click overwrites the same result file.
- Numbering: any ~nn counts as one of the program's own numbers, and several are summed (name~1~4~7~2 starts as name~14). For timestamp-style names (YYYY-MM-DD_HH-MM-SS), the sum is added to the seconds instead, and only the seconds ever change. A taken name gets a number up to ~99, and backups go up to ~999.
- Typing in the name box counts as an unsaved change when you leave a photo.
- A save writes the result to a temporary file first, so a failure such as a full disk or a read-only folder or share stops before anything is changed. The system's message appears in a dialog and the program stays open.
- The Overwrite! question lives in a persistent Settings checkbox, not a once-per-session warning. The dialog stays terse, because a crisis moment is the wrong place for a lecture. The longer note sits at the top of Settings.

## Navigation and Auto

- Results made by Save New are inserted into the list right after their photo. Back and Move can land on them. Skip to Next and Auto go straight to the next original.
- Skip to Next is the most pressed button, since nearly every save is followed by it, so it sits close to the save buttons.
- Auto advances after each save. While it is on, the four save buttons show an arrow on pale green and the navigation buttons turn gray but still work. Auto is kept away from Delete and Overwrite!.
- Leaving a photo with unsaved changes asks first if the Confirm setting is on. If it is off, the corners are quietly added to the Recents list instead.
- Recents are corners only, newest first, de-duplicated, up to 500. One click applies them, which suits a series shot from the same spot.

## Keyboard

- Alt is the main modifier. A, S and D are Replace (Amend), Save New and Overwrite! (Dangerous). B, N and M are Back, Skip to Next and Move. R renames and V toggles the preview. Ctrl+B and Ctrl+N are alternates, and Ctrl+Shift+Alt with B or N jumps 100.
- Ctrl is the times-100 step for the arrow keys, WASD and plus and minus, so Ctrl letter shortcuts are avoided. Ctrl+R stays Reset.
- F2 and Ctrl+Z are deliberately untouched. F2 means rename in Explorer, and Ctrl+Z is reserved in case a real undo is ever added.
- Shortcuts that would clash with typing are ignored while a text box has the keyboard.
- There are no extra safety bumpers on the shortcuts. Over-protection was explicitly declined.

## Output options

- Crop to lines cuts the result at your four sides. Off keeps the whole photo, straightened.
- Rotate, Mirror and BW/WB change only the preview and the saved result. BW/WB is experimental, and its thresholds were tuned by eye (about 64 and 160).
- Outline writes a ~dbg picture of the original with your lines drawn on it, including the grid when it is on.
- The grid is curved to follow the bends in the main view, and straight in the preview when Crop to lines is on.

## Deliberately not built

- Background removal and batch-first workflows.
- Interface translation. If it ever happens, the plan is to use standard interface terms so existing glossaries can be reused.
- Ctrl+Z undo and Undelete are parked, with their scope undecided.
- The naming of backups (dot prefix versus other schemes) is parked, and the dot prefix stays for now.

## Maybe in the near future

- A [DBG] button that replaces the Outline checkbox in exactly the same position. It would write an original-size picture with the overlays (the lines, the grid and the start stroke) to a name~dbg~nn file, without forcing a regular save alongside it.
- Log files. They are tabled, not ruled out.
- An in-app Help panel (F1) built from the README.
- A first-run help screen, shown once.
- A fallback for backups: if the .originals folder cannot be created (for example where subfolders are not allowed), use the .trashed_ prefix instead.
