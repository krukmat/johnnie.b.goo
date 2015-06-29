// Copyright (c) 2011 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

var QUERY_URL = 'http://jbg.dev:8080/roulette_track/';
var APIs = [];


function onPlay(event) {
 var player = this;
 timeout = setInterval(function () {
   console.log(player.p.getCurrentTime());
 }, 500);
}

function onPause(event) {
  clearInterval(timeout);
}


function query() {
    var formData = new FormData();

	// Let's upload the complete file object
	makeRequest(QUERY_URL, formData, function(data) {
      // Render the results.
      object = JSON.parse(data)
      if (object.error !== undefined)
          $('#response').text(object.error);
      else{
          $('#response').text(data);
          var id_list = [];
          for (var i in object){
            id_list.push(object[i].youtube_code);
          }
          $('#player').player({
              video: id_list[0],
              events: {
                play: onPlay,
                pause: onPause,
                end: onPause
              }
          });
          $('#playlist').tube({
            player: 'player-container',
            list: [id_list]
          });
      }
    });
}

function makeRequest(URL, formData, callback) {
  var xhr = new XMLHttpRequest();
  xhr.open('POST', URL);
  // Append our file to the formData object
  // Notice the first argument "file" and keep it in mind
  xhr.addEventListener('load', function(e) {
    var result = xhr.responseText;
    callback(result);
  });
  xhr.send(formData);
}

document.getElementById('roulette').addEventListener("click",function(iVal){
      query();
});