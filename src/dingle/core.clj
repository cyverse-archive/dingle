(ns dingle.core
  (:use [dingle.scripting] 
        [dingle.git]
        [dingle.services]
        [dingle.jenkins]
        [slingshot.slingshot :only [try+ throw+]])
  (:require [clojure.string :as string]
            [clojure.java.io :as io]
            [clojure-commons.file-utils :as ft]))

(defn err
  [err-str]
  {:error err-str})

(def config (atom nil))

(defn load-configuration
  [config-file]
  (when-not (.exists (io/file config-file))
    (throw+ (err (str "Config " config-file " doesn't exist."))))
  
  (try+
    (load-file config-file)
    (catch Exception e
      (throw (Exception. "Error loading config file."))))
  
  (let [config (resolve 'dingle.config/config)]
    (when-not config
      (throw+ (err (str "Couldn't resolve 'dingle.config/config from " config-file))))
    config))

(defn configure
  ([]
    (configure (ft/path-join (System/getProperty "user.home") ".dingle/config.clj")))
  ([config-file]
    (reset! config @(load-configuration config-file))
    nil))

(defn full-repo-string
  "Prepends git URL to the name of the repo. Use with list-of-repos."
  [repo]
  (str (:github-base-url @config) repo))

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
  [host port]
  (remote-execute 
    host 
    port 
    (:ssh-user @config)
    (service-restart "iplant-services" (:sudo-password @config))))

(defn update-services
  "Updates the backend service."
  [host port]
  (let [yu-part (partial yum-update (:sudo-password @config))] 
    (remote-execute
      host
      port
      (:ssh-user @config)
      (apply yu-part (:list-of-services @config)))))

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

(defn merge-and-tag-prereqs
  [tag]
  (doseq [repo (mapv full-repo-string (:prereq-repos @config))]
    (report-all (tagging-workflow repo tag))))

(defn build-prereqs
  []
  (doseq [job (:prereq-jobs @config)]
    (report-all 
      (trigger-job 
        (:jenkins-url @config)
        job
        (:jenkins-token @config)))))

(defn merge-and-tag-repos
  "If passed only a tag, then it calls (tagging-workflow) on each of the
   repos in list-of-repos.

   If passed a tag and a list of repos, then it calls (tagging-workflow)
   on each of the repos passed in. You'll need to map full-repo-string
   on the list of repos that you pass in (or use full git repo URLs)."
  ([tag]
    (merge-and-tag-repos tag (mapv full-repo-string (:list-of-repos @config))))
  ([tag repos]
    (report-all (execute (clean)))
    (doseq [repo repos]
      (tagging-workflow repo))))

