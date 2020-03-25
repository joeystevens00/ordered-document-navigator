var getJSON = function(url, callback) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.responseType = 'json';
    xhr.onload = function() {
      var status = xhr.status;
      if (status === 200) {
        callback(null, xhr.response);
      } else {
        callback(status, xhr.response);
      }
    };
    xhr.send();
};
function is_numeric(str){
    return /^\d+$/.test(str);
}
var build_url_relative = function(path) {
    var current_folder_id = window.location.pathname.split('/')[2];
    // if using the folder name, continue to use it
    if (!is_numeric(current_folder_id)) {
      path = path.replace('/folder/' + {{folder_id}}, '/folder/' + current_folder_id);
    }
    return window.location.protocol + "//" + window.location.host + path + '#' + window.location.hash.substr(1);
}
var getFile = function(folder_id, file_id, callback) {
    var url = build_url_relative("/folder/" + folder_id + "/file/" + file_id);
    console.log("GET " + url);
    getJSON(url, callback);
};
