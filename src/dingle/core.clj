(ns dingle.core
  (:use [dingle.git]))

(defn full-repo-string
  [repo]
  (str "git@github.com:iPlantCollaborativeOpenSource/" repo))

(def list-of-repos
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

(defn workflow
  [repo tag]
  (execute
    (git-clone repo)
    (git-checkout repo "master")
    (git-merge repo "master" "dev")
    (git-push repo)
    (git-tag repo tag)
    (git-push-tags repo)))

(defn dingle
  [tag]
  (let [repos (mapv full-repo-string list-of-repos)]
    (execute (clean))
    
    (doseq [repo repos]
      (workflow repo))))

(defn -main
  [& args]
  (println "booyah"))
