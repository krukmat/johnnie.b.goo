// Copyright (c) 2011 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

var QUERY_URL = 'http://jbg.dev:8088/query/';

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

	// Let's upload the complete file object
	makeRequest(QUERY_URL, myFile, function(data) {
      // Render the results.
      object = JSON.parse(data)
      if (object.error !== undefined)
          $('#response').text(object.error);
      else
          $('#response').text('Track_id:'+object.metadata.track_id);
    });
}


function makeRequest(URL, myFileObject, callback) {
  var xhr = new XMLHttpRequest();
  xhr.open('POST', URL);
  var formData = new FormData();
  // Append our file to the formData object
  // Notice the first argument "file" and keep it in mind
  formData.append('mp3', myFileObject);

  xhr.addEventListener('load', function(e) {
    var result = xhr.responseText;
    callback(result);
  });
  xhr.send(formData);
}

document.getElementById('check').addEventListener("click",function(iVal){
      query();
});