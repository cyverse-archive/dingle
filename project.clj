(defproject dingle "0.1.0-SNAPSHOT"
  :description "FIXME: write description"
  :url "http://example.com/FIXME"
  :license {:name "Eclipse Public License"
            :url "http://www.eclipse.org/legal/epl-v10.html"}
  :dependencies [[org.clojure/clojure "1.4.0"]
                 [org.clojure/tools.cli "0.2.1"]
                 [org.iplantc/clojure-commons "1.2.0-SNAPSHOT"]
                 [org.cloudhoist/stevedore "0.7.2"]]
  :repositories {"sonatype"
                 "http://oss.sonatype.org/content/repositories/releases"}
  :aot [dingle.core]
  :main dingle.core
  :min-lein-version "2.0.0")
