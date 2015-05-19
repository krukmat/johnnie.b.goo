// Copyright (c) 2011 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

var QUERY_URL = 'http://jbg.dev:8088/query/';
var INGEST_URL = 'http://jbg.dev:8088/ingest/';

//TODO: Commit should have all metadata parameters
//TODO: Query: More metadata. Popup always visible??

function query() {
	// Retrieve the FileList object from the referenced element ID
	var myFileList = document.getElementById('mp3').files;

	// Grab the first File Object from the FileList
	var myFile = myFileList[0];

	// Set some variables containing the three attributes of the file
	var myFileName = myFile.name;
	var myFileSize = myFile.size;
	var myFileType = myFile.type;

	// Alert the information we just gathered
	console.log("FileName: " + myFileName + "- FileSize: " + myFileSize + " - FileType: " + myFileType);

    var formData = new FormData();
    formData.append('mp3', myFile);

	// Let's upload the complete file object
	makeRequest(QUERY_URL, formData, function(data) {
      // Render the results.
      object = JSON.parse(data)
      if (object.error !== undefined)
          $('#response').text(object.error);
      else{
          $('#response').text('Track_id:'+object.metadata.track_id);
          console.log(object.metadata);
          chrome.tabs.create({url:'http://www.songsterr.com/a/wa/search?pattern='+object.metadata.artist+'+'+object.metadata.track});
      }
    });
}

function ingest() {
	// Retrieve the FileList object from the referenced element ID
	var myFileList = document.getElementById('mp3').files;

	// Grab the first File Object from the FileList
	var myFile = myFileList[0];

	// Set some variables containing the three attributes of the file
	var myFileName = myFile.name;
	var myFileSize = myFile.size;
	var myFileType = myFile.type;

	// Alert the information we just gathered
	console.log("FileName: " + myFileName + "- FileSize: " + myFileSize + " - FileType: " + myFileType);
	var $form = new FormData();

	$form.append('mp3', myFile);
	$form.append('track', $('#track').val());
	$form.append('artist', $('#artist').val());
	$form.append('release', $('#release').val());
	$form.append('length', myFile.size);
	$form.append('codever', '1');


	// Let's upload the complete file object
	makeRequest(INGEST_URL, $form, function(data) {
      // Render the results.
      object = JSON.parse(data)
      if (object.error !== undefined)
          $('#response').text(object.error);
      else
          $('#response').text('Track_id:'+object.track_id);
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

document.getElementById('check').addEventListener("click",function(iVal){
      query();
});

document.getElementById('ingest').addEventListener("click",function(iVal){
      ingest();
});