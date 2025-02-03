# Changelog

All notable changes to this project will be documented in this file.

---

## [1.10.1] - 2025-02-05
### Added
- **Mod List Links**: Changed mod list into clickable links.
- **Extra Links Dropdown**: Added a dropdown for extra relevant links.
- **Hints Feature**: Introduced a hint system that randomly displays useful hints underneath the title.
- **Rainbow Effect Toggle**: Added a setting to disable the rainbow color effect.

---

## [1.10.0] - 2025-02-03
### Added
- **Drag and Drop Mod Installation**: Users can now drag and drop folders, archives, or files onto the manager to prepare for custom mod installations. These will be installed after the main modpack mods.
- **Light/Dark Mode**: Introduced a dropdown in settings to switch between light and dark themes.
- **Automatic Manager Updates**: The manager now checks for updates and installs them automatically.

### Fixed
- **Invisible Checkboxes**: Resolved an issue where checkboxes were not visible in certain themes.
- **Remove and Backup Mods Overwriting Defaults**: Now properly retains custom settings.
- **Branch Dropdown Auto Guides**: Branch selection now correctly triggers guidance blinks.
- **Miscellaneous Bug Fixes**: General stability improvements.

---

## [1.9.3] - 2025-02-02
### Added
- **Light/Dark Mode**: Introduced a dropdown in settings to switch between light and dark themes.
- **Automatic Manager Updates**: The manager now checks for updates and installs them automatically.
  
### Fixed
- **Invisible Checkboxes**: Resolved an issue where checkboxes were not visible in certain themes.
- **Remove and Backup Mods Overwriting Defaults**: Now properly retains custom settings.
- **Branch Dropdown Auto Guides**: Branch selection now correctly triggers guidance blinks.
- **Miscellaneous Bug Fixes**: General stability improvements.

---

## [1.9.2] - 2025-02-01
### Added
- **Elapsed Timer for Downloads/Updates**: Shows estimated time remaining during operations.

### Changed
- **Auto Refresh for Installed Modpacks**: Installed modpack information refreshes immediately after install/uninstall.

---

## [1.9.1] - 2025-01-31
### Added
- **Steam Deck Support**: Added compatibility for Steam Deck users.

### Fixed
- **Force Download Crash**: Resolved a fatal crash when force downloads completed, but the manager couldn't determine which button to stop blinking.

---

## [1.9.0] - 2025-01-30
### Added
- **Settings Overhaul**: 
  - Introduced a tabbed settings menu.
  - New options for skipping mod selection, auto-install after downloads, and more.
- **First-Time User Guidance**: The manager now assists new users in downloading and installing modpacks and Lovely Injector.

### Fixed
- **General Bug Fixes**.

---

## [1.8.2] - 2025-01-29
### Fixed
- **Preset Loading Issue**: Fixed presets not being read correctly.
- **Custom Game Directory Registration**: The manager now properly recognizes custom game directories.

---

## [1.8.1] - 2025-01-23
### Added
- **Linux Support Fixes**: Adjustments made to improve compatibility.
- **Version Checking for Modpack Branches**: Now supports checking mod versions per branch.

---

## [1.8.0] - 2025-01-20
### Added
- **Branch Switching**: Users can now switch to different development branches of a modpack.
- **macOS Support**: The manager now runs on macOS.
- **Smods Cleanup**: Detects and removes redundant Steamodded installations.

### Fixed
- **Update Prompt Hidden by Splash Screen**: The splash screen no longer obstructs update notifications.

---

## [1.7.0] - 2025-01-15
### Added
- **New Logo Splash Screen**: Updated branding.
- **Custom Preset Management**: Users can now save and manage custom mod selection presets.
- **Offline Mode**: Allows basic modpack management without an internet connection.

---

## [1.6.11] - 2025-01-10
### Fixed
- **Crash When Saving Settings**: A bug causing crashes when modifying settings has been fixed.

---

## [1.6.10] - 2025-01-09
### Fixed
- **General Bug Fixes and Improvements**.

---

## [1.6.9] - 2025-01-05
### Fixed
- **Reverse Selection Button**: Now correctly reverses dependent mods.
- **Installation Progress Bar**: Displays a progress bar while installing modpacks.

---

## [1.6.8] - 2025-01-04
### Fixed
- **Quick Update Module**: Resolved persistent errors during quick updates.

---

## [1.6.7] - 2025-01-04
### Fixed
- **Dependencies System**: Fixed dependency issues again.
- **Dynamic Dependencies**: Dependencies are no longer hardcoded.
- **General Bug Fixes**.

---

## [1.6.6] - 2025-01-04
### Fixed
- **Dependencies System**: Further fixes for mod dependencies.
- **Dynamic Dependencies**: Dependencies are now dynamically handled.

---

## [1.6.3] - 2025-01-03
### Fixed
- **Quick Update Functionality**: Finally resolved issues preventing quick updates from working correctly.

---

