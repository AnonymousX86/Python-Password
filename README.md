# Python Password

<<<<<<< HEAD
![Code correctness](https://github.com/AnonymousX86/Python-Password/workflows/Code%20correctness/badge.svg)

**Hello world!** This is my first project of usable program.
=======
**Hello world!** This is my very first project of usable program.
>>>>>>> dev

### What is the program about?

Python Password is intended to safely store passwords.

### How does it work?

Program is saving passwords to local database (SQLite database). Passwords are encrypted with a secret key, based on
master password and salt, both could be a user input or random values, so you can re-create the file when it's gone for
some reasons. When you would like to get any password it won't be prompted on the screen, but safely copied to
clipboard.

## Quick start guide


### Passwords menu

Maim screen of program is passwords menu. From here you can:

- add passwords,
- copy passwords,
- delete passwords.

On the left side there will be displayed list of saved passwords. Ypu can click on specific password to see context
menu wth 3 options; "copy", "delete" and "nothing".

On the right side there are 4 sections.

1. **Adding password.** To add password, simply enter it's alias and password itself. Then click button to add it.
2. **Removing password.** You can delete password also from here. Simply provide it's alias and click button.
3. **Info.** - Here you can see how many passwords there are in database.
4. **Refresh.** - Click this button to refresh view, and fetch passwords from local database.
  
  
### Settings menu

In this menu, you can:

- change alpha password,
- change beta password.

You can see in `FAQ.md` how do they work.

There will be also options to manage backups.


### Info menu

On the left side, there are some basic information about version, author and 3rd party software.

On the right side you can see (of course clickable) links.


## How to start using?

For download please look at [releases section](https://github.com/AnonymousX86/Python-Password/releases).

---

*If you want to help me improve this program, (report issues etc.) or just talk, please contact me via
Discord: `Anonymous©#7296`, or use [GitHub issues](https://github.com/AnonymousX86/Python-Password/issues).*
