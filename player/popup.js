// Copyright (c) 2011 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

var QUERY_URL = 'http://jbg.dev:8080/roulette_track/';
var APIs = [];
var done = false;
var index = 0;
var id_list = [];
var player;

function onPlayerReady(event) {
    event.target.loadPlaylist(id_list);
}

function onPlayerStateChange(event) {
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
          // $('#response').text(data);
          for (var i in object){
            id_list.push(object[i].youtube_code);
          }
          var player;
          var tag = document.createElement('script');
          tag.src = "https://www.youtube.com/player_api";
          var firstScriptTag = document.getElementsByTagName('script')[0];
          firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
          window.onYouTubePlayerAPIReady = function() {
              done = false;
              player = new YT.Player('player', {
                  height: '300',
                  width: '300',
                  loadPlaylist:{
                    listType:'playlist',
                    list: id_list,
                    index:parseInt(0),
                    suggestedQuality:'small'
                 },
                  events: {
                    'onReady': onPlayerReady,
                    'onStateChange': onPlayerStateChange
                  }
              });
          }
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
