/*
 * Copyright 2015-present Open Networking Laboratory
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.onlab.jdvue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectWriter;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.io.FileWriter;
import java.io.IOException;
import java.util.Set;

/**
 * Able to create a "Hierarchical Edge Bundling" view from an analyzed {@link Catalog}.
 */
public class BundleView extends AbstractReportGenerator {

    private static final String HTML_EXT = ".html";

    private static final String INDEX = "index.html";
    private static final String D3JS = "d3.v3.min.js";

    private static final String TITLE_PLACEHOLDER = "TITLE_PLACEHOLDER";
    private static final String D3JS_PLACEHOLDER = "D3JS_PLACEHOLDER";
    private static final String DATA_PLACEHOLDER = "DATA_PLACEHOLDER";

    private final Catalog cat;

    /**
     * Wraps a catalog in a bundle view generator.
     *
     * @param cat the catalog
     */
    public BundleView(Catalog cat) {
        this.cat = cat;
    }

    /**
     * Prints out the longest cycle; just for kicks.
     */
    public void dumpLongestCycle() {
        DependencyCycle longest = null;
        for (DependencyCycle cycle : cat.getCycles()) {
            if (longest == null || longest.getCycleSegments().size() < cycle.getCycleSegments().size()) {
                longest = cycle;
            }
        }

        if (longest != null) {
            for (Dependency dependency : longest.getCycleSegments()) {
                System.out.println(dependency);
            }
        }
    }

    /**
     * Writes the HTML visualization of the catalog file.
     *
     * @throws IOException if issues encountered writing the HTML file
     */
    public void writeHTMLFile() throws IOException {
        String base = cat.basePath();
        String htmlFile = base + HTML_EXT;

        String index = getResourceAsString(INDEX);
        String d3js = getResourceAsString(D3JS);

        FileWriter fw = new FileWriter(htmlFile);
        ObjectWriter writer = new ObjectMapper().writer(); // .writerWithDefaultPrettyPrinter();
        fw.write(index.replace(TITLE_PLACEHOLDER, base)
                .replace(D3JS_PLACEHOLDER, d3js)
                .replace(DATA_PLACEHOLDER, writer.writeValueAsString(toJson())));
        fw.close();
    }

    // Produces a JSON structure designed to drive the hierarchical visual
    // representation of Java package dependencies and any dependency cycles
    private JsonNode toJson() {
        ObjectMapper mapper = new ObjectMapper();
        ObjectNode root = mapper.createObjectNode();
        root.put("packages", jsonPackages(mapper));
        root.put("cycleSegments", jsonCycleSegments(mapper, cat.getCycleSegments()));
        root.put("summary", jsonSummary(mapper));
        return root;
    }

    // Produces a JSON summary of dependencies
    private JsonNode jsonSummary(ObjectMapper mapper) {
        ObjectNode summary = mapper.createObjectNode();
        summary.put("packages", cat.getPackages().size());
        summary.put("sources", cat.getSources().size());
        summary.put("cycles", cat.getCycles().size());
        summary.put("cycleSegments", cat.getCycleSegments().size());
        return summary;
    }

    // Produces a JSON structure with package dependency data
    private JsonNode jsonPackages(ObjectMapper mapper) {
        ArrayNode packages = mapper.createArrayNode();
        for (JavaPackage javaPackage : cat.getPackages()) {
            packages.add(json(mapper, javaPackage));
        }
        return packages;
    }

    // Produces a JSON structure with all cyclic segments
    private JsonNode jsonCycleSegments(ObjectMapper mapper,
                                       Set<Dependency> segments) {
        ObjectNode cyclicSegments = mapper.createObjectNode();
        for (Dependency dependency : segments) {
            String s = dependency.getSource().name();
            String t = dependency.getTarget().name();
            cyclicSegments.put(t + "-" + s,
                    mapper.createObjectNode().put("s", s).put("t", t));
        }
        return cyclicSegments;
    }

    // Produces a JSON object structure describing the specified Java package.
    private JsonNode json(ObjectMapper mapper, JavaPackage javaPackage) {
        ObjectNode node = mapper.createObjectNode();

        ArrayNode imports = mapper.createArrayNode();
        for (JavaPackage dependency : javaPackage.getDependencies()) {
            imports.add(dependency.name());
        }

        Set<DependencyCycle> packageCycles = cat.getPackageCycles(javaPackage);
        Set<Dependency> packageCycleSegments = cat.getPackageCycleSegments(javaPackage);

        node.put("name", javaPackage.name());
        node.put("size", javaPackage.getSources().size());
        node.put("imports", imports);
        node.put("cycleSegments", jsonCycleSegments(mapper, packageCycleSegments));
        node.put("cycleCount", packageCycles.size());
        node.put("cycleSegmentCount", packageCycleSegments.size());
        return node;
    }

}
