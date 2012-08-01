# Dingle

Some basic process automation for the iPlant QA Drops. You will need the following to do anything interesting:

* Commit access to the git repos.
* Passwordless SSH access to the dev machines.
* sudo access on the dev machines.
* Jenkins tokens for the jobs you want to trigger.

This project is meant to be used from Leiningen's REPL. 


## Setup

Create a file at ~/.dingle/config.clj. It should look like the following

'''
(ns dingle.config)

(def config
  (hash-map
    :ssh-user "<your ssh user>"
    :ssh-password "<your ssh password>"
    :sudo-password "<your sudo password>"
    :github-base-url "git@github.com:iPlantCollaborativeOpenSource/"
    :jenkins-url "<your jenkins url>"
    :jenkins-token "<your jenkins token>"
    
    :prereq-repos  ["clj-jargon.git"
                    "iplant-clojure-commons.git"]
    
    :prereq-jobs   ["clj-jargon"
                    "iplant-clojure-commons"]
    
    :list-of-repos ["iplant-clojure-commons.git"
                    "clj-jargon.git"
                    "Nibblonian.git"
                    "facepalm.git"
                    "OSM.git"
                    "metadactyl-clj.git"
                    "iplant-email.git"
                    "JEX.git"
                    "Panopticon.git"
                    "filetool.git"
                    "Scruffian.git"
                    "Donkey.git"
                    "Conrad.git"]
    
    :list-of-services ["nibblonian"
                       "metadactyl"
                       "scruffian"
                       "panopticon"
                       "donkey"
                       "jex"
                       "notificationagent"
                       "osm"
                       "iplant-email"
                       "conrad"]))
'''

Substitute the values for your accounts in the above as appropriate. Do *NOT* check them in to a public github repo.

## Doing stuff

Assuming you've got the config file in place and Dingle checked out, run 'lein repl' from the top level Dingle directory. The first thing you should do is run '(configure)'.

Here's an example workflow:

'''
(configure)
(merge-and-tag-prereqs "a-git-tag-string")
(build-prereqs)
(merge-and-tag-repos "a-git-tag-string")
'''

Right now, none of the functions that interact with Jenkins are blocking, so you'll have to watch Jenkins to tell when builds are complete. This will be fixed in the future, most likely.