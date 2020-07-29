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

import java.io.IOException;

/**
 * Generator of a self-contained HTML file which serves as a GUI for
 * visualizing Java package dependencies carried in the supplied catalog.
 *
 * The HTML file is an adaptation of D3.js Hierarchical Edge Bundling as
 * shown at http://bl.ocks.org/mbostock/7607999.
 *
 * @author Thomas Vachuska
 */
public class DependencyViewer {

    /**
     * Main program entry point.
     *
     * @param args command line arguments
     */
    public static void main(String[] args) {
        ProgArgs progArgs = new ProgArgs(args);

        Catalog cat = new Catalog(progArgs.catPath());
        try {
            cat.load();
            cat.analyze();
            System.err.println(cat);

            BundleView bundleView = new BundleView(cat);
            bundleView.dumpLongestCycle();
            bundleView.writeHTMLFile();

            if (progArgs.outputDetailData()) {
                new CatalogDetails(cat).writeDetails();
            }
        } catch (IOException e) {
            System.err.println("Unable to process catalog: " + e.getMessage());
        }
    }

}
