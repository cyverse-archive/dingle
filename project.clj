(defproject dingle "0.1.0-SNAPSHOT"
  :description "FIXME: write description"
  :url "http://example.com/FIXME"
  :license {:name "Eclipse Public License"
            :url "http://www.eclipse.org/legal/epl-v10.html"}
  :dependencies [[org.clojure/clojure "1.5.1"]
                 [org.clojure/tools.cli "0.3.1"]
                 [org.iplantc/clojure-commons "1.4.7"]
                 [org.cloudhoist/stevedore "0.8.0-alpha.1"]
                 [clj-ssh "0.5.7"]
                 [slingshot "0.10.3"]
                 [com.cemerick/url "0.1.0"]
                 [org.eclipse.jgit/org.eclipse.jgit "2.0.0.201206130900-r"]]
  :repositories {"sonatype"
                 "http://oss.sonatype.org/content/repositories/releases"
                 "iplantCollaborative"
                 "http://projects.iplantcollaborative.org/archiva/repositories/internal"
                 "jgit-repo"
                 "http://download.eclipse.org/jgit/maven"}
  :aot [dingle.core]
  :main dingle.core
  :min-lein-version "2.0.0")
