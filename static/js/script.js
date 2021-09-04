'use strict'
Vue.component('app-header',{
    template: '#header',
    props : ['link1','link2','link3','link4','logo'],
    delimiters: ['[[', ']]']
  })


  var app =  new Vue({
     el: '#appRoot',
     data : {
       appTitle: 'つぶやき書店',
       appLink1: 'TOP(つぶやき書店とは）',
       appLink2:'使い方',
       appLink3: '書店を利用する',
       appLink4: 'Github'
     },
     delimiters: ['[[', ']]']
   })
