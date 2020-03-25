function checkKey(e) {
    e = e || window.event;

    if (e.keyCode == '37') {
        getFile({{folder_id}}, {{file_id}}, function (err, file) {
            if (err != null) {
                console.log('error: ' + err);
            }
            console.log(file);
            if (file.last && file.last.content_path) {
                window.location.href = build_url_relative(file.last.content_path);
            }
        });
       // left arrow
    }
    else if (e.keyCode == '39') {
       // right arrow
        getFile({{folder_id}}, {{file_id}}, function (err, file) {
            if (err != null) {
                console.log('error: ' + err);
            }
            console.log(file);
            if (file.next && file.next.content_path) {
                window.location.href = build_url_relative(file.next.content_path);
            }
        });
    }

}
$(document).ready(function() {
    console.log('Folder {folder_id} and File {file_id}');
    document.onkeydown = checkKey;
});
