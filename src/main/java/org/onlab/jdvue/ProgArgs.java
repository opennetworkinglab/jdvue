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

/**
 * Encapsulates the command line arguments for the Dependency Viewer.
 */
public class ProgArgs {
    private static final String USAGE = "Expected Args: <catalog path> [-d]";
    private static final String DETAIL_DATA_FLAG = "-d";

    private final String catPath;
    private final String asString;

    private boolean outputDetailData = false;

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
            if (DETAIL_DATA_FLAG.equals(args[i])) {
                outputDetailData = true;
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
     * Returns true if the detail data flag was set.
     *
     * @return true if dump analysis flag set
     */
    public boolean outputDetailData() {
        return outputDetailData;
    }
}
