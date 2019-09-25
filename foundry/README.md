# cartographer

`cartographer` is a PiE project for painlessly managing IT resources like robots, driver stations, and developer environments.
We use [Ansible](https://www.ansible.com/) to automate deployments and specify standardized configurations as code in PieCentral.
`cartographer` unifies several prior disparate projects: `frankfurter`, `chrommunal`, and `axiom`.

## Setting Up a Development Environment

1. Install [Virtualbox](https://www.virtualbox.org/), then [Vagrant](https://www.vagrantup.com/downloads.html).
   This will allow you to provision and run a virtual machine (VM).
1. Open [`roles/base/defaults/main.yml`](roles/base/defaults/main.yml) in a text editor, and change `name` and `email` to your name and your `_@pioneers.berkeley.edu` email.
1. Open a terminal.
   * If you're using OS X, open the `Terminal` app.
   * If you're using Windows, open `Command Prompt`.
   * If you're using Linux, you probably already know how to open a terminal.
1. Run `vagrant up && vagrant provision`.
   You should see a bunch of messages being printed to your screen.
1. Log into your machine with `vagrant ssh`.
1. If you haven't already, sign up for a [GitHub](https://github.com/) account.
   GitHub hosts many projects, including those outside of PiE.
1. Run `cat ~/.ssh/id_rsa.pub`.
   It will print something like: `ssh-rsa <random characters> <email>@pioneers.berkeley.edu`.
   Copy this line and [follow these instructions](https://help.github.com/en/articles/adding-a-new-ssh-key-to-your-github-account) for adding this key to your GitHub account.
   Now, whenever you check in code, you won't need to enter a password.
