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

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

/**
 * Unit tests for program arguments object.
 */
public class ProgArgsTest {

    private static final String CAT_PATH = "somepath/somecat";
    private static final String DUMP_FLAG = "-d";
    private static final String OTHER_FLAG = "-o";

    @Test
    public void basics() {
        ProgArgs pa = new ProgArgs(new String[]{CAT_PATH});

        assertEquals("wrong catalog path", CAT_PATH, pa.catPath());
        assertFalse("DA flag should be false", pa.dumpAnalysis());
    }

    @Test(expected = IllegalArgumentException.class)
    public void noArgs() {
        new ProgArgs(new String[]{});
    }

    @Test
    public void dumpFlag() {
        ProgArgs pa = new ProgArgs(new String[]{CAT_PATH, DUMP_FLAG});

        assertEquals("wrong catalog path", CAT_PATH, pa.catPath());
        assertTrue("DA flag should be true", pa.dumpAnalysis());
    }

    @Test
    public void otherFlag() {
        ProgArgs pa = new ProgArgs(new String[]{CAT_PATH, OTHER_FLAG});

        assertEquals("wrong catalog path", CAT_PATH, pa.catPath());
        assertFalse("DA flag should be false", pa.dumpAnalysis());
    }
}
