(ns dingle.scripting
  (:use [pallet.stevedore]
        [clj-ssh.ssh])
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

(defmacro combine
  [& scripts]
  `(with-script-language :pallet.stevedore.bash/bash
     (do-script ~@scripts)))

(defmacro chain
  [& scripts]
  `(with-script-language :pallet.stevedore.bash/bash
     (chained-script ~@scripts)))

(defmacro checked
  [& scripts]
  `(with-script-language :pallet.stevedore.bash/bash
     (checked-script ~@scripts)))

(defn sudo-cmd
  [cmd pass]
  (str "echo " pass " | sudo -S " cmd))

(defn remote-execute
  [host port user pass cmd]
  (let [conn-str (str user "@" host)] 
    (execute
      (scriptify
        (ssh "-t" "-t" "-p" ~port ~conn-str ~cmd)))))