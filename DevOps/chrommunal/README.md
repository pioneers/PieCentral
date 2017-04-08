# chrommunal

chrommunal is a collection of setup scripts written to ease the process of setting up a PiE
public-use chromebook to run both the Dawn IDE and ubuntu via crouton. Unfortunately, it is more or
less impossible to totally automate the process, but we attempt to simplify the entire process to
being only a few steps given in the instructions below.

## Setup instructions

* Switch the chromebook to developer mode. Instructions on how to do this can be found
  [here](http://www.howtogeek.com/210817/how-to-enable-developer-mode-on-your-chromebook/). Note
  that the power button on the convertible Acer chromebooks can be found on the right-hand side
  of the laptop (it's pretty easy to miss).

* Open a crosh developer terminal by typing `ctrl+alt+t`, and type `shell` to switch to a real unix
  shell. From there, copy/paste or type the following command, then hit enter

  `wget -O - https://raw.githubusercontent.com/pioneers/DevOps/master/chrommunal/setup-chrome.sh | bash`

  * If you get the following error:
  
  ```
  Please specify a username for the primary user: Failed to complete chroot setup. The chroot setup script may be broken. Your chroot is not fully configured. Removing the chroot setup script. You may want to update your chroot again. UID 1000 not found in trusty
  ``` 
  
  run: `sudo sh ~/Downloads/crouton -u -n trusty`

* After the script finishes running, enter the following into the linux terminal that your shell
  instance was replaced with.

  ```wget -O - https://raw.githubusercontent.com/pioneers/DevOps/master/chrommunal/setup-ubuntu.sh | bash```

## Usage

Now that everything is installed, you can find a short (and probably incomplete) list of things that
the chromebooks can do below. For all of these commands, we assume that you have already opened up
a crosh shell using `ctrl+alt+t` and typed `shell` to enter a real unix shell.

* `dawn` can be used to open an instance of Dawn within ChromeOS
* `term` enters the install within the terminal currently open (think of it as ssh-ing in) again
   within ChromeOS.
* `ubuntu` switches the GUI entirely to an ubuntu environment. Switching back and forth is possible
  with `ctrl+alt+shift+<left/right arrow>`.

## Names

All chrommunal laptops will be named after *-creme
