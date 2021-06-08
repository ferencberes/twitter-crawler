const vis = require('vis')

var nodes = new vis.DataSet([
  { id: 1, label: "Node 1" },
  { id: 2, label: "Node 2" },
  { id: 3, label: "Node 3" },
  { id: 4, label: "Node 4" },
]);

// create an array with edges
var edges = new vis.DataSet([
  { from: 1, to: 3 },
  { from: 1, to: 2 },
  { from: 2, to: 4 },
]);

// create a network

var container = document.getElementById("mynetwork");
var data = {
  nodes: nodes,
  edges: edges,
};
var options = {};
var network = new vis.Network(container, data, options);

/*
const { Kafka } = require('kafkajs')

const kafka = new Kafka({
  clientId: 'dynamic_network_visualization',
  brokers: ['localhost:9092']
})

const consumer = kafka.consumer({ groupId: 'test-group' })
//await consumer.connect()
consumer.connect()
//await consumer.subscribe({ topic: 'sample', fromBeginning: true })
consumer.subscribe({ topic: 'sample', fromBeginning: true })
//await 
consumer.run({
  eachMessage: async ({ topic, partition, message }) => {
    var msg = message.value.toString()
    var splitted = msg.split(",")
    if (splitted.length > 1) {
       var resp = "edge"
    } else {
       var resp = "node"
    }
    console.log({
      response: resp,
    })
  },
})
*/
