(ns pipeline.xslt
  (:import [net.sf.saxon.s9api Processor XdmDestination]
           [javax.xml.transform.stream StreamSource]
           [java.io File]))

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
  (.serializeNode (.newSerializer processor (File. output-path)) node))

(defn run-pipeline
  [xslt-dir input-path output-path]
  (let [number-transformer (compile-stylesheet (str xslt-dir "/number-annotations.xsl"))
        standoff-transformer (compile-stylesheet (str xslt-dir "/inline-to-standoff.xsl"))
        numbered (run-transform number-transformer (StreamSource. (File. input-path)))
        result (run-transform standoff-transformer (.asSource numbered))]
    (serialize-to-file result output-path)))

(defn -main [& args]
  (when (not= (count args) 3)
    (println "Usage: pipeline <xslt-dir> <input-path> <output-path>")
    (System/exit 1))
  (let [[xslt-dir input-path output-path] args]
    (run-pipeline xslt-dir input-path output-path)))