var socket = io.connect('http://localhost:3000');

socket.on('try existing tab', function(data, callback) {

  var target_url = data.url

  chrome.tabs.query({}, function(tabs) {
    for (var i = 0; i < tabs.length; i++) {
      var current_tab_url = tabs[i].url;
      var current_tab_id  = tabs[i].id;

      if (current_tab_url.includes(target_url)) {
        chrome.tabs.update(current_tab_id, {selected: true})
        data.create_new_tab = false;
      }
    }

    callback(data);

  })
})
