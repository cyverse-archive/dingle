(ns dingle.rpms
  (:use [dingle.scripting]
        [dingle.core :only [config]])
  (:require [clojure.string :as string]
            [clojure-commons.file-utils :as ft]))

(defn exec-list-rpms
  [host port user rpm-name yum-path]
  (let [search-str (str rpm-name "*.rpm")] 
    (:out 
      (first 
        (remote-execute
          host
          port
          user
          (scriptify 
            (cd ~yum-path) 
            (rpm -qp --qf "\"%{name}\\t%{version}\\t%{release}\\t%{arch}\\n\"" ~search-str)))))))

(defn list-rpms
  [host port user rpm-name yum-path]
  (let [rpm-listing (exec-list-rpms host port user rpm-name yum-path)]
    (mapv
      #(zipmap [:name :version :release :arch] (string/split % #"\t"))
      (map 
        string/trim 
        (filter 
          #(not (string/blank? %)) 
          (string/split rpm-listing #"\n"))))))
