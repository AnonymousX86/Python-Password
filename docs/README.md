# Python Password

![Code correctness](https://github.com/AnonymousX86/Python-Password/workflows/Code%20correctness/badge.svg)

**This project is my first desktop app - password manager. It's made with Python 3.7 and [material design standard](https://material.io/).**

## What's the program about?

Python Password is intended to safely store passwords. They are encrypted with two master passwords and saved locally.
Master passwords could be randomly generated or set by user, so you can re-create them when they're gone for some reasons
or you'd like to share your passwords with someone. Of course many users on the same PC will have separate data folders.
When you would like to get any password it won't be prompted on the screen, but safely copied to clipboard with no risk
that someone could view your password.As you know that youre password save on system ,so we give an option to configure and
logint to youre account directly from this app you just have to give auto login permistion to your account you can disable this 
featers from setting.there is also a option for dark theam.

![Passwords menu](https://github.com/AnonymousX86/Python-Password/blob/master/docs/screenshots/Passwords%20menu.png)


## Quick start guide


### Passwords menu

Main screen of program is passwords menu. From here you can:

- add passwords,
- copy passwords,
- delete passwords.

On the left side there will be displayed list of saved passwords. You can click on specific password to see context
menu wth  3 options; "copy", "delete" and "nothing".

On the right side there are 4 sections.

1. **Adding password** - to add password, simply enter it's alias and password itself. Then click button to add it.
2. **Removing password** - you can delete password also from here. Simply provide it's alias and click button.
3. **Info** - here you can see how many passwords there are in database.
4. **Refresh** - click this button to refresh view, and fetch passwords from local database.
  
  
### Settings menu

In this menu, you can:

- change alpha password,
- change beta password,
- change theams,
- check for updates

You can see in
[`FAQ.md`](https://github.com/AnonymousX86/Python-Password/blob/master/docs/FAQ.md#what-are-alpha-and-beta-passwords)
how do they work.

![Settings with side menu](https://github.com/AnonymousX86/Python-Password/blob/master/docs/screenshots/Settings%20with%20side%20menu.png)


### Info menu

On the left side, there are some basic information about version, author and 3rd party software.

On the right side you can see (of course clickable) links.


## How to start using?

For download please look at [latest release](https://github.com/AnonymousX86/Python-Password/releases/latest).

![Context](https://github.com/AnonymousX86/Python-Password/blob/master/docs/screenshots/Context.png)


## Ideas what to add

| Idea | Added in version |
| ---- | ---------------- |
| Theme changing. | v0.2.3 |
| Many translations. | v0.2.5 |
| Clear cache 15 seconds after copy password. | - |
| Login system. | - |
| Ciphering database. | - |


### You can find more information about project in:

- [FAQ](https://github.com/AnonymousX86/Python-Password/blob/master/docs/FAQ.md).
- [Changelog](https://github.com/AnonymousX86/Python-Password/blob/master/docs/CHANGELOG.md).

---

**If you want to help me improve this program, (report issues etc.) or just talk, please contact me via
Discord: `Anonymous©#7296`, or use [GitHub issues](https://github.com/AnonymousX86/Python-Password/issues).**
