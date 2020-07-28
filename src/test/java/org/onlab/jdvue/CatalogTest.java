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

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;

/**
 * Unit test for the source catalog.
 *
 * @author Thomas Vachuska
 */
public class CatalogTest {

    @Test
    public void basics() throws IOException {
        Catalog cat = new Catalog();
        cat.load("src/test/resources/catalog.db");
        cat.analyze();

        assertEquals("incorrect package count", 12, cat.getPackages().size());
        assertEquals("incorrect source count", 14, cat.getSources().size());

        JavaPackage pkg = cat.getPackage("k");
        assertNotNull("package should be found", pkg);

        JavaSource src = cat.getSource("k.K");
        assertNotNull("source should be found", src);

        assertEquals("incorrect package source count", 1, pkg.getSources().size());
        assertEquals("incorrect package dependency count", 1, pkg.getDependencies().size());
        assertEquals("incorrect package cycle count", 3, cat.getPackageCycles(pkg).size());

        assertEquals("incorrect segment count", 11, cat.getCycleSegments().size());
        assertEquals("incorrect cycle count", 5, cat.getCycles().size());
    }

    @Test
    public void nonMavenCat() throws IOException {
        Catalog cat = new Catalog();
        cat.load("src/test/resources/non_maven_cat.db");
        cat.analyze();

        assertEquals("incorrect package count", 3, cat.getPackages().size());
        assertEquals("incorrect source count", 8, cat.getSources().size());

        JavaPackage pkg = cat.getPackage("com.foobar.model");
        assertNotNull("package should be found", pkg);

        JavaSource src = cat.getSource("com.foobar.model.MagicBean");
        assertNotNull("source should be found", src);

        assertEquals("incorrect package source count", 3, pkg.getSources().size());
        assertEquals("incorrect package dependency count", 1, pkg.getDependencies().size());
        assertEquals("incorrect package cycle count", 1, cat.getPackageCycles(pkg).size());

        assertEquals("incorrect segment count", 3, cat.getCycleSegments().size());
        assertEquals("incorrect cycle count", 1, cat.getCycles().size());
    }

    @Test
    public void abcCatNormal() throws IOException {
        Catalog cat = new Catalog();
        cat.load("src/test/resources/abc_cat_normal.db");
        cat.analyze();

        assertEquals("incorrect package count", 4, cat.getPackages().size());
        assertEquals("incorrect source count", 4, cat.getSources().size());

        assertEquals("incorrect segment count", 3, cat.getCycleSegments().size());
        assertEquals("incorrect cycle count", 1, cat.getCycles().size());
    }

    @Test
    public void abcCatStatic() throws IOException {
        /*
            Verify that static imports are correctly parsed to return the "source" name (not the "method" name)...

            src/com/foobar/loop/alpha/Aaa.java:package com.foobar.loop.alpha;
            src/com/foobar/loop/alpha/Aaa.java:import static com.foobar.loop.beta.Bbb.returnCodeB;
                                               ^^^^^^        ^^^^^^^^^^^^^^^^^^^^^^^^
         */
        Catalog cat = new Catalog();
        cat.load("src/test/resources/abc_cat_static.db");
        cat.analyze();

        assertEquals("incorrect package count", 4, cat.getPackages().size());
        assertEquals("incorrect source count", 4, cat.getSources().size());

        assertEquals("incorrect segment count", 3, cat.getCycleSegments().size());
        assertEquals("incorrect cycle count", 1, cat.getCycles().size());
    }
}