## [1.6.2] - 2024-12-31
### Fixed
- **Excluded Mods Not Loading**: Excluded mods are now properly recognized when selecting mods.

---

## [1.6.1] - 2024-12-31
### Added
- **Mod Hover Information**: Hovering over a mod now displays its genre, tags, and description.
- **Right-Click Mod Actions**: Right-clicking a mod allows users to visit its Discord thread or mod page.

### Fixed
- **Mod Selection Panel Too Long**: The left panel is now scrollable.
- **Favorite Mods Not Saving**: Favorite mods now persist correctly.

---

## [1.6.0] - 2024-12-31 (Pre-release)
### Added
- **Mod Selection UI Overhaul**: Complete redesign of the mod selection UI.
- **Modpack Genres & Tags**: Mods are now categorized by genre and tag.

### Known Issues
- **Potential Bugs**: This update may introduce new bugs due to significant changes.

---

## [1.5.7] - 2024-12-28
### Added
- **Refresh Button Centering**: The refresh button is now centered.
- **Scrollable Mod Selection Popup**: The mod selection popup now supports scrolling.
- **Mod Selection Search/Filter**: Users can now filter and search for mods within the selection popup.

---

## [1.5.6] - 2024-12-27
### Added
- **Automatic Modpack Verification**: Modpacks are now verified automatically after cloning or updating.
- **Lovely Injector Check**: The manager now checks if Lovely Injector is installed before launching the game.

---

## [1.5.5] - 2024-12-21
### Added
- **Improved Failcase Notifications**: Modified notifications to be clearer in failure scenarios.
- **New Mod Dependencies**: Added additional mod dependencies.

---

## [1.5.4] - 2024-11-06
### Fixed
- **General Bug Fixes**.

---

## [1.5.3] - 2024-11-03
### Fixed
- **Git Issues During Downloads**: Attempted to resolve problems with Git operations when downloading modpacks.

---

## [1.5.2a] - 2024-10-27
### Fixed
- **General Bug Fixes**.

---

## [1.5.1] - 2024-10-25
### Fixed
- **General Bug Fixes**.

---

## [1.5.0] - 2024-10-24
### Added
- **Remote Modpack Data Fetching**: Populates modpack list, URLs, and descriptions dynamically.
- **New Modpack Support**: Expanded support for additional modpacks.
- **Multi-Modpack Downloads/Updates**: Users can now download and update multiple modpacks at once.
- **Manager Update Check**: The tool now checks for its own updates.
- **Dynamic UI Colors**: The UI can change colors dynamically.

### Fixed
- **General Bug Fixes**.

---

## [1.4.5] - 2024-10-19
### Added
- **Verify Modpack Button**: Added a button to verify the integrity of installed modpacks.

---

## [1.4.4] - 2024-09-29
### Added
- **"I Feel Lucky" Button**: Randomly selects mods when installing modpacks.

---

## [1.4.3] - 2024-09-29
### Added
- **Toggle for Mods Folder Removal**: Users can now choose whether to remove the Mods folder before installing new modpacks.
- **Support for Taquin Paquet**: Added compatibility for the Taquin Paquet modpack.

### Fixed
- **Reverse Selection in Mod Install Popup**: Fixed an issue where reverse selection did not function as intended.

---

## [1.4.2] - 2024-09-25
### Added
- **Mod Dependency System**: Implemented a dependency system in mod selections.

### Fixed
- **Coonie's Modpack Version Checking**: Resolved an issue where Coonie's pack version was not being properly checked.

---

## [1.4.1] - 2024-09-22
### Added
- **Coonie's Modpack Support**: Added support for Coonie's modpack.

### Fixed
- **Progress Dialog Background**: Fixed grey background in progress dialogs.
- **General Bug Fixes**.

### Known Issues
- **Potential Bugs**: More bugs may exist; users are encouraged to report them.

---

## [1.4.0] - 2024-09-16
### Added
- **Dark Mode Compatibility**: Proper styles to ensure UI usability in dark modes.

---

## [1.3.1] - 2024-09-08
### Added
- **Simple Tutorial**: Added an in-app tutorial to guide new users.

---

## [1.3.0] - 2024-09-08
### Added
- **UI Enhancements**:
  - Buttons now have hover and pressed indicators.
  - Downloading and updating modpacks now display a progress popup.
  - The progress popup now centers on the main window.

### Changed
- **Backup Mods Folder Handling**: Changed the backup Mods folder prompt to a checkbox.

### Fixed
- **General Bug Fixes**.

---

## [1.2.6] - 2024-08-29
### Added
- **Revert to Current Button for Time Travel**: Allows users to revert without recloning the modpack.
- **Version Checking Improvements**: Manager is now included in the Check Versions function.

### Fixed
- **Time Travel Functionality**: Resolved issues with reverting modpacks.
- **Lovely Injector Indicator**: Properly indicates when Lovely Injector needs installation or updating.

---

## [1.2.5] - 2024-08-28
### Added
- **Quick Update Function**: Allows faster modpack updates.
- **Alignment Fixes**: Properly aligned elements in Check Versions.

