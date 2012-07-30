(ns dingle.scripting
  (:use [pallet.stevedore]
        [clj-ssh.cli])
  (:require [pallet.common.shell :as sh]
            [pallet.stevedore.bash :as bash]))

(defn execute
  [& scripts]
  (for [scr scripts] 
     (sh/bash scr)))

(defmacro scriptify
  [& body]
  `(with-script-language :pallet.stevedore.bash/bash
    (script ~@body)))

(defn remote-execute
  [host port user pass & scripts]
  (for [scr scripts]
    (ssh host scr 
         :port port 
         :username user 
         :password pass 
         :strict-host-key-checking :no)))