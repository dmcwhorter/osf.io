var $osf = require('osfHelpers');
var bootbox = require('bootbox');
var $ = require('jquery');

(function() {

    function newBasePath() {
        var isValidBasePath = /^(?!.*(\.\.|-\.))[^.][a-z0-9\d.-]{2,61}[^.]$/;
        var $elm = $('#addonSettingsHdfs');
        var $select = $elm.find('select');

        bootbox.prompt('Select base HDFS path to use', function(basePathName) {

            if (!basePathName) {
                return;
            } else if (isValidBasePath.exec(basePathName) == null) {
                bootbox.confirm({
                    title: 'Invalid base path',
                    message: "Sorry, that's not a valid path. Try another?",
                    callback: function(result) {
                        if(result) {
                            newBasePath();
                        }
                    }
                });
            } else {
                $osf.postJSON(
                    nodeApiUrl + 'hdfs/newbasepath/',
                    {basePath_name: basePathName}
                ).done(function() {
                    $select.append('<option value="' + basePathName + '">' + basePathName + '</option>');
                    $select.val(basePathName);
                }).fail(function(xhr) {
                    var message = JSON.parse(xhr.responseText).message;
                    bootbox.confirm({
                        title: 'Error setting up base path',
                        message: message + "\nTry again?",
                        callback: function(result) {
                            if(result) {
                                newBasePath();
                            }
                        }
                    });
                });
            }
        });
    }

    var removeNodeAuth = function() {
        $.ajax({
            type: 'DELETE',
            url: nodeApiUrl + 'hdfs/settings/',
            contentType: 'application/json',
            dataType: 'json'
        }).done(function() {
            window.location.reload();
        }).fail(
            $osf.handleJSONError
        );
    };

    function importNodeAuth() {
        $osf.postJSON(
            nodeApiUrl + 'hdfs/import-auth/',
            {}
        ).done(function() {
            window.location.reload();
        }).fail(
            $osf.handleJSONError
        );
    }

    $(document).ready(function() {

        $('#newBasePath').on('click', function() {
            newBasePath();
        });

        $('#hdfsRemoveToken').on('click', function() {
            bootbox.confirm({
                title: 'Deauthorize Hdfs?',
                message: 'Are you sure you want to remove this Hdfs authorization?',
                callback: function(confirm) {
                    if(confirm) {
                        removeNodeAuth();
                    }
                }
            });
        });

        $('#hdfsImportToken').on('click', function() {
            importNodeAuth();
        });

        $('#addonSettingsHdfs .addon-settings-submit').on('click', function() {
            var $basePath = $('#hdfs_basePath');
            if ($basePath.length && !$basePath.val()) {
                return false;
            }
        });

    });

})();
