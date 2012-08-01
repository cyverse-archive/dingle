(ns dingle.jenkins
  (:use [dingle.scripting]
        [cemerick.url])
  (:require [clojure-commons.file-utils :as ft]))

(defn jenkins-job-url
  [jenkins-url job-name jenkins-token]
  (str (-> (url jenkins-url "job" job-name "build")
         (assoc :query {:token jenkins-token}))))

(defn trigger-job
  "Uses curl to do a GET request against a Jenkins URL, triggering a build."
  [jenkins-url job-name jenkins-token]
  (let [full-jurl (jenkins-job-url jenkins-url job-name jenkins-token)]
    (scriptify
      (curl ~full-jurl))))