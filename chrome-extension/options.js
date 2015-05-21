// Saves options to chrome.storage
function save_options() {
  var api = $('#api').val();
  chrome.storage.sync.set({
    Api: api
  }, function() {
    // Update status to let user know options were saved.
    var status = document.getElementById('status');
    status.textContent = 'Options saved.';
    setTimeout(function() {
      status.textContent = '';
    }, 750);
  });
}

// Restores select box and checkbox state using the preferences
// stored in chrome.storage.
function restore_options() {
  // Use default value color = 'red' and likesColor = true.
  var values = [];
  chrome.storage.sync.get({
    Api: 'http://www.songsterr.com/a/wa/search?pattern='
  }, function(items) {
    for (item in items.Api){
        values.push(items.Api[item]);
    }
    $('#api').val(values);
    $('#api').multiselect();
  });
}
document.addEventListener('DOMContentLoaded', restore_options);
document.getElementById('save').addEventListener('click',
    save_options);