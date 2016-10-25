import moment from  'moment'
import axios from 'axios'
import vis from 'vis'



axios.get('plot/Annihilator.json')
  .then(data => {
    let ds = new vis.DataSet({})
    console.log(data)
    let md = data.data
    let mp = []
    let c = 0
    md.member_points.forEach(m => {
      // members.add(m.member)
      console.log(m.member,moment(m.t,'YYYYMDDHHmmss').format(),moment(m.f,'YYYYMDDHHmmss').format())
      mp.push({
        start: moment(m.t,'YYYYMDDHHmmss'),
        end: moment(m.f,'YYYYMDDHHmmss'),
        content: m.member
      })

    })
    console.log(mp)
    ds.add(mp)
    //
    const plotElem = new vis.Timeline(document.getElementById('chart'), ds, {})
  })
  .catch(err => {
    console.log(err)
  })
// import * as d3 from 'd3'
// import mg from 'metrics-graphics'
// // const d3 = require('d3')
// // const nv = require('nvd3')
//
// console.log('test')
// var chart
// d3.json('plot/Accept.json', data => {
//   console.log(data)
//   let mp = []
//   let members = new Set()
//   data.member_points.forEach(m => {
//     // members.add(m.member)
//     // console.log(moment(m.f,'YYYYMMDDHHMMSS').year(),moment(m.t,'YYYYMMDDHHMMSS').year())
//
//     mp.push({
//       date: moment(m.t,'YYYYMMDDHHMMSS').toDate(),
//       value: m.member
//     })
//
//     mp.push({
//       date: moment(m.f,'YYYYMMDDHHMMSS').toDate(),
//       value: m.member
//     })
//
//
//   })
//
//   // let y = d3.scaleOrdinal()
//   //   .range([0, window.innerHeight])
//   //   .domain(Array.from(members.values()))
//   //
//   // //2016 10 25 05 10 84
//   //
//   // mp = mg.convert.date(mp,'date','%Y-%m-%d')
//   // console.log(mp)
//   //
//   mg.data_graphic({
//     title: "Accept",
//     data: mp,
//     left: 200,
//     full_width: true,
//     height: 500,
//     missing_is_hidden: true,
//     target: '#chart',
//     x_accessor: 'date',
//     y_accessor: 'value',
//   })
//   // let md = {
//   //   "key": "mementos",
//   //   "values": []
//   // }
//   // let plotd = []
//   // data.mementos.forEach(m => {
//   //   console.log(m)
//   //   md.values.push({
//   //     label: 'memento',
//   //     value: m.datetime
//   //   })
//   // })
//   // console.log()
//   // nv.addGraph(() => {
//   //   // chart = nv.models.multiBarHorizontalChart()
//   //   //   .x(d => d.label)
//   //   //   .y(d => d.value)
//   //   //   .
//   // })
// })