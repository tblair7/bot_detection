Bot detection for Old School Runescape

Author: [Tyler Blair](https://www.github.com/tblair7)

----

Old School Runescape is plagued by bots that affect many aspects of the game and the current in-game bot detection is lacking. Here, I develop a way to flag potential bots by means of tracking user activity. 

Requires [pyspark-cassandra](https://github.com/anguenot/pyspark-cassandra):  
`git clone https://github.com/anguenot/pyspark-cassandra.git`

pyspark-cassandra needs to be compiled with [sbt](https://www.scala-sbt.org/release/docs/Setup.html). On Macs:  
`brew install sbt@1
sbt compile`

Additional details can be found [here](https://medium.com/@amirziai/running-pyspark-with-cassandra-in-jupyter-2bf5e95c319). 
