$(".dropdown-toggle").click(function(e) {
    e.stopPropagation();
    $(".dropdown").slideToggle( "slow", function() {
        // Animation complete.
    });
});

$('.dropdown').click(function(e) {
    e.stopPropagation();
});

$(document).click(function() {
     $('.dropdown').slideUp("slow", function() {});
});

// Initialize default values of theme, keymap and mode in settings
var codeMirror = CodeMirror(document.getElementById('firepad-container'), {
    lineNumbers: true,
    theme : '3024-day',
    keyMap: 'sublime',
    mode: 'python',
    crudeMeasuringFrom: 100
});

// Initialize Firepad
function init(theme) {
    var firepadRef = getRef();
    var firepad = Firepad.fromCodeMirror(firepadRef, codeMirror, {
        defaultText: ""
    });

    firepad.on('ready', function() {
    	// Firepad is ready
    	$("#preload").hide();
    	firepadRef.update({ startedAt: Firebase.ServerValue.TIMESTAMP });
        firepadRef.onDisconnect().update({ updatedAt: Firebase.ServerValue.TIMESTAMP });
    });
}

// Configuration for limit sizing in Codemirror
codeMirror.enforceMaxLength = function(cm, change) {
    var maxLength = cm.getOption("maxLength");
    if (maxLength && change.update) {
        var str = change.text.join("\n");
        var delta = str.length-(cm.indexFromPos(change.to) - cm.indexFromPos(change.from));
        if (delta <= 0) { return true; }
        delta = cm.getValue().length+delta-maxLength;
        if (delta > 0) {
            str = str.substr(0, str.length-delta);
            change.update(change.from, change.to, str.split("\n"));
        }
    }
    return true;
}

// Codemirror instance for size limiting
codeMirror.setOption("maxLength", 2000);
codeMirror.on("beforeChange", codeMirror.enforceMaxLength);


// Helper to get hash from end of URL or generate a random one.
function getRef() {
    var ref = new Firebase('https://codex-for-all.firebaseio.com');
    var hash = window.location.hash.replace(/#/g, '');

    if (hash) {
        ref = ref.child(hash);
    } else {
        ref = ref.push(); // generate unique location.
        window.location = window.location + '#' + ref.key(); // add it as a hash to the URL.
    }
    if (typeof console !== 'undefined')
        console.log('Firebase data: ', ref.toString());
    return ref;
}

function test() {
    var data;
    var connect = new Firebase('https://codex-for-all.firebaseio.com/-JdD-7o8NByCR6_LVrsb/updatedAt');
    //var key = connect.key();
    //key = connect.child("-JdD-7o8NByCR6_LVrsb").key();
    connect.on("value", function(snapshot) {
	data = snapshot.val();

    });
    alert(data);
}

// Applies changed mode to other collaborators as well
function firebasemode() {
    var hash = window.location.hash.replace(/#/g, '');
    var connect = new Firebase('https://codex-for-all.firebaseio.com' + hash + '/settings');
    
    connect.on("value", function(snapshot) {
	var changedPost = snapshot.val();
	// console.log("src:" + changedPost.src);
	// console.log("value:" + changedPost.value);
	// var c = changedPost;
	checkloadjscssfile(changedPost.src, "js");
	codeMirror.setOption("mode", changedPost.value);
	$("#id_modeselect").val(changedPost.value+","+changedPost.src);
    });

}

// Fire initialization of Firepad
init('default');
firebasemode();
