# Python Password

**Hello world!** This is my first project of usable program.

*For now it's named as above, because I have no better idea how to name it. Here are some words about it.*

## What is the program about?
Python Password is intended to safely store passwords.
##### Current version 0.1 (Alpha)

## How does it work?
Program is saving passwords to local database (SQLite database). Passwords are encrypted with a secret key, based
on master password and salt, both could be a user input (or only the first one) so you can re-create the file
when it's gone for some reasons. When you would like to get any password it won't be prompted on the screen, but
safely copied to clipboard.

## Quick start guide
1. At very first launch, program will create 3 files:

   - `Alpha.key`,
   - `Beta.key`,
   - `Passwords.db`.
   
   All of them are needed for proper program functioning. Each subsequent start of the program is trying to find those
   files. Every missing file will be re-created.
   
2. After program will check files, you will se typical console GUI. You can provide option number, or underlined letter.
   Options are:
   
   1. **Change alpha password** - if you want to change your master password.
   2. **Get password** - program shows all saved passwords' names and asks which you want to get. Password isn't
      prompted, it's being copied to clipboard. (Same as <kbd>Ctrl + C</kbd>, <kbd>Ctrl + V</kbd>)
   3. **Set password** - used for saving password.
   4. **Delete password** - after double inserting password's name, that password is being deleted from local database.
   5. **Info** - useful links and info about the program.
   6. **Exit** - I think I don't have to describe it.
   
3. Program is working in loop, so it will continue working unless you will close the window or select `Exit` option.

## How to start using?
For download please look at [releases section](https://github.com/AnonymousX86/Python-Password/releases).

If you want to help me improve this program, (report issues etc.) please contact me via Discord: `Anonymous©#7296`,
or use [GitHub issues](https://github.com/AnonymousX86/Python-Password/issues).

### Thanks for all of your help!
