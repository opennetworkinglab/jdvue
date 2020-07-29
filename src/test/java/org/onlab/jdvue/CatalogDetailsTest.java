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

import org.junit.Test;

import java.io.IOException;

import static java.util.Arrays.asList;
import static org.junit.Assert.assertEquals;

/**
 * Unit tests for {@link CatalogDetails}.
 */
public class CatalogDetailsTest {
    private static final String CAT_BASE = "src/test/resources/non_maven_cat";

    private static final String[] EXP_PKGSRC = {
            "Pcom.foobar.model",
            "SMagicBean",
            "SMagicBeanTest",
            "SPlantPot",
            "Pcom.foobar.util",
            "SBadUtils",
            "SMathUtils",
            "SStringUtils",
            "Pcom.foobar.view",
            "SBeanViewer",
            "SBeanViewerTest",
    };

    private static final String[] EXP_DEPS = {
            "D0.0>1.2",
            "D0.0>1.1",
            "D0.2>1.1",
            "D1.0>2.0",
            "D2.0>0.0",
            "D2.0>0.2",
            "D2.1>0.0",
            "D2.1>0.2",
    };

    private static final String[] EXP_CYCS = {
            "C0}1}2}",
    };

    @Test
    public void basics() throws IOException {
        Catalog cat = new Catalog(CAT_BASE);
        cat.load();
        cat.analyze();
        // basic assertions about the catalog
        assertEquals("incorrect package count", 3, cat.getPackages().size());
        assertEquals("incorrect source count", 8, cat.getSources().size());
        assertEquals("incorrect segment count", 3, cat.getCycleSegments().size());
        assertEquals("incorrect cycle count", 1, cat.getCycles().size());

        // generate the encoded data
        CatalogDetails deets = new CatalogDetails(cat);
        assertEquals("Bad package source encoding", asList(EXP_PKGSRC), deets.getEncPackageSources());
        assertEquals("Bad encoded dependencies", asList(EXP_DEPS), deets.getEncDependencies());
        assertEquals("Bad encoded cycles", asList(EXP_CYCS), deets.getEncCycles());

        // let's write the output file (but we aren't asserting against it)
        deets.writeDetails();
    }
}