---

## [1.2.4] - 2024-08-28
### Added
- **Quick Update Function**: Introduced the first version of Quick Update.

---

## [1.2.3] - 2024-08-27
### Added
- **New Modpacks**: Added support for the **Insane** and **Cruel** packs.

---

## [1.2.2] - 2024-08-26
### Added
- **Warning System for Mod Installation**: Users are now warned before installing modpacks.
- **Backup Mods Folder Function**: Prevents accidental data loss during mod installations.

---

## [1.2.1] - 2024-08-25
### Added
- **Auto Save Backup & Restore Function**: Automatically backs up and restores previous settings.
- **Menubar**: Added a menu bar for additional navigation.

---

## [1.2.0] - 2024-08-24
### Added
- **PyQt6 Migration**: The manager now utilizes PyQt6 instead of Tkinter.
- **Profile Creation**: Introduced profile creation functionality.

### Fixed
- **General Bug Fixes & Tweaks**.

---

## [1.1.3] - 2024-08-24
### Fixed
- **Modpack Info Update**: Now updates installed modpack info regardless of program location.
- **Install Button Functionality**:
  - Fixed issue where the install button became nonfunctional after being used once.
  - Resolved problem where the install button wiped the Mods folder before saving.

---

## [1.1.2] - 2024-08-21
### Changed
- **Main Window Layout**: Reorganized for better usability.

---

## [1.1.1] - 2024-08-20
### Fixed
- **General Bug Fixes**.

---

## [1.1.0] - 2024-08-20
### Added
- **Mod Selection Function**: Users can now choose which mods to install.

---

## [1.0.0] - 2024-08-20
### Added
- **Settings Functional**: Users can now adjust manager settings.
- **Profile Options**: Introduced profile management for different configurations.

### Fixed
- **Code Organization**: Improved code structure for maintainability.
- **General Bug Fixes**.

---

## [0.6.0] - 2024-08-19
### Added
- **Time Travel Function**: Users can revert to previous versions of a modpack.

---

## [0.5.2] - 2024-08-18
### Changed
- **Game Launch Method**: The manager now launches the game through Steam.

---

## [0.5.1] - 2024-08-18
### Added
- **Rewritten Update Function**: Now forces a clean download and install.
- **Short Explanations**: Additional context provided in parentheses for clarity.

---

## [0.5.0] - 2024-08-17
### Added
- **Settings Button**: Allows customization of the game and mods installation paths.
- **Manager Information**: Displays relevant details about the mod manager.

---

## [0.4.3] - 2024-08-15
### Fixed
- **Download Button Issue**: Attempted to fix the download button not functioning on certain devices.

---

## [0.4.2] - 2024-08-15
### Added
- **Mod List Button**: Users can now access the mod list directly from the manager.

---

## [0.4.1] - 2024-08-14
### Fixed
- **Lovely Injector Installation**: Resolved issues with installing Lovely Injector.

---

## [0.4.0] - 2024-08-14
### Added
- **Uninstall Button**: Allows users to remove installed modpacks.
- **Lovely Installation Abort Option**: Users can now abort the installation of Lovely Injector.
- **Discord Button Positioning**: Moved the Discord button for better accessibility.

### Removed
- **Redundant Settings Button**.

---

## [0.3.3] - 2024-08-14
### Added
- **Grid Layout**: Improved UI organization using a grid layout.
- **Blue Play Button**: Updated the Play button design.
- **Lovely Injector Button**: Added a dedicated button for installing Lovely Injector.

---

## [0.3.2] - 2024-08-13
### Changed
- **Title Padding Adjustment**: Adjusted `padx` on the title for better visual alignment.

---

## [0.3.1] - 2024-08-13
### Added
- **Dynamic Window Sizing**: The window now adjusts its size dynamically.
- **Play Button Size Adjustment**: Resized the Play button for better accessibility.

---

## [0.3.0] - 2024-08-13
### Added
- **Lovely Injector Download & Install**: Added functionality to install Lovely Injector.
- **Play Button**: Introduced a Play button to launch the game.

---

## [0.2.2] - 2024-08-13
### Added
- **Discord Forum Link**: Added a link to the Balatro modding community on Discord.

### Fixed
- **Directory Existence Check**: Fixed a bug where the program would error out if the target directory did not exist.

---

## [0.2.1] - 2024-08-13
### Fixed
- **Version Check Issues**: Attempted to fix problems with checking the installed version.

---

## [0.2.0] - 2024-08-13
### Added
- **Custom Installation Path**: Users can now customize the installation directory.

### Fixed
- **Version Check Functionality**: Attempted to resolve issues with detecting the installed version.

---

## [0.1.0] - 2024-08-13
### Initial Release
- **First version of Balatro Modpack Manager**: Basic functionality introduced.

---

For more details and past versions, visit the [Balatro Modpack Manager Releases](https://github.com/Dimserene/Balatro-ModpackManager/releases).
