(ns dingle.rpms
  (:use [dingle.scripting])
  (:require [clojure.string :as string]))

(defn exec-list-rpms
  "Uses (remote-execute) to return a listing of RPM information from yum-path."
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
  "Access 'host' on 'port' as 'user' and returns a listing of RPM information
   for RPMs that start with 'rpm-name' in the 'yum-path' directory.

   Params:
     host - String containing the hostname to ssh to.
     port - The ssh port for the host. Usually 22. Should be an integer.
     user - The user to ssh in as. Must have passwordless ssh set up. String.
     rpm-name - String containing the name of the rpm to look for.
     yum-path - The path to the directory on host that contains RPMs. String.

   Returns:
     A sequence of maps in the format:
     [
         {
             :name \"RPM name\"
             :version \"RPM version\"
             :release \"RPM release number\"
             :arch \"RPM architecture\"
         }
     ]
  "
  [host port user rpm-name yum-path]
  (let [rpm-listing (exec-list-rpms host port user rpm-name yum-path)]
    (mapv
      #(zipmap [:name :version :release :arch] (string/split % #"\t"))
      (map 
        string/trim 
        (filter 
          #(not (string/blank? %)) 
          (string/split rpm-listing #"\n"))))))
