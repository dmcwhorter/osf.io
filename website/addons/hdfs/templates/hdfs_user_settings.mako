<form role="form" id="addonSettings${addon_short_name.capitalize()}" data-addon="${addon_short_name}">

    <span data-owner="user"></span>

    <div>
        <h4 class="addon-title">
            Hadoop HDFS

            <small class="authorized-by">
                % if has_auth:
                    authorized
                    <a id="hdfsRemoveAccess" class="text-danger pull-right addon-auth">Delete Credentials</a>
                % endif
            </small>

        </h4>
    </div>

    % if not has_auth:
        <div class="form-group">
            <label for="hdfsAddon">Name Node Host</label>
            <input class="form-control" id="host" name="host" ${'disabled' if disabled else ''} />
        </div>
        <div class="form-group">
            <label for="hdfsAddon">Name Node Port</label>
            <input class="form-control" id="port" name="port" ${'disabled' if disabled else ''} />
        </div>
        <div class="form-group">
            <label for="hdfsAddon">Hadoop RPC Protocol Version</label>
            <input class="form-control" id="protocol_version" name="protocol_version" ${'disabled' if disabled else ''} />
        </div>
        <div class="form-group">
            <label for="hdfsAddon">Use Trash?</label>
            <input class="form-control" id="use_trash" name="use_trash" ${'disabled' if disabled else ''} />
        </div>
        <div class="form-group">
            <label for="hdfsAddon">HDFS Username</label>
            <input class="form-control" id="effective_user" name="effective_user" ${'disabled' if disabled else ''} />
        </div>
        <div class="form-group">
            <label for="hdfsAddon">Base Path</label>
            <input class="form-control" id="base_path" name="base_path" ${'disabled' if disabled else ''} />
        </div>

        <button class="btn btn-success addon-settings-submit">
            Submit
        </button>
    % endif

    ${self.on_submit()}

    <!-- Form feedback -->
    <div class="addon-settings-message" style="display: none; padding-top: 10px;"></div>

</form>

<%def name="on_submit()">
    <script type="text/javascript">
        window.contextVars = $.extend({}, window.contextVars, {'addonSettingsSelector': '#addonSettings${addon_short_name.capitalize()}'});
    </script>
</%def>

<%include file="profile/addon_permissions.mako" />
