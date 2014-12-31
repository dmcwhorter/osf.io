# Hadoop HDFS Storage Add-on for OSF

## Status as of 12/31/2014
* Some basic functionality is working including creating the base directory in HDFS from the Settings page
* Many things are untested and not working

## Setting up an HDFS environment for testing
* Install Docker
* `[sudo] docker pull sequenceiq/hadoop-docker:2.5.2`
* `[sudo] docker run -i -p 9000:9000 -p 50070:50070 -t sequenceiq/hadoop-docker:2.5.2 /etc/bootstrap.sh -bash`
* This will start up a basic Hadoop 2.5.2 instance and expose 2 ports
    * Go to [http://localhost:50070](http://localhost:50070) to see the HDFS status and information pages
    * HDFS RPC calls go to host `localhost`, port `9000`
* For testing, then you can use these connection parameters:
    * HDFS Name Node Host: `localhost`
    * HDFS Name Node Port: `9000`
    * Hadoop Protocol Version: `9`
    * Use Trash: `False` or `True`
    * HDFS Username: `root`
    * Base Path: `/user/root/osf_test` or any location