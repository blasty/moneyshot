Moneyshot
====================

A collection of python scripts to aid you in the final steps
of binary exploitation or during the construction of buffers.

This project is by no means any rocket-science, and many of
these components might remind you of loose scripts that everyone
has written at some point in time. ;-)


Dependencies
---------------------
Moneyshot depends on:

* python (2.x for now)
* diStorm3 (for disassembly functionality)

There's some external libraries that moneyshot depends on as well.
however, (local) installation of these is automatically done by
setting up the git submodules. (See installation notes)

Installation
---------------------
<pre>
$ git clone https://github.com/blasty/moneyshot.git
$ cd moneyshot
$ git submodule init
$ git submodule update
$ cd lib/darm && make 
</pre>

Usage
---------------------

Running moneyshot.py without any arguments gives you an overview of 
all modules/commands currently implemented. If you supply an action
without any arguments moneyshot will inform you about the usage
of the specific module/action.

<pre>
$ ./moneyshot.py
    __   __  ______.___   __  _____._  __._______._ __  ____._________
   /  \ /  \/  __  |    \|  |/  ___| \/  /\  ___/  |  |/ __  \__   __/
  /    '    \   /  |  |\    |   _|_\    /__\   \|     |   /  |  |  |
 /___\  /    \_____|__|  \__|______||__||______/|__|__|\_____|  |__|
      \/ _____\


  usage: moneyshot <action> [options]

  actions:
    * list     - list shellcodes
    * build    - build shellcodes
    * pattern  - build patterns
    * lolsled  - build a lolsled
    * format   - format input
    * fmt      - formatstring helper
    * rop      - ROP helper
    * rop-arm  - ARM ROP helper
    * rep      - String repeater
    * dwords   - binary format dwords
    * dumpsym  - dump symbols for given binary
    * dumpelf  - dump information for given binary
</pre>


Todo
---------------------

If you want to help out and improve moneyshot, that would
be most welcome. I'm a very lazy coder so I only work
in small spurts when I need a feature/fix myself. But
if you send me sensible pull requests it is likely that I
will merge them into the master repo. If you're looking for
some inspiration of what to implement/fix:

* The structure of my code sux, needs to be more pythonic, I suppose.
* Commandline argument handling is a horrible hack, switch to argparse maybe.
* The rop and rop-arm module are currently separated, but mostly equal logic-wise..
* The ELF parser is an ugly and horrible hack, rewrite or replace with a proper lib
* Assembling x86(-64)/ARM code is done using a system("gcc..") hack atm..
* Mach-O support
* PE (win) support
* Make ROP module(s) agnostic of binary format (currently only ELF32/ELF64)
* Turn moneyshot into an actual python module with a sane API, so we can import * from moneyshot
* ROP gadget finding is nice, but we might be able to propose full ROP chains as well
