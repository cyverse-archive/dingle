(ns dingle.core
  (:use [dingle.scripting] 
        [dingle.git]
        [dingle.services])
  (:require [clojure.string :as string]))

(defn full-repo-string
  "Prepends git URL to the name of the repo. Use with list-of-repos."
  [repo]
  (str "git@github.com:iPlantCollaborativeOpenSource/" repo))

(def list-of-repos
  "List of the basenames for the github projects that we want to manage."
  
  ["iplant-clojure-commons.git"
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
   "Conrad.git"])

(def list-of-services
  "List of the backend iPlant services. Also acts as a list of RPM names."
  ["nibblonian"
   "metadactyl"
   "scruffian"
   "panopticon"
   "donkey"
   "jex"
   "notificationagent"
   "osm"
   "iplant-email"
   "conrad"])

(defn report
  [cmd-map]
  (println (string/join (repeat 80 "-")))
  (println (str "Exit Code: " (:exit cmd-map)))
  (println (str "Stdout: "))
  (println (:out cmd-map))
  (println (str "Stderr: "))
  (println (:err cmd-map)))

(defn report-all
  [cmd-maps]
  (doseq [cmd-map cmd-maps]
    (report cmd-map)))

(defn restart-services
  "Restarts the backend services, one-by-one"
  [host port ssh-user sudo-pass]
  (report-all 
    (remote-execute 
      host 
      port 
      ssh-user
      (service-restart "iplant-services" sudo-pass))))

(defn update-services
  "Updates the backend service."
  [host port ssh-user sudo-pass]
  (report-all
    (let [yu-part (partial yum-update sudo-pass)] 
      (remote-execute
        host
        port
        ssh-user
        (apply yu-part list-of-services)))))

(defn tagging-workflow
  "Checks out the repo, merges the dev branch into master, pushes up the 
   merged changes, tags the repo with the value in tag, and finally
   pushes up the tags."
  [repo tag]
  (report-all 
    (execute
      (git-clone repo)
      (git-checkout repo "master")
      (git-merge repo "master" "dev")
      (git-push repo)
      (git-tag repo tag)
      (git-push-tags repo))))

(defn merge-and-tag-repos
  "If passed only a tag, then it calls (tagging-workflow) on each of the
   repos in list-of-repos.

   If passed a tag and a list of repos, then it calls (tagging-workflow)
   on each of the repos passed in. You'll need to map full-repo-string
   on the list of repos that you pass in (or use full git repo URLs)."
  ([tag]
    (merge-and-tag-repos tag (mapv full-repo-string list-of-repos)))
  ([tag repos]
    (report-all (execute (clean)))
    (doseq [repo repos]
      (tagging-workflow repo))))

