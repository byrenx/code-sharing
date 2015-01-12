var filesadded = "" // list of files already added

// Checks the selected settings and will load its file source
function checkloadjscssfile(file_path, file_type) {
    if (filesadded.indexOf("[" + file_path + "]") == -1) {
        loadCSSJSFile(file_path, file_type);
        filesadded += "[" + file_path + "]" // List of files added in the form "[filename1],[filename2],etc"
    }
}


// Dynamically load the file specified by filename
function loadCSSJSFile(filename, filetype) {
    var element_name = "head", // html element which the file will be appended. default to head
        fileref;
    fileref = document.createElement('script');
    if (filetype == "js") { // if filename is a external JavaScript file
        fileref.setAttribute("type", "text/javascript");
        fileref.setAttribute("src", filename);
        element_name = "content";
    } else if (filetype == "css") { // if filename is an external CSS file
        fileref = document.createElement("link");
        fileref.setAttribute("rel", "stylesheet");
        fileref.setAttribute("type", "text/css");
        fileref.setAttribute("href", filename);
    }

    if (typeof fileref != "undefined") {
        document.getElementsByTagName(element_name)[0].appendChild(fileref);
    }
}
