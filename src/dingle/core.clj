(ns dingle.core
  (:use [dingle.git]))

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

(defn tagging-workflow
  "Checks out the repo, merges the dev branch into master, pushes up the 
   merged changes, tags the repo with the value in tag, and finally
   pushes up the tags."
  [repo tag]
  (execute
    (git-clone repo)
    (git-checkout repo "master")
    (git-merge repo "master" "dev")
    (git-push repo)
    (git-tag repo tag)
    (git-push-tags repo)))

(defn dingle
  "If passed only a tag, then it calls (tagging-workflow) on each of the
   repos in list-of-repos.

   If passed a tag and a list of repos, then it calls (tagging-workflow)
   on each of the repos passed in. You'll need to map full-repo-string
   on the list of repos that you pass in (or use full git repo URLs)."
  ([tag]
    (dingle tag (mapv full-repo-string list-of-repos)))
  ([tag repos]
    (execute (clean))
    (doseq [repo repos]
      (tagging-workflow repo))))

