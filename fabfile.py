from fabric.api  import *
import config

env.hosts = ['prontotype.us']
env.user = "ec2-user"
env.key_filename = ["/Users/sean/.ssh/hjklist_key_0.pem",]

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
