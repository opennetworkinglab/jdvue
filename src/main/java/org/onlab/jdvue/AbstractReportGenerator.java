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

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;

/**
 * Base class for generating text-based reports.
 */
public abstract class AbstractReportGenerator {

    /**
     * Slurps the specified input stream into a string.
     *
     * @param stream input stream to be read
     * @return string containing the contents of the input stream
     * @throws IOException if issues encountered reading from the stream
     */
    protected String slurp(InputStream stream) throws IOException {
        StringBuilder sb = new StringBuilder();
        BufferedReader br = new BufferedReader(new InputStreamReader(stream));
        String line;
        while ((line = br.readLine()) != null) {
            sb.append(line).append(System.lineSeparator());
        }
        br.close();
        return sb.toString();
    }

    /**
     * Uses the given string as the name of the resource to slurp in.
     *
     * @param resourceName name of the resource to read
     * @return string containing the contents of the specified resource
     * @throws IOException if issues encountered reading from the resource
     */
    protected String getResourceAsString(String resourceName) throws IOException {
        return slurp(getClass().getResourceAsStream(resourceName));
    }

}
