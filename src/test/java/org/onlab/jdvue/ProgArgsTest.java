package org.onlab.jdvue;

import org.junit.Test;

import static org.junit.Assert.*;

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
//        System.out.println(pa);

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
//        System.out.println(pa);

        assertEquals("wrong catalog path", CAT_PATH, pa.catPath());
        assertTrue("DA flag should be true", pa.dumpAnalysis());
    }

    @Test
    public void otherFlag() {
        ProgArgs pa = new ProgArgs(new String[]{CAT_PATH, OTHER_FLAG});
//        System.out.println(pa);

        assertEquals("wrong catalog path", CAT_PATH, pa.catPath());
        assertFalse("DA flag should be false", pa.dumpAnalysis());
    }
}
