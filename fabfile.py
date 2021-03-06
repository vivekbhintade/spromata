from fabric.api  import *
import config

HOSTNAME = 'spromata'

env.hosts = [HOSTNAME]
env.use_ssh_config = True
env.key_filename = "$HOME/.ssh/%s.pem" % HOSTNAME

# Remote

def pull():
    with cd(config.site_name):
        run("git pull")

def restart():
    run("sudo supervisorctl restart %s_server" % config.site_name)

def tail():
    with cd(config.site_name):
        run("tail -f stdout.log")

# Local

def push():
    local("git push")

# Combined

def pull_restart():
    pull()
    restart()
def push_pull():
    push()
    pull()
def push_pull_restart():
    push_pull()
    restart()

pr=pull_restart
pp=push_pull
ppr=push_pull_restart
