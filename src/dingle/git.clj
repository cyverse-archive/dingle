(ns dingle.git
  (:use [pallet.stevedore])
  (:require [pallet.common.shell :as sh]
            [pallet.stevedore.bash :as bash]
            [clojure-commons.file-utils :as ft]
            [clojure.string :as string])
  (:import [java.io File]))

(def wdir "dingle")

(defn repo->dirname
  [repo]
  (ft/path-join wdir (string/replace (ft/basename repo) #"\.git" "")))

(defn execute
  [& scripts]
  (doseq [scr scripts] 
     (println (:out (sh/bash scr)))))

(defmacro scriptify
  [& body]
  `(with-script-language :pallet.stevedore.bash/bash
    (script ~@body)))

(defn clean
  []
  (scriptify
    (echo "Executing clean")
    (rm "-rf" ~wdir)))

(defn git-clone
  [repo]
  (scriptify
    (echo "Executing git-clone")
    (mkdir ~wdir)
    (pushd ~wdir)
    (echo (str "Cloning " ~repo))
    (git "clone" ~repo)
    (echo (str "Done cloning " ~repo))
    (popd)))

(defn git-checkout
  [repo gref]
  (let [repo-dir (repo->dirname repo)] 
    (scriptify
      (echo "Executing git-checkout")
      (pushd ~repo-dir)
      (echo (str "Checking out " ~gref " in " ~repo-dir))
      (git "checkout" ~gref)
      (popd))))

(defn git-merge
  [repo to-branch from-branch]
  (let [repo-dir (repo->dirname repo)]
    (scriptify
      (echo "Executing git-merge")
      (pushd ~repo-dir)
      (echo (str "Merging " ~from-branch " into " ~to-branch))
      (git merge ~from-branch)
      (echo (str "Done merging " ~from-branch " into " ~to-branch))
      (popd))))

(defn git-push
  [repo]
  (let [repo-dir (repo->dirname repo)]
    (scriptify
      (echo "Executing git-push")
      (echo (str "Pushing from " repo-dir))
      (pushd ~repo-dir)
      (git push)
      (popd))))

(defn git-tag
  [repo tag]
  (let [repo-dir (repo->dirname repo)]
    (scriptify
      (echo "Executing git-tag")
      (echo (str "Tagging " repo-dir " with " tag))
      (pushd ~repo-dir)
      (git tag ~tag)
      (popd))))

(defn git-push-tags
  [repo]
  (let [repo-dir (repo->dirname repo)]
    (scriptify
      (echo "Executing git-push-tags")
      (echo (str "Pushing from " repo-dir))
      (pushd ~repo-dir)
      (git push --tags)
      (popd))))



