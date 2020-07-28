package org.onlab.jdvue;

/**
 * Encapsulates the command line arguments for the Dependency Viewer.
 */
public class ProgArgs {
    private static final String USAGE = "Expected Args: <catalog path> [-d]";
    private static final String DUMP_ANALYSIS_FLAG = "-d";

    private final String catPath;
    private final String asString;

    private boolean dumpAnalysis = false;

    public ProgArgs(String[] args) {
        if (args.length < 1) {
            System.err.println(USAGE);
            throw new IllegalArgumentException("Missing catalog name");
        }
        catPath = args[0];
        asString = makeString(args);

        if (args.length > 1) {
            scanForFlags(args);
        }
    }

    private String makeString(String[] args) {
        StringBuilder sb = new StringBuilder(args[0]);
        for (int i = 1; i < args.length; i++) {
            sb.append(" ").append(args[i]);
        }
        return sb.toString();
    }

    private void scanForFlags(String[] args) {
        for (int i = 1; i < args.length; i++) {
            if (DUMP_ANALYSIS_FLAG.equals(args[i])) {
                dumpAnalysis = true;
            }
        }
    }

    @Override
    public String toString() {
        return "ProgArgs{ " + asString + " }";
    }

    /**
     * Returns the catalog path (first argument).
     *
     * @return the catalog path
     */
    public String catPath() {
        return catPath;
    }

    /**
     * Returns true if the dump analysis flag was set.
     *
     * @return true if dump analysis flag set
     */
    public boolean dumpAnalysis() {
        return dumpAnalysis;
    }
}
