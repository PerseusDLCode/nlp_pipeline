<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet
    version="3.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    xpath-default-namespace="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="tei">

  <xsl:output method="xml" indent="yes" encoding="UTF-8"/>

  <!-- identity transform -->
  <xsl:template match="@* | node()">
    <xsl:copy>
      <xsl:apply-templates select="@* | node()"/>
    </xsl:copy>
  </xsl:template>

  <!-- deep-copy teiHeader unchanged so its <foreign>, <persName> etc.
       are not matched by the inline-annotation templates below -->
  <xsl:template match="teiHeader">
    <xsl:copy-of select="."/>
  </xsl:template>

  <!-- root: emit teiHeader, then text (with anchors), then standOff -->
  <xsl:template match="TEI">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <xsl:apply-templates select="teiHeader"/>
      <xsl:apply-templates select="text"/>
      <standOff xmlns="http://www.tei-c.org/ns/1.0">
        <listAnnotation type="inline">
          <xsl:apply-templates
              select=".//text//del
                      | .//text//mentioned
                      | .//text//foreign
                      | .//text//hi"
              mode="to-annotation"/>
        </listAnnotation>
        <listAnnotation type="milestones">
          <xsl:apply-templates select=".//text//milestone" mode="to-annotation"/>
        </listAnnotation>
        <!-- glosses are moved here wholesale; the body template suppresses them -->
        <listAnnotation type="glosses">
          <xsl:apply-templates select=".//text//gloss" mode="to-annotation"/>
        </listAnnotation>
      </standOff>
    </xsl:copy>
  </xsl:template>

  <!-- ============================================================
       mode="to-annotation": build standOff records from input elements
  ============================================================ -->

  <xsl:template match="del | mentioned | foreign | hi" mode="to-annotation">
    <annotation xmlns="http://www.tei-c.org/ns/1.0"
                xml:id="ann-{@xml:id}"
                target="#{@xml:id}-s #{@xml:id}-e"
                type="{local-name()}">
      <xsl:copy-of select="@*[name() != 'xml:id']"/>
    </annotation>
  </xsl:template>

  <xsl:template match="milestone" mode="to-annotation">
    <annotation xmlns="http://www.tei-c.org/ns/1.0"
                xml:id="ann-{@xml:id}"
                target="#{@xml:id}"
                type="milestone">
      <xsl:copy-of select="@*[name() != 'xml:id']"/>
    </annotation>
  </xsl:template>

  <!-- copy the full gloss element verbatim so its inner markup is preserved -->
  <xsl:template match="gloss" mode="to-annotation">
    <xsl:copy-of select="."/>
  </xsl:template>

  <!-- ============================================================
       body transforms: inline elements → anchor pairs or suppressed
  ============================================================ -->

  <xsl:template match="del | mentioned | foreign | hi">
    <anchor xmlns="http://www.tei-c.org/ns/1.0" xml:id="{@xml:id}-s"/>
    <xsl:apply-templates select="node()"/>
    <anchor xmlns="http://www.tei-c.org/ns/1.0" xml:id="{@xml:id}-e"/>
  </xsl:template>

  <!-- suppress gloss from body; content lives in standOff -->
  <xsl:template match="gloss"/>

  <xsl:template match="milestone">
    <anchor xmlns="http://www.tei-c.org/ns/1.0" xml:id="{@xml:id}"/>
  </xsl:template>

</xsl:stylesheet>
