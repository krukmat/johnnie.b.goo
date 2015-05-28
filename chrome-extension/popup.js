// Copyright (c) 2011 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

var QUERY_URL = 'http://jbg.dev:8088/query/';
var INGEST_URL = 'http://jbg.dev:8088/ingest/';
var BULK_UPLOAD_URL = 'http://jbg.dev:8088/bulk_process/';
var APIs = [];
chrome.storage.sync.get({
    Api: 'http://www.songsterr.com/a/wa/search?pattern='
  }, function(items) {
    for (item in items.Api){
        APIs.push(items.Api[item]);
    }
  });

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
          for (var api in APIs)
              chrome.tabs.create({url:APIs[api]+object.metadata.artist+'+'+object.metadata.track});
      }
    });
}

function bulk_upload() {
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
    formData.append('list_file', myFile);

	// Let's upload the complete file object
	makeRequest(BULK_UPLOAD_URL, formData, function(data) {
      // Render the results.
      object = JSON.parse(data)
      if (object.error !== undefined)
          $('#response').text(object.error);
      else{
          $('#response').text('OK');
      }
    });
}

function ingest() {
	// Retrieve the FileList object from the referenced element ID
    $('body').css('height', '500px');

	bootbox.dialog({
      title: "Ingest",
      message: '<form action="http://jbg.dev:8088/ingest/" method="post" enctype="multipart/form-data" name="form" id="form">\
    <dt><label>Select a File to Upload</label></dt><dl><input id="upload" type="file" name="upload" /></dl>\
    <dt><label>Artist</label></dt><dl><input id="artist" type="text" name="artist" /></dl>\
    <dt><label>Release</label></dt><dl><input id="release" type="text" name="release" /></dl>\
    <dt><label>Track</label></dt><dl><input id="track" type="text" name="track" /></dl>\
</form>',
    buttons: {
        danger: {
          label: "Update",
          className: "btn-danger",
          callback: function() {
            var myFileList = $('#upload')[0];
            var myFileList = myFileList.files;
            var myFile = myFileList[0];
            // Set some variables containing the three attributes of the file
            var myFileName = myFile.name;
            var myFileSize = myFile.size;
            var myFileType = myFile.type;
            var FilenameConvention = myFileName.split('-');
            var ArtistName =  $.trim(FilenameConvention[0]);
            var ArtistTrack = $.trim(FilenameConvention[1]).replace('.mp3', '');

            // Alert the information we just gathered
            console.log("FileName: " + myFileName + "- FileSize: " + myFileSize + " - FileType: " + myFileType);
            var $form = new FormData();

            $form.append('mp3', myFile);
            if (ArtistTrack !== undefined)
                $form.append('track', ArtistTrack);
            else
                $form.append('track', $('#track').val());
            if (ArtistName !== undefined)
                $form.append('artist', ArtistName);
            else
                $form.append('artist', $('#artist').val());
            $form.append('release', $('#release').val());
            $form.append('length', myFile.size);
            $form.append('codever', '1');


            // Let's upload the complete file object
            makeRequest(INGEST_URL, $form, function(data) {
              // Render the results.
              object = JSON.parse(data)
              $('body').css('height', '');
              if (object.error !== undefined)
                  $('#response').text(object.error);
              else
                  $('#response').text('Track_id:'+object.track_id);
            });
          }
        },
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

document.getElementById('check').addEventListener("click",function(iVal){
      query();
});

document.getElementById('bulk_upload').addEventListener("click",function(iVal){
      bulk_upload();
});

document.getElementById('ingest').addEventListener("click",function(iVal){
      ingest();
});