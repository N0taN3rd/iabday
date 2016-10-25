const moment = require('moment')
const d3 = require('d3')
const nv = require('nvd3')

console.log('test')
var chart
d3.json('plot/Accept.json', data => {
  console.log(data)
  let md = {
    "key": "mementos",
    "values": []
  }
  let plotd = []
  data.mementos.forEach(m => {
    console.log(m)
    md.values.push({
      label: 'memento',
      value: m.datetime
    })
  })
  console.log()
  // nv.addGraph(() => {
  //   // chart = nv.models.multiBarHorizontalChart()
  //   //   .x(d => d.label)
  //   //   .y(d => d.value)
  //   //   .
  // })
})