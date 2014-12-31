
<form role="form" id="addonSettings${addon_short_name.capitalize()}" data-addon="${addon_short_name}">

    <div>
        <h4 class="addon-title">
            Hadoop HDFS
        </h4>
    </div>


    % if not user_has_auth:

        <div class="form-group">
            <label for="hdfsAddon">Name Node Host</label>
            <input class="form-control" id="host" name="host"/>
        </div>
        <div class="form-group">
            <label for="hdfsAddon">Name Node Port</label>
            <input class="form-control" id="port" name="port"/>
        </div>
        <div class="form-group">
            <label for="hdfsAddon">Hadoop RPC Protocol Version</label>
            <input class="form-control" id="protocol_version" name="protocol_version"/>
        </div>
        <div class="form-group">
            <label for="hdfsAddon">Use Trash?</label>
            <input class="form-control" id="use_trash" name="use_trash"/>
        </div>
        <div class="form-group">
            <label for="hdfsAddon">HDFS Username</label>
            <input class="form-control" id="effective_user" name="effective_user"/>
        </div>
        <div class="form-group">
            <label for="hdfsAddon">Base Path</label>
            <input class="form-control" id="base_path" name="base_path"/>
        </div>

        <button class="btn btn-success addon-settings-submit">
            Submit
        </button>

    % endif


    % if not node_has_auth:

        <div class="form-group">
            <label for="hdfsAddon">Node Path</label>
            <input class="form-control" id="node_path" name="node_path"/>
        </div>

    % elif node_has_auth and node_path is None:

        <div>
            <span class="text-danger">
                Error loading HDFS node path. Please refresh the page.
            </span>
        </div>

    %endif


    ${self.on_submit()}

    <div class="addon-settings-message" style="display: none; padding-top: 10px;"></div>

</form>

<%def name="on_submit()">
    <% import json %>
    <script type="text/javascript">
        window.contextVars = $.extend(true, {}, window.contextVars,
        {
            'currentUser': {
                'hasAuth': ${json.dumps(user_has_auth)}
            },
            'hdfsSettingsSelector': '#addonSettings${addon_short_name.capitalize()}'

        });
    </script>
</%def>

