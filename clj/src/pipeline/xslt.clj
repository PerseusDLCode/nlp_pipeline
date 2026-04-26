(ns pipeline.xslt
  (:import [net.sf.saxon.s9api Processor XdmDestination]
           [javax.xml.transform.stream StreamSource]
           [java.io File])
  (:require [clojure.java.io :as io]
            [clojure.pprint :as pprint]
            [clojure.string :as string]
            [babashka.fs :as fs]))

(def ^Processor processor (Processor. false))

(defn compile-stylesheet
  [^String path]
  (-> processor
      .newXsltCompiler
      (.compile (StreamSource. (File. path)))))

(defn run-transform
  [executable source]
  (let [transformer (.load executable)
        dest        (XdmDestination.)]
    (doto transformer
      (.setSource source)
      (.setDestination dest)
      .transform)
    (.getXdmNode dest)))

(defn serialize-to-file
  [node ^String output-path]
  (pprint/pprint output-path)
  (.serializeNode (.newSerializer processor (File. output-path)) node))

(defn standoff-filename
  [^File f]
  (let [basename (.getName f)
        without-ext (first (fs/split-ext basename))
        parent (.getParent f)]
    (str parent "/" without-ext ".standoff.xml")))

(defn run-pipeline
  [input-path]
  (let [xslt-dir "resources/xslt"
        number-transformer (compile-stylesheet (str xslt-dir "/number-annotations.xsl"))
        standoff-transformer (compile-stylesheet (str xslt-dir "/inline-to-standoff.xsl"))]
    (for [f (filter #(and
                      (.isFile %)
                      (string/ends-with? (str %) ".xml")
                      (not (string/ends-with? (str %) "__cts__.xml")))
                    (file-seq (io/file input-path)))
          :let  [numbered (run-transform number-transformer (StreamSource. f))
                 result (run-transform standoff-transformer (.asSource numbered))
                 output-path (standoff-filename f)]]
      (serialize-to-file result output-path))))

(defn -main [& args]
  (when (not= (count args) 1)
    (println "Usage: pipeline <input-path>")
    (System/exit 1))
  (let [[input-path] args]
    (run-pipeline input-path)))