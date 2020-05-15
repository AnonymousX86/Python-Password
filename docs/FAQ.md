# Frequently asked questions
Please read this, if you're unsure how the program works.


## Where passwords are stored?

Your passwords are stored locally, so only you can access this file from your's computer. Files are stored in default
local app data directory (default is `C:\Users\YOUR_USERNAME\AppData\Local`).


## How passwords are saved?

All password are stored in local SQLite database. ([What's SQLite?][sqlite]</sup>) Before program saves them, they're
being encrypted with alpha password, which is encrypted with beta password.


## What are alpha and beta passwords?

All passwords are encrypted with alpha password. So with the same alpha password, two passwords will be encrypted in
the same way.

Beta password is used to encrypt alpha password. So if you want to reproduce alpha password on another computer,
beta passwords must match. Otherwise, passwords will be encrypted in another way and you won't be able to get passwords
encrypted with another combination of alpha and beta passwords.


## Who has access passwords?

Only those who are using program, on your's computer profile. Different users on the same PC will have separate settings
and saved data.


## Program is acting weird, what can I do?

Probably you found a bug. Please let me know what it is by making and [issue][issues].


## I think something could be done better

That's great! Be sure to make an enhancement [issue][issues].

Or if you're a Python
programmer you can make a [pull request][pulls] with code changes.


## How can I get in touch with developer?

You can invite me via Discord, my nick is `Anonymous©#7296` or [send me an email][mail].


## I've not found what am I looking for

You have two options:
- Open new issue [here][issues].
- Write to me.


[sqlite]: <https://www.sqlite.org/index.html>
[issues]: <https://github.com/AnonymousX86/Python-Password/issues/new/choose>
[pulls]: <https://github.com/AnonymousX86/Python-Password/pulls>
[mail]: <mailto:jakub.suchenek.25@gmail.com>
