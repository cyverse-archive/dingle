(ns dingle.jenkins
  (:use [dingle.scripting]
        [cemerick.url])
  (:require [clojure-commons.file-utils :as ft]
            [clojure.data.json :as json]))

(defn jenkins-job-url
  [jenkins-url job-name jenkins-token]
  (str (-> (url jenkins-url "job" job-name "build")
         (assoc :query {:token jenkins-token}))))

(defn jenkins-lastbuild-url
  [jenkins-url job-name]
  (str (url jenkins-url "job" job-name "lastBuild/api/json")))

(defn trigger-job
  "Uses curl to do a GET request against a Jenkins URL, triggering a build."
  [jenkins-url job-name jenkins-token]
  (let [full-jurl (jenkins-job-url jenkins-url job-name jenkins-token)]
    (execute
      (scriptify
        (curl ~full-jurl)))))

(defn build-running?
  [jenkins-url job-name]
  (let [full-jurl (jenkins-lastbuild-url jenkins-url job-name)]
    (:building
      (json/read-json
        (:out 
          (first
            (execute
              (scriptify
                (curl ~full-jurl)))))))))