/**
 * Angular module responsible for sharing the code using the url via email;
 * Displays the list of themes, keymaps and modes for the app's settings.
 *
 */
var codeShareApp = angular.module('codeShareApp', []);

codeShareApp.service('CodeRest', function ($http) {
    return {
        compose: function (params) {
            return $http.get('/api/code_share/compose', {params: params});
        }
    }

});

codeShareApp.controller('SettingsController', function ($scope, $http, CodeRest, $location) {
    $scope.params = {}; // model
    $scope.params['url'] = $location.absUrl(); //$location.path(); // get current url
    $scope.paramsList = {}; // list
    $scope.params['csrf_token'] = $("input[name=csrf_token]").val();
    //alert($scope.params['csrf_token']);
    $scope.compose = function () {
        CodeRest.compose($scope.params)
            .success(function (data, status, headers, config) {
                if (status == 200) {
                    $scope.response = "Successfully shared codex!";
                } else if (status == 403) {
                    $scope.response = "Invalid email!";
                }
            }).error(function (data, status, headers, config) {
                $scope.response = "Codex sharing failed!";
            });
    }

    // Preload themes
    $scope.themes = [
        {name: "3024-day", src: "//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/theme/3024-day.min.css"},
        {name: "3024-night", src: "//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/theme/3024-night.min.css"},
        {name: "ambiance-mobile", src: "//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/theme/ambiance-mobile.min.css"},
        {name: "ambiance", src: "//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/theme/ambiance.min.css"},
        {name: "base16-dark", src: "//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/theme/base16-dark.min.css"},
        {name: "base16-light", src: "//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/theme/base16-light.min.css"},
        {name: "blackboard", src: "//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/theme/blackboard.min.css"},
        {name: "cobalt", src: "//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/theme/cobalt.min.css"},
        {name: "eclipse", src: "//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/theme/eclipse.min.css"},
        {name: "elegant", src: "//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/theme/elegant.min.css"},
        {name: "erlang-dark", src: "//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/theme/erlang-dark.min.css"},
        {name: "lesser-dark", src: "//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/theme/lesser-dark.min.css"},
        {name: "mbo", src: "//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/theme/mbo.min.css"},
        {name: "mdn-like", src: "//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/theme/mdn-like.min.css"},
        {name: "midnight", src: "//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/theme/midnight.min.css"},
        {name: "monokai", src: "//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/theme/monokai.min.css"},
        {name: "neat", src: "//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/theme/neat.min.css"},
        {name: "neo", src: "//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/theme/neo.min.css"},
        {name: "night", src: "//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/theme/night.min.css"},
        {name: "paraiso-dark", src: "//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/theme/paraiso-dark.min.css"},
        {name: "paraiso-light", src: "//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/theme/paraiso-light.min.css"},
        {name: "pastel-on-dark", src: "//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/theme/pastel-on-dark.min.css"},
        {name: "rubyblue", src: "//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/theme/rubyblue.min.css"},
        {name: "solarized", src: "//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/theme/solarized.min.css"},
        {name: "the-matrix", src: "//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/theme/the-matrix.min.css"},
        {name: "tomorrow-night-eighties", src: "//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/theme/tomorrow-night-eighties.min.css"},
        {name: "twilight", src: "//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/theme/twilight.min.css"},
        {name: "vibrant-ink", src: "//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/theme/vibrant-ink.min.css"},
        {name: "xq-dark", src: "//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/theme/xq-dark.min.css"},
        {name: "xq-light", src: "//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/theme/xq-light.min.css"}
    ];

    $scope.theme_selected = $scope.themes[0];

    // Preload modes
    $scope.modes = [
        {name: 'Python', src: "text/x-python,//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/mode/python/python.min.js"},
        {name: 'Javascript', src: "application/javascript,https://cdnjs.cloudflare.com/ajax/libs/codemirror/4.5.0/mode/javascript/javascript.js"},
        {name: 'YAML', src: "text/x-yaml,//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/mode/yaml/yaml.min.js"},
        {name: 'CSS', src: "text/css,//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/mode/css/css.min.js"},
        {name: 'HTML', src:"text/html,//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/mode/htmlmixed/htmlmixed.min.js"}
    ];

    $scope.default_mode = $scope.modes[0];

    // Preload keymaps
    $scope.keymaps = [
        {name: "sublime", src: "//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/keymap/sublime.min.js"},
        {name: "emacs", src: "//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/keymap/emacs.min.js"},
        {name: "vim", src: "//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/keymap/vim.min.js"}
    ];

    $scope.default_keymap = $scope.keymaps[0];


    // Change mode, keymaps, themes using ng-click
    $scope.changeTheme = function () {
        // load the source file
        checkloadjscssfile($scope.theme_selected['src'], "css");
        codeMirror.setOption("theme", $scope.theme_selected['name']);
    }

    $scope.changeMode = function () {
        var hash = window.location.hash.replace(/#/g, ''),
            value_n_src,
            value,
            src,
            connect;
        value_n_src = new String($scope.default_mode['src']).split(",");
        value = value_n_src[0];
        src = value_n_src[1];

        // connect to firebase
        connect = new Firebase('https://codex-for-all.firebaseio.com' + hash);
        userRef = connect.child("settings");
        userRef.set({
            value: value,
            src: src
        });

        // load the source file
        checkloadjscssfile(src, "js");
        codeMirror.setOption("mode", value);
    }

    $scope.changeKey = function () {
        checkloadjscssfile($scope.default_keymap['src'], "js");
        codeMirror.setOption("keyMap", $scope.default_keymap['name']);
    }
});


// init themes, mode and keymap
loadCSSJSFile("//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/theme/3024-day.min.css", "css");
codeMirror.setOption("theme", "3024-day");

// init mode
loadCSSJSFile("//cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/mode/python/python.min.js", "js");
codeMirror.setOption("mode", "python");

// For Tooltips
$(function () {
  $('[data-toggle="tooltip"]').tooltip();
    $('#pop_hover').popover('toggle');
    $('#pop_hover').click();

});

function toggleWrapping(x) {
    if(x.checked) {
        codeMirror.setOption("lineWrapping", true);
    }
    else {
        codeMirror.setOption("lineWrapping", false);
    }
}