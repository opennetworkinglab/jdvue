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

import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * Able to create a compact text file containing data pertaining to an analyzed {@link Catalog}.
 */
public class CatalogDetails {
    private static final String DATA_EXT = ".data";
    private static final String COMMENT_CHAR = ";";
    private static final String PACKAGE_CHAR = "P";
    private static final String SOURCE_CHAR = "S";
    private static final String DEP_CHAR = "D";
    private static final String DEP_ARROW_CHAR = ">";
    private static final String CYCLE_CHAR = "C";
    private static final String CYCLE_ARROW_CHAR = "}";

    private final Catalog cat;
    private final String dataFileName;

    private final Map<JavaPackage, Integer> packageCodes = new HashMap<>();
    private final Map<JavaPackage, Map<JavaSource, Integer>> sourceCodes = new HashMap<>();

    private List<JavaPackage> sortedPackages;
    private final Map<JavaPackage, List<JavaSource>> sortedSources = new HashMap<>();

    private final List<String> encPackageSources = new ArrayList<>();
    private final List<String> encDependencies = new ArrayList<>();
    private final List<String> encCycles = new ArrayList<>();

    private FileWriter fw;

    /**
     * Wraps a catalog in a detail writer.
     *
     * @param cat the catalog
     */
    public CatalogDetails(Catalog cat) {
        this.cat = cat;
        this.dataFileName = cat.basePath() + DATA_EXT;
        sortPackages();
        encodeData();
    }

    private void sortPackages() {
        sortedPackages = getSortedPackages();

        for (JavaPackage p : sortedPackages) {
            int nextCode = packageCodes.size();
            packageCodes.put(p, nextCode);

            sortSources(p);
        }
    }

    private void sortSources(JavaPackage p) {
        // Sort sources by name, even though they don't implement Comparable
        List<JavaSource> sortedSrcs = getSortedSources(p);
        sortedSources.put(p, sortedSrcs);

        Map<JavaSource, Integer> srcMap = sourceCodes.computeIfAbsent(p, k -> new HashMap<>());

        for (JavaSource s : sortedSrcs) {
            int nextCode = srcMap.size();
            srcMap.put(s, nextCode);
        }
    }

    private List<JavaPackage> getSortedPackages() {
        // Sort packages by name, even though they don't implement Comparable
        List<JavaPackage> sortedPkgs = cat.getPackages().stream()
                .map(JavaEntity::name)
                .sorted()
                .map(cat::getPackage)
                .collect(Collectors.toList());
        return Collections.unmodifiableList(sortedPkgs);
    }

    private List<JavaSource> getSortedSources(JavaPackage pkg) {
        // Sort sources by name, even though they don't implement Comparable
        List<JavaSource> sortedSrcs = pkg.getSources().stream()
                .map(JavaEntity::name)
                .sorted()
                .map(cat::getSource)
                .collect(Collectors.toList());
        return Collections.unmodifiableList(sortedSrcs);
    }

    private String leafName(String dottedName) {
        int ri = dottedName.lastIndexOf(".");
        return ri >= 0 ? dottedName.substring(ri + 1) : dottedName;
    }

    private void encodeData() {
        encodePackages();
        encodeDependencies();
        encodeCycles();
    }

    private void encodePackages() {
        for (JavaPackage p : sortedPackages) {
            encodePackage(p);
        }
    }

    private void encodePackage(JavaPackage p) {
        encPackageSources.add(PACKAGE_CHAR + p.name());
        List<JavaSource> srcs = sortedSources.get(p);
        for (JavaSource s : srcs) {
            encPackageSources.add(SOURCE_CHAR + leafName(s.name()));
        }
    }

    private void encodeDependencies() {
        for (JavaPackage p : sortedPackages) {
            encodeDependencies(p);
        }
    }

    private void encodeDependencies(JavaPackage p) {
        for (JavaSource s : sortedSources.get(p)) {
            encodeDependencies(s);
        }
    }

    private void encodeDependencies(JavaSource src) {
        for (JavaEntity imp : src.getImports()) {
            JavaSource tgt = (JavaSource) imp;
            encDependencies.add(DEP_CHAR + coded(src) + DEP_ARROW_CHAR + coded(tgt));
        }
    }

    private void encodeCycles() {
        for (DependencyCycle cycle : cat.getCycles()) {
            encCycles.add(CYCLE_CHAR + encodeCycleAsString(cycle));
        }

    }

    private String encodeCycleAsString(DependencyCycle cycle) {
        StringBuilder sb = new StringBuilder();
        for (JavaPackage p: cycle.getCycle()) {
            sb.append(coded(p)).append(CYCLE_ARROW_CHAR);
        }
        return sb.toString();
    }

    private String coded(JavaPackage p) {
        return packageCodes.get(p).toString();
    }

    private String coded(JavaSource s) {
        JavaPackage p = s.getPackage();
        String sCodeStr = sourceCodes.get(p).get(s).toString();
        return coded(p) + "." + sCodeStr;
    }


    // for unit testing access

    List<String> getEncPackageSources() {
        return Collections.unmodifiableList(encPackageSources);
    }

    List<String> getEncDependencies() {
        return Collections.unmodifiableList(encDependencies);
    }

    List<String> getEncCycles() {
        return Collections.unmodifiableList(encCycles);
    }


    public void writeDetails() throws IOException {
        fw = new FileWriter(dataFileName);
        writeHeader();
        writeCodedBlock("Packages/Sources", encPackageSources);
        writeCodedBlock("Source Dependencies", encDependencies);
        writeCodedBlock("Package Cycles", encCycles);
        fw.close();
    }

    private void writeCodedBlock(String heading, List<String> encData) throws IOException {
        wrComment("");
        wrComment(heading);
        for (String data : encData) {
            writeLine(data);
        }
    }

    private void writeHeader() throws IOException {
        wrComment("Java Package Dependency Data");
        wrComment(new Date().toString());
        wrComment(dataFileName);
        wrComment("");
    }

    private void wrComment(String comment) throws IOException {
        writeLine(COMMENT_CHAR + comment);
    }

    private void writeLine(String line) throws IOException {
        fw.write(line + System.lineSeparator());
    }
}
