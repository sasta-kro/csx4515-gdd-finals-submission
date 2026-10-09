# Three Ways to Play

A Unity game collection by **Sai Aike Shwe Tun Aung**, created for CSX4515 Game Development.

Three Ways to Play combines driving, flying, and sumo ball gameplay in one project. A shared main menu lets players choose a game or exit, while each game has a pause menu for resuming, restarting, or returning to game selection.

## Games

| Game | Overview |
| --- | --- |
| **Mad Driver** | Drive through a road course with traffic and obstacles. Switch between two camera views. |
| **Fly Like a Bird** | Guide a continuously moving plane through an obstacle course by controlling its pitch. |
| **I'm a Sumo and a Ball** | Stay on a floating island, push enemies off the arena, and survive growing waves. Collect knockback, projectile, and smash powerups, with bosses and smaller enemies joining later waves. |

## Getting started

### Requirements

- Unity **6000.5.3f1**, preferably installed through Unity Hub
- Git to clone the repository
- Internet access for initial package downloads

### Open and play

1. Clone this repository with Git.
2. In Unity Hub, add the cloned project folder containing `Assets`, `Packages`, and `ProjectSettings`.
3. Open it using Unity 6000.5.3f1 and wait for package resolution, asset import, and script compilation to finish.
4. Open `Assets/Scenes/MainMenu.unity` and press **Play**.

**The first opening can take several minutes.** Unity downloads required packages and rebuilds its local asset and shader caches. These generated files are excluded from Git and subsequent openings are usually faster.

The repository contains everything needed to play, edit, and build the game. Git LFS and the original tutorial projects are not required.

## Controls

| Game | Movement | Additional controls |
| --- | --- | --- |
| Driving | W/S or Up/Down to drive, A/D or Left/Right to steer | C switches cameras |
| Flying | W/S or Up/Down to pitch | Forward movement is automatic |
| Sumo | W/S or Up/Down to roll, A/D or Left/Right to rotate the view | Collect powerups to activate their effects |

Click menu buttons or use Up/Down and Enter to select an option.

Press **Escape** or click **Pause [Esc]** during any game to open the pause menu. **Resume** continues the current game, **Restart** resets it, and **Back to Main Menu** returns to game selection. Escape also closes the pause menu. After falling off the sumo island, use the pause menu to restart.

**Exit** closes a built game. In the Unity Editor, it stops Play mode.

## Building

Open **File > Build Profiles**, select a desktop platform, and install its build support through Unity Hub if needed. The four enabled scenes are already configured in this order:

1. MainMenu
2. Driving
3. Flying
4. Sumo

Use **Build** or **Build and Run**. Local build output is excluded from Git.

## Project layout

| Folder | Contents |
| --- | --- |
| `Assets/Games/Driving` | Driving scene, gameplay scripts, models, materials, and prefabs |
| `Assets/Games/Flying` | Flying scene, gameplay scripts, plane assets, and preserved baked lighting |
| `Assets/Games/Sumo` | Sumo scene, enemy and powerup prefabs, gameplay scripts, and mist effect |
| `Assets/Scenes` | Main menu scene |
| `Assets/Prefabs` | Shared pause menu and game HUD |
| `Assets/Scripts/Menus` | Menu navigation and pause behavior |
| `Tools` | Optional reference checks and asset-generation utilities |

The project uses the **built-in render pipeline**, **legacy input**, and native **uGUI** menus. Each game's scripts have a separate namespace.

## Alternative assets

A small set of alternatives is retained for experimenting with the scenes:

- A blue car and a traffic cone in the driving asset folders
- A cube-shaped floating island, potion pickup model, and alternate selection ring in the sumo asset folders
- An additional grid material for sumo and a grey obstacle material for flying

Keep the existing gameplay scripts, colliders, tags, and required object names when replacing visuals. `Tools/retained-alternatives.json` lists the exact asset paths.

## Optional tools

After Unity has imported the project, run `python3 -B Tools/verify_project.py` from the project folder to check serialized references, scene registration, menu callbacks, and lighting dependencies. This does not run the game.

The menu-generation and lighting-remapping utilities are optional maintenance tools. They expect the original course workspace layout and its `w6_Prototype1_v2` project. They are not needed for normal play, editing, or building. Regenerating menus replaces their saved layout.

## Credits and asset usage

Gameplay is adapted from Unity Learn's driving, flying, and sumo learning projects. Course assets include models and textures provided by Synty Studios. The original asset license notices are retained with the driving and sumo source assets and state that these assets are not for commercial use.
