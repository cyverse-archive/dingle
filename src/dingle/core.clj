(ns dingle.core
  (:use [dingle.scripting] 
        [dingle.git]
        [dingle.services]
        [dingle.jenkins]
        [dingle.scm]
        [slingshot.slingshot :only [try+ throw+]])
  (:require [clojure.string :as string]
            [clojure.java.io :as io]
            [clojure-commons.file-utils :as ft]
            [dingle.rpms :as rpms]
            [clojure.set :as set]))

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
  "Build the prereq jobs."
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

(defn list-latest-rpms
  "Lists the filename of the latest version of the RPMs in the :rpm-names
   list in the config.

   Params:
     host - The host to connect to to do the listing. String.
     port - The port to connect on. Integer.
     user - The user to connect as. String.
     rpm-dir - The config key of the directory to look in on the remote machine

   Returns a list of the RPM filenames."
  [rpm-dir]
  (let [full-dir (ft/path-join (:rpm-base-dir @config) (get @config rpm-dir))
        host     (:rpm-host @config)
        port     (:rpm-host-port @config)
        user     (:rpm-host-user @config)]
    (mapv 
      #(rpms/latest-rpm host port user %1 full-dir)
      (:rpm-names @config))))

(defn new-qa-rpms
  "Returns a sequence of hash-maps telling which RPMs would be copied to QA
   if you to run (push-rpms-to-qa)."
  []
  (let [dev-dir (ft/path-join (:rpm-base-dir @config) 
                              (:rpm-dev-dir @config))
        qa-dir  (ft/path-join (:rpm-base-dir @config)
                              (:rpm-qa-dir @config))
        host    (:rpm-host @config)
        port    (:rpm-host-port @config)
        user    (:rpm-host-user @config)]
    (into [] 
      (set/difference 
        (set (list-latest-rpms :rpm-dev-dir))
        (set (list-latest-rpms :rpm-qa-dir))))))

(defn print-new-qa-rpms
  "Convenience function that will print off the filenames of the RPMs that
   would be pushed to QA if you were to run (push-rpms-to-qa)."
  []
  (doseq [rpm-map (new-qa-rpms)]
    (println (rpms/rpm-map->rpm-name rpm-map))))

(defn copy-rpms-to-qa
  "Copies new RPMs to QA and updates the yum repository."
  []
  (let [host      (:rpm-host @config)
        port      (:rpm-host-port @config)
        user      (:rpm-host-user @config)
        sudo-pass (:sudo-pass @config)
        dev-dir   (ft/path-join (:rpm-base-dir @config) 
                                (:rpm-dev-dir @config))
        qa-dir    (ft/path-join (:rpm-base-dir @config)
                                (:rpm-qa-dir @config))]
    (report-all
      (mapv
        #(rpms/copy-rpm host port user sudo-pass % dev-dir qa-dir)
        (new-qa-rpms)))
    
    (report-all 
      (rpms/createrepo host port user sudo-pass qa-dir "root:www"))))

(defn setup-scm
  "Downloads and extracts the scm bundle into the working directory."
  [scm-url]
  (clj-execute
    (script-setup-scm scm-url (:scm-working-dir @config))))

(defn run-export-tool
  "Runs export tools from the latest built scm tarball against a deployed 
   version of the DE.

   When this function exits, you should have a screen session named
   'export-tool' running in the background. When that session is complete
   you can run the (run-import-tool) function safely.

   Params:
     scm-url - Full URL to the scm tarball to use.
     source - Version of the source DE."
  [source]
  (future
    (let [de-host     (:de-host @config)
          de-port     (:de-port @config)
          working-dir (:scm-working-dir @config)]
      (clj-execute
        (script-run-export-tool working-dir de-host de-port source)))))

(defn run-import-tool
  "Runs import-tools.py from the latest built scm tarball against a
   deployed version of the DE."
  [dest]
  (future
    (let [de-host     (:de-host @config)
          de-port     (:de-port @config)
          working-dir (:scm-working-dir @config)] 
      (clj-execute
        (script-run-import-tool working-dir de-host de-port dest)))))

(defn run-export-analyses
  "Runs export-analyses.py from the latest built scm tarball against a
   deployed version of the DE."
  [dest]
  (future
    (let [de-host     (:de-host @config)
          de-port     (:de-port @config)
          working-dir (:scm-working-dir @config)] 
      (clj-execute
        (script-run-export-analyses working-dir de-host de-port dest)))))

(defn run-import-analyses
  "Runs import-analyses.py against a deployed version of the DE."
  [dest]
  (future
    (let [de-host     (:de-host @config)
          de-port     (:de-port @config)
          working-dir (:scm-working-dir @config)] 
      (clj-execute
        (script-run-import-analyses working-dir de-host de-port dest)))))

