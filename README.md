# Python Password

**Hello world!** This is my first project of usable program.

*For now it's named as above, because I have no better idea how to name it. Here are some words about it.*

## What is the program about?
Python Password is intended to safely store passwords.
##### Current version 0.1 (Alpha)

## How does it work?
At first launch program is creating local database (SQLite database). Of course program is searching for file
every time it's opened In that database passwords will be stored and `master.key` file, where's stored key
used to encrypt end decrypt passwords. That `.key` file is generated based on user password and random
ASCII symbol or also user input so you can replicate the key with 2 simple inputs.

## Quick start guide
1. At very first launch, program will create 3 files:

   - `settings.py`,
   - `master.key`,
   - `passwords.db`.
   
   All of them are needed for proper program functioning. Each subsequent start of the program is trying to find those
   files. Every missing file will be re-created.
   
2. After program will check files, you will se typical console GUI. You can provide option number, or underlined letter.
   Options are:
   
   1. **Re-generate master key** - if you want to change your master password.
   2. **Get password** - program shows all saved passwords' names and asks which you want to get. Password isn't
      prompted, it's being copied to clipboard. (Same as <kbd>Ctrl + C</kbd>, <kbd>Ctrl + V</kbd>)
   3. **Save password** - used for saving password.
   4. **Delete password** - after double inserting password's name, that password is being deleted from local database.
   5. **Info** - useful links and info about the program.
   6. **Exit** - I think I don't have to describe it.
   
3. Program is working in loop, so it will continue working unless you will close the windows or select `Exit` option.

oIf you want to help me improve this program, please contact me via Discord: `Anonymous©#7296`, or this repo's issues.

### Thanks for all of your help!
